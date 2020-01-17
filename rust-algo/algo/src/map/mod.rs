
use crate::{
    units::*,
    coords::Coords,
    messages::{
        PlayerId,
        FrameData,
        Config,
        frame,
        config::UnitInformation
    },
    bounds::{
        MAP_BOUNDS,
        BOARD_SIZE,
        MapEdge
    },
    grid::Grid,
    pathfinding::{self, StartedAtWall},
    enum_iterator::IntoEnumIterator,
};

use std::{
    sync::Arc,
    rc::Rc,
    cell::RefCell,
    ops::{Index},
};

use serde::Serialize;
use serde_json;

/// Conversion from frame data into a `MapState`.
pub mod parse;

/// Structured representation of the game state.
///
/// Allows the user to read the map state, and stage
/// changes to commit as a move for their turn.
pub struct MapState {
    inner: Rc<RefCell<MapStateInner>>,
    tile_grid: Grid<MapTile>,
}

struct MapStateInner {
    config: Arc<Config>,
    frame: Box<FrameData>,

    walls: Grid<Option<Unit<FirewallUnitType>>>,
    remove: Grid<Option<Unit<RemoveUnitType>>>,
    info: Grid<Vec<Unit<InfoUnitType>>>,

    atlas: Arc<UnitTypeAtlas>,
    build_stack: Vec<SpawnCommand>,
    deploy_stack: Vec<SpawnCommand>,
}

#[derive(Debug, Clone, Serialize)]
struct SpawnCommand(String, i32, i32);

/// Access to a map at specific coordinates.
///
/// This allows the user to read the game state and make
/// moves at that tile. However, that tile may not be
/// actually present on the map. If the tile is not
/// present, operations which attempt to access the map
/// will fail at runtime.
pub enum MapTile {
    None,
    Some(MapTileInner),
}

#[doc(hidden)]
pub struct MapTileInner {
    coords: Coords,
    state: Rc<RefCell<MapStateInner>>,
}

impl Index<Coords> for MapState {
    type Output = MapTile;

    fn index(&self, index: Coords) -> &Self::Output {
        match self.tile_grid.get(index).as_ref() {
            Some(&map_tile) => map_tile,
            None => &MapTile::None,
        }
    }
}

impl MapTile {
    pub fn valid(&self) -> bool {
        match self {
            &MapTile::Some(_) => true,
            &MapTile::None => false,
        }
    }

    /// Filter a `MapTile` to only tiles with valid coordinates.
    pub fn if_valid(&self) -> Option<&Self> {
        if self.valid() {
            Some(self)
        } else {
            None
        }
    }
}

impl MapStateInner {
    /// How much of a specific resource do we currently own.
    fn resource_owned(&self, resource: Resource) -> f32 {
        match resource {
            Resource::Cores => self.frame.p1_stats.cores,
            Resource::Bits => self.frame.p1_stats.bits,
        }
    }

    /// How much does a certain unit type cost to spawn, in its respective resource unit.
    fn cost_of(&self, unit_type: impl Into<SpawnableUnitType>) -> f32 {
        let unit_type: UnitType = unit_type.into().into();
        self.config.unit_information[unit_type as usize].cost().unwrap()
    }

    /// How many of a certain unit type can we afford to spawn.
    fn number_affordable(&self, unit_type: impl Into<SpawnableUnitType>) -> u32 {
        let unit_type: SpawnableUnitType = unit_type.into();
        let cost = self.cost_of(unit_type);
        let wealth = match unit_type {
            SpawnableUnitType::Info(_) => self.frame.p1_stats.bits,
            SpawnableUnitType::Firewall(_) => self.frame.p1_stats.cores,
        };
        (wealth / cost) as u32
    }

    /// Inner frame data.
    fn frame_data(&self) -> Box<FrameData> {
        self.frame.clone()
    }

    /// Inner game config data.
    fn config(&self) -> Arc<Config> {
        Arc::clone(&self.config)
    }

    /// Inner unit type atlas.
    fn atlas(&self) -> Arc<UnitTypeAtlas> {
        Arc::clone(&self.atlas)
    }

    /// Submit the recorded spawn commands to the game engine.
    fn submit(&self) {
        let line = serde_json::to_string(&self.build_stack).unwrap();
        println!("{}", line);
        let line = serde_json::to_string(&self.deploy_stack).unwrap();
        println!("{}", line);
    }
}

impl MapState {
    /// If a ping were spawned at this tile, and it navigated through the map without any walls
    /// changing or the ping dying, what path would it take?
    pub fn pathfind(&self, start: Coords, target: MapEdge) -> Result<Vec<Coords>, StartedAtWall> {
        pathfinding::pathfind(self, &self[start], target)
    }
}

impl MapTileInner {
    /// Get the coordinates of this tile.
    fn coords(c: Coords, _map: &MapStateInner) -> Coords {
        c
    }

    /// Get all info units at tile.
    fn info_units(c: Coords, map: &MapStateInner) -> Vec<Unit<InfoUnitType>> {
        map.info[c].clone()
    }

    /// Get optional wall unit at tile.
    fn wall_unit(c: Coords, map: &MapStateInner) -> Option<Unit<FirewallUnitType>> {
        map.walls[c].clone()
    }

    /// Get optional remove unit at tile.
    fn remove_unit(c: Coords, map: &MapStateInner) -> Option<Unit<RemoveUnitType>> {
        map.remove[c].clone()
    }

    /// Can the given number of a given unit type be spawned at this tile? If not, why?
    fn can_spawn(c: Coords, map: &MapStateInner, unit_type: impl Into<UnitType>, quantity: u32) -> CanSpawn {
        let unit_type = unit_type.into();
        if let Some(not_enough_resources) = {
            unit_type.as_spawnable().and_then(|spawnable| {
                let resource = Resource::which_buys(spawnable);
                let have = map.resource_owned(resource);
                let need = map.cost_of(spawnable) * quantity as f32;
                if need > have {
                    Some(CanSpawn::NotEnoughResources {
                        resource,
                        have,
                        need
                    })
                } else {
                    None
                }
            })
        } {
            not_enough_resources
        } else if unit_type != UnitType::Remove && Self::wall_unit(c, map).is_some() {
            CanSpawn::UnitAlreadyPresent {
                coords: c,
                unit_present: UnitPresent::Wall,
            }
        } else if unit_type.is_firewall() && Self::info_units(c, map).len() > 0 {
            CanSpawn::UnitAlreadyPresent {
                coords: c,
                unit_present: UnitPresent::Info,
            }
        } else if c.y < 0 || c.y >= BOARD_SIZE as i32 / 2 {
            CanSpawn::WrongSideOfMap(c)
        } else if !MAP_BOUNDS.is_in_arena(c) {
            CanSpawn::OutOfBounds(c)
        } else if unit_type.is_info() && !(
            MAP_BOUNDS.is_on_edge[MapEdge::BottomLeft as usize][c.x as usize][c.y as usize] ||
                MAP_BOUNDS.is_on_edge[MapEdge::BottomRight as usize][c.x as usize][c.y as usize]
        ) {
            CanSpawn::NotOnEdge(c)
        } else {
            CanSpawn::Yes
        }
    }

    /// Can a firewall be removed at this tile? If not, why?
    fn can_remove_firewall(c: Coords, map: &MapStateInner) -> CanRemove {
        if !MAP_BOUNDS.is_in_arena(c) {
            CanRemove::OutOfBounds(c)
        } else if c.y >= BOARD_SIZE as i32 / 2 {
            CanRemove::WrongSideOfMap(c)
        } else if Self::info_units(c, map).len() > 0 {
            CanRemove::InfoUnitPresent(c)
        } else if Self::wall_unit(c, map).is_none() {
            CanRemove::NoUnitPresent(c)
        } else {
            CanRemove::Yes
        }
    }

    /// Attempt to spawn a unit on the board.
    fn spawn(c: Coords, map: &mut MapStateInner, unit_type: impl Into<SpawnableUnitType>) -> Result<(), CanSpawn> {
        let coords = c;

        let unit_type = unit_type.into();
        // assert that the move is valid
        match Self::can_spawn(c, map, unit_type, 1) {
            CanSpawn::Yes => (),
            cannot => return Err(cannot)
        };

        // subtract the cost from our wealth
        let resource = Resource::which_buys(unit_type);
        let cost = map.cost_of(unit_type);
        match resource {
            Resource::Cores => map.frame.p1_stats.cores -= cost,
            Resource::Bits => map.frame.p1_stats.bits -= cost,
        };

        match unit_type {
            SpawnableUnitType::Firewall(unit_type) => {
                if let UnitInformation::Wall { stability, .. } = map.atlas.type_info(unit_type.into()) {
                    let unit = Unit {
                        unit_type,
                        stability: *stability,
                        id: None,
                        owner: PlayerId::Player1
                    };
                    map.walls[coords] = Some(unit);
                } else { panic!("A SpawnableUnitType::Firewall isn't a UnitInformation::Wall - is something wrong with the Atlas?") }
            },
            SpawnableUnitType::Info(unit_type) => {
                if let UnitInformation::Data { stability, .. } = map.atlas.type_info(unit_type.into()) {
                    let unit = Unit {
                        unit_type,
                        stability: *stability,
                        id: None,
                        owner: PlayerId::Player1
                    };
                    map.info[coords].push(unit);
                } else { panic!("A SpawnableUnitType::Info isn't a UnitInformation::Data - is something wrong with the Atlas?") }
            }
        }

        // add it to the command stack
        let unit_type: UnitType = unit_type.into();
        let spawn = SpawnCommand::new(unit_type, coords, &*map.atlas);
        if unit_type.is_firewall() || unit_type == UnitType::Remove {
            map.build_stack.push(spawn);
        } else {
            map.deploy_stack.push(spawn);
        }

        // success
        Ok(())
    }

    /// Attempt to spawn a unit at a location, returning whether successful.
    fn try_spawn(c: Coords, map: &mut MapStateInner, unit_type: impl Into<SpawnableUnitType>) -> bool {
        Self::spawn(c, map, unit_type).is_ok()
    }

    /// Attempt to remove a firewall from a location on the board.
    fn remove_firewall(c: Coords, map: &mut MapStateInner) -> Result<(), CanRemove> {
        let coords = c;

        match Self::can_remove_firewall(c, map) {
            CanRemove::Yes => (),
            cannot => return Err(cannot),
        };

        // remove the unit, saving the unit type and asserting that the unit previously existed
        let unit_type = map.walls[coords].take().unwrap().unit_type;

        // add the remove unit
        map.remove[coords] = Some(Unit {
            unit_type: RemoveUnitType,
            stability: 1.0,
            id: None,
            owner: PlayerId::Player1
        });

        // refund the cost
        let resource = Resource::which_buys(unit_type);
        let cost = map.cost_of(unit_type);
        match resource {
            Resource::Cores => map.frame.p1_stats.cores += cost,
            Resource::Bits => map.frame.p1_stats.bits += cost,
        };

        // add it to the command stack
        map.build_stack.push(SpawnCommand::new(
            UnitType::Remove, coords, &*map.atlas));

        // success
        Ok(())
    }

    /// Attempt to remove a firewall from a location on the board, returning whether successful.
    fn try_remove_firewall(c: Coords, map: &mut MapStateInner) -> bool {
        Self::remove_firewall(c, map).is_ok()
    }
}

// ==== helper data types ====

/// Whether a unit can be spawned at a location.
#[derive(Debug, Copy, Clone, PartialEq)]
pub enum CanSpawn {
    Yes,
    OutOfBounds(Coords),
    WrongSideOfMap(Coords),
    NotOnEdge(Coords),
    NotEnoughResources {
        resource: Resource,
        have: f32,
        need: f32,
    },
    UnitAlreadyPresent {
        coords: Coords,
        unit_present: UnitPresent
    }
}

/// Whether a firewall can be removed at a location.
#[derive(Debug, Copy, Clone, PartialEq)]
pub enum CanRemove {
    Yes,
    OutOfBounds(Coords),
    WrongSideOfMap(Coords),
    NoUnitPresent(Coords),
    InfoUnitPresent(Coords),
}

/// Details on a possible unit spawn being blocked by another unit.
#[derive(Debug, Copy, Clone, PartialEq)]
pub enum UnitPresent {
    Wall,
    Info
}

/// A spendable resource that the player has.
#[derive(Debug, Copy, Clone, PartialEq)]
pub enum Resource {
    Cores,
    Bits
}

/// A unit on the map.
///
/// Generic over the set of unit type.
#[derive(Clone, Debug)]
pub struct Unit<T: Into<UnitType>> {
    pub unit_type: T,
    pub stability: f32,
    pub id: Option<String>,
    pub owner: PlayerId,
}

impl<T: Into<UnitType>> Unit<T> {
    /// Turn this Unit<T> into a Unit<UnitType>
    pub fn unspecialize(self) -> Unit<UnitType> {
        Unit {
            unit_type: self.unit_type.into(),
            stability: self.stability,
            id: self.id,
            owner: self.owner
        }
    }
}

impl CanSpawn {
    /// Whether self is CanSpawn::Yes
    pub fn yes(self) -> bool {
        self == CanSpawn::Yes
    }
}

impl CanRemove {
    /// Whether self is CanRemove::Yes
    pub fn yes(self) -> bool {
        self == CanRemove::Yes
    }
}

impl Resource {
    /// Get the resource which spawns a particular unit type.
    pub fn which_buys(unit_type: impl Into<SpawnableUnitType>) -> Self {
        let unit_type: SpawnableUnitType = unit_type.into();
        match unit_type {
            SpawnableUnitType::Info(_) => Resource::Bits,
            SpawnableUnitType::Firewall(_) => Resource::Cores,
        }
    }
}

impl SpawnCommand {
    fn new(unit_type: UnitType, coords: Coords, atlas: &UnitTypeAtlas) -> Self {
        SpawnCommand(
            atlas.type_into_shorthand(unit_type).to_owned(),
            coords.x,
            coords.y
        )
    }
}

// ==== macro boilerplate ====

macro_rules! map_tile_delegate {
    {$(
        $( #[$outer:meta] )*
        fn $name:ident( $($arg:tt)* ) -> $ret:ty;
    )*}=>{
        impl MapTile {
            $( map_tile_delegate!(@method, ( $( #[$outer] )* ), $name, ( $($arg)* ), $ret); )*
        }
    };
    (@method,
        ( $( #[$outer:meta] )* ),
        $name:ident,
        ($c:ident: Coords, $map:ident: &MapStateInner $(, $k:ident : $v:ty )* $(,)? ),
        $ret:ty
     )=>{
        $( #[$outer] )*
        pub fn $name (&self $( , $k : $v)* ) -> $ret {
            match self {
                &MapTile::None => panic!("tile not on map"),
                &MapTile::Some(MapTileInner {
                    coords,
                    ref state,
                }) => {
                    let guard = state.borrow();
                    let ret: $ret = MapTileInner::$name(
                        coords,
                        &*guard,
                        $( $k, )*
                    );
                    ret
                }
            }
        }
    };
    (@method,
        ($( #[$outer:meta] )*),
        $name:ident,
        ($c:ident: Coords, $map:ident: &mut MapStateInner $(, $k:ident : $v:ty )* $(,)? ),
        $ret:ty
     )=>{
        $( #[$outer] )*
        pub fn $name (&self $( , $k : $v)* ) -> $ret {
            match self {
                &MapTile::None => panic!("tile not on map"),
                &MapTile::Some(MapTileInner {
                    coords,
                    ref state,
                }) => {
                    let mut guard = state.borrow_mut();
                    MapTileInner::$name(
                        coords,
                        &mut *guard,
                        $( $k, )*
                    )
                }
            }
        }
    };
}

map_tile_delegate! {
    /// Get the coordinates of this tile.
    fn coords(c: Coords, _map: &MapStateInner) -> Coords;

    /// Get all info units at tile.
    fn info_units(c: Coords, map: &MapStateInner) -> Vec<Unit<InfoUnitType>>;

    /// Get optional wall unit at tile.
    fn wall_unit(c: Coords, map: &MapStateInner) -> Option<Unit<FirewallUnitType>>;

    /// Get optional remove unit at tile.
    fn remove_unit(c: Coords, map: &MapStateInner) -> Option<Unit<RemoveUnitType>>;

    /// Can the given number of a given unit type be spawned at this tile? If not, why?
    fn can_spawn(c: Coords, map: &MapStateInner, unit_type: impl Into<UnitType>, quantity: u32) -> CanSpawn;

    /// Can a firewall be removed at this tile? If not, why?
    fn can_remove_firewall(c: Coords, map: &MapStateInner) -> CanRemove;

    /// Attempt to spawn a unit on the board.
    fn spawn(c: Coords, map: &mut MapStateInner, unit_type: impl Into<SpawnableUnitType>) -> Result<(), CanSpawn>;

    /// Attempt to spawn a unit at a location, returning whether successful.
    fn try_spawn(c: Coords, map: &mut MapStateInner, unit_type: impl Into<SpawnableUnitType>) -> bool;

    /// Attempt to remove a firewall from a location on the board.
    fn remove_firewall(c: Coords, map: &mut MapStateInner) -> Result<(), CanRemove>;

    /// Attempt to remove a firewall from a location on the board, returning whether successful.
    fn try_remove_firewall(c: Coords, map: &mut MapStateInner) -> bool;
}

macro_rules! map_state_delegate {
    {$(
        $( #[$outer:meta] )*
        fn $name:ident(&self $(, $k:ident : $v:ty )* $(,)?) -> $ret:ty;
    )*}=>{
        impl MapState {
            $(
            $( #[$outer] )*
            pub fn $name(&self $(, $k : $v)*) -> $ret {
                let guard = self.inner.borrow();
                guard.$name($( $k ),*)
            }
            )*
        }
    };
}

map_state_delegate! {
    /// How much of a specific resource do we currently own.
    fn resource_owned(&self, resource: Resource) -> f32;

    /// How much does a certain unit type cost to spawn, in its respective resource unit.
    fn cost_of(&self, unit_type: impl Into<SpawnableUnitType>) -> f32;

    /// How many of a certain unit type can we afford to spawn.
    fn number_affordable(&self, unit_type: impl Into<SpawnableUnitType>) -> u32;

    /// Inner frame data.
    fn frame_data(&self) -> Box<FrameData>;

    /// Inner game config data.
    fn config(&self) -> Arc<Config>;

    /// Inner unit type atlas.
    fn atlas(&self) -> Arc<UnitTypeAtlas>;

    /// Submit the recorded spawn commands to the game engine.
    fn submit(&self) -> ();
}
