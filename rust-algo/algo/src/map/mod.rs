
use crate::{
    units::*,
    coords::Coords,
    messages::{
        PlayerId,
        FrameData,
        Config,
        frame,
        config::{
            UnitCategory,
            UnitInformation,
        },
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
    u32,
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

    walls: Grid<Option<Unit<StructureUnitType>>>,
    mobile: Grid<Vec<Unit<MobileUnitType>>>,
    remove: Grid<Option<Unit<RemoveUnitType>>>,
    upgrade: Grid<Option<Unit<UpgradeUnitType>>>,

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

#[derive(Copy, Clone, Debug, PartialEq, PartialOrd)]
pub struct Cost {
    pub bits: Option<f32>,
    pub cores: Option<f32>,
}

impl Cost {
    pub fn filter_nonzero(self) -> Self {
        Cost {
            bits: self.bits.filter(|&n| n != 0.0),
            cores: self.cores.filter(|&n| n != 0.0),
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
    fn cost_of(&self, unit_type: impl Into<SpawnableUnitType>) -> Cost {
        let unit_type: UnitType = unit_type.into().into();
        let unit = &self.config.unit_information[unit_type as usize];

        Cost {
            cores: unit.cost1.filter(|&n| n != 0.0),
            bits: unit.cost2.filter(|&n| n != 0.0),
        }
    }

    /// How many of a certain unit type can we afford to spawn.
    fn number_affordable(&self, unit_type: impl Into<SpawnableUnitType>) -> u32 {
        let unit_type: SpawnableUnitType = unit_type.into();
        let cost = self.cost_of(unit_type);

        u32::min(
            cost.bits
                .map(|cost| self.frame.p1_stats.bits / cost)
                .map(|n| n as u32)
                .unwrap_or(99),
            cost.cores
                .map(|cost| self.frame.p1_stats.cores / cost)
                .map(|n| n as u32)
                .unwrap_or(99),
        )
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
    /// If a Scout were spawned at this tile, and it navigated through the map without any walls
    /// changing or the Scout dying, what path would it take?
    pub fn pathfind(&self, start: Coords, target: MapEdge) -> Result<Vec<Coords>, StartedAtWall> {
        pathfinding::pathfind(self, &self[start], target)
    }
}

impl MapTileInner {
    /// Get the coordinates of this tile.
    fn coords(c: Coords, _map: &MapStateInner) -> Coords {
        c
    }

    /// Get all mobile units at tile.
    fn mobile_units(c: Coords, map: &MapStateInner) -> Vec<Unit<MobileUnitType>> {
        map.mobile[c].clone()
    }

    /// Get optional wall unit at tile.
    fn wall_unit(c: Coords, map: &MapStateInner) -> Option<Unit<StructureUnitType>> {
        map.walls[c].clone()
    }

    /// Get optional remove unit at tile.
    fn remove_unit(c: Coords, map: &MapStateInner) -> Option<Unit<RemoveUnitType>> {
        map.remove[c].clone()
    }

    /// Get optional upgrade unit at tile.
    fn upgrade_unit(c: Coords, map: &MapStateInner) -> Option<Unit<UpgradeUnitType>> {
        map.upgrade[c].clone()
    }

    /// Can the given number of a given unit type be spawned at this tile? If not, why?
    fn can_spawn(c: Coords, map: &MapStateInner, unit_type: impl Into<UnitType>, quantity: u32) -> CanSpawn {
        let unit_type = unit_type.into();
        if let Some(not_enough_resources) = {

            unit_type.as_spawnable().and_then(|spawnable| {
                let cost = map.cost_of(spawnable);

                let need_bits = cost.bits.unwrap_or(0.0) * quantity as f32;
                let need_cores = cost.cores.unwrap_or(0.0) * quantity as f32;

                let have_bits = map.resource_owned(Resource::Bits);
                let have_cores = map.resource_owned(Resource::Cores);

                if need_bits > have_bits || need_cores > have_cores {
                    Some(CanSpawn::NotEnoughResources {
                        need_bits,
                        need_cores,
                        have_bits,
                        have_cores,
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
        } else if unit_type.is_structure() && Self::mobile_units(c, map).len() > 0 {
            CanSpawn::UnitAlreadyPresent {
                coords: c,
                unit_present: UnitPresent::Mobile,
            }
        } else if c.y < 0 || c.y >= BOARD_SIZE as i32 / 2 {
            CanSpawn::WrongSideOfMap(c)
        } else if !MAP_BOUNDS.is_in_arena(c) {
            CanSpawn::OutOfBounds(c)
        } else if unit_type.is_mobile() && !(
            MAP_BOUNDS.is_on_edge[MapEdge::BottomLeft as usize][c.x as usize][c.y as usize] ||
                MAP_BOUNDS.is_on_edge[MapEdge::BottomRight as usize][c.x as usize][c.y as usize]
        ) {
            CanSpawn::NotOnEdge(c)
        } else {
            CanSpawn::Yes
        }
    }

    /// Can a Structure be removed at this tile? If not, why?
    fn can_remove_structure(c: Coords, map: &MapStateInner) -> CanRemove {
        if !MAP_BOUNDS.is_in_arena(c) {
            CanRemove::OutOfBounds(c)
        } else if c.y >= BOARD_SIZE as i32 / 2 {
            CanRemove::WrongSideOfMap(c)
        } else if Self::mobile_units(c, map).len() > 0 {
            CanRemove::MobileUnitPresent(c)
        } else if Self::wall_unit(c, map).is_none() {
            CanRemove::NoUnitPresent(c)
        } else {
            CanRemove::Yes
        }
    }

    fn upgrade_cost(unit_info: &UnitInformation) -> Cost {
        let cores = unit_info.upgrade.as_ref()
            .and_then(|info| info.cost1)
            .unwrap_or(unit_info.cost1
                .unwrap_or(0.0));
        let bits = unit_info.upgrade.as_ref()
            .and_then(|info| info.cost2)
            .unwrap_or(unit_info.cost2
                .unwrap_or(0.0));

        Cost {
            cores: Some(cores),
            bits: Some(bits),
        }.filter_nonzero()
    }

    fn can_upgrade(c: Coords, map: &MapStateInner) -> CanUpgrade {

        if !MAP_BOUNDS.is_in_arena(c) {
            CanUpgrade::OutOfBounds(c)
        } else if c.y >= BOARD_SIZE as i32 / 2 {
            CanUpgrade::WrongSideOfMap(c)
        } else if Self::mobile_units(c, map).len() > 0 {
            CanUpgrade::MobileUnitPresent(c)
        } else if Self::wall_unit(c, map).is_none() {
            CanUpgrade::NoUnitPresent(c)
        } else if let Some(err) = {
            let unit = Self::wall_unit(c, map).unwrap();
            let atlas = map.atlas();
            let info = atlas.type_mobile(unit.unit_type.into());
            let cost = Self::upgrade_cost(info);

            let need_bits = cost.bits.unwrap_or(0.0);
            let need_cores = cost.cores.unwrap_or(0.0);

            let have_bits = map.resource_owned(Resource::Bits);
            let have_cores = map.resource_owned(Resource::Cores);

            if need_bits > have_bits || need_cores > have_cores {
                Some(CanUpgrade::NotEnoughResources {
                    need_bits,
                    need_cores,
                    have_bits,
                    have_cores,
                })
            } else {
                None
            }
        } {
            err
        } else if map.upgrade[c].is_some() {
            CanUpgrade::AlreadyUpgraded
        } else {
            CanUpgrade::Yes
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
        let cost = map.cost_of(unit_type);
        map.frame.p1_stats.cores -= cost.cores.unwrap_or(0.0);
        map.frame.p1_stats.bits -= cost.bits.unwrap_or(0.0);

        let unit_info =  map.atlas.type_mobile(unit_type.into());
        match unit_info.unit_category {
            Some(UnitCategory::Structure) => {
                let unit = Unit {
                    unit_type: unit_type.into_structure().unwrap(),
                    health: unit_info.start_health.unwrap_or(0.0),
                    id: None,
                    owner: PlayerId::Player1,
                };
                map.walls[coords] = Some(unit);
            },

            Some(UnitCategory::Mobile) => {
                let unit = Unit {
                    unit_type: unit_type.into_mobile().unwrap(),
                    health: unit_info.start_health.unwrap_or(0.0),
                    id: None,
                    owner: PlayerId::Player1,
                };
                map.mobile[coords].push(unit);
            },

            None => panic!("unit info of spawnable unit does not have unit category"),
        };

        // add it to the command stack
        let unit_type: UnitType = unit_type.into();
        let spawn = SpawnCommand::new(unit_type, coords, &*map.atlas);
        if unit_type.is_structure() || unit_type == UnitType::Remove {
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

    fn upgrade(c: Coords, map: &mut MapStateInner) -> Result<(), CanUpgrade> {
        match Self::can_upgrade(c, map) {
            CanUpgrade::Yes => (),
            cannot => return Err(cannot),
        };

        map.upgrade[c] = Some(Unit {
            unit_type: UpgradeUnitType,
            health: 1.0,
            id: None,
            owner: PlayerId::Player1,
        });

        let wall = map.walls[c].as_ref().unwrap();
        let atlas = map.atlas();
        let unit_info = atlas.type_mobile(wall.unit_type.into());
        let cost = Self::upgrade_cost(unit_info);
        map.frame.p1_stats.cores -= cost.cores.unwrap_or(0.0);
        map.frame.p1_stats.bits -= cost.bits.unwrap_or(0.0);

        map.build_stack.push(SpawnCommand::new(
            UnitType::Upgrade, c, &*map.atlas
        ));

        Ok(())
    }

    /// Attempt to remove a Structure from a location on the board.
    fn remove_structure(c: Coords, map: &mut MapStateInner) -> Result<(), CanRemove> {
        let coords = c;

        match Self::can_remove_structure(c, map) {
            CanRemove::Yes => (),
            cannot => return Err(cannot),
        };

        // add the remove unit
        map.remove[coords] = Some(Unit {
            unit_type: RemoveUnitType,
            health: 1.0,
            id: None,
            owner: PlayerId::Player1,
        });

        // add it to the command stack
        map.build_stack.push(SpawnCommand::new(
            UnitType::Remove, coords, &*map.atlas
        ));

        // success
        Ok(())
    }

    /// Attempt to remove a Structure from a location on the board, returning whether successful.
    fn try_remove_structure(c: Coords, map: &mut MapStateInner) -> bool {
        Self::remove_structure(c, map).is_ok()
    }

    fn try_upgrade(c: Coords, map: &mut MapStateInner) -> bool {
        Self::upgrade(c, map).is_ok()
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
        have_bits: f32,
        need_bits: f32,
        have_cores: f32,
        need_cores: f32,
    },
    UnitAlreadyPresent {
        coords: Coords,
        unit_present: UnitPresent
    }
}

/// Whether a Structure can be removed at a location.
#[derive(Debug, Copy, Clone, PartialEq)]
pub enum CanRemove {
    Yes,
    OutOfBounds(Coords),
    WrongSideOfMap(Coords),
    NoUnitPresent(Coords),
    MobileUnitPresent(Coords),
}

#[derive(Debug, Copy, Clone, PartialEq)]
pub enum CanUpgrade {
    Yes,
    OutOfBounds(Coords),
    WrongSideOfMap(Coords),
    NoUnitPresent(Coords),
    MobileUnitPresent(Coords),
    AlreadyUpgraded,
    NotEnoughResources {
        have_bits: f32,
        need_bits: f32,
        have_cores: f32,
        need_cores: f32,
    },
}

/// Details on a possible unit spawn being blocked by another unit.
#[derive(Debug, Copy, Clone, PartialEq)]
pub enum UnitPresent {
    Wall,
    Mobile
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
    pub health: f32,
    pub id: Option<String>,
    pub owner: PlayerId,
}

impl<T: Into<UnitType>> Unit<T> {
    /// Turn this Unit<T> into a Unit<UnitType>
    pub fn unspecialize(self) -> Unit<UnitType> {
        Unit {
            unit_type: self.unit_type.into(),
            health: self.health,
            id: self.id,
            owner: self.owner,
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

impl CanUpgrade {
    /// Whether self is CanUpgrade::Yes
    pub fn yes(self) -> bool {
        self == CanUpgrade::Yes
    }
}

impl Resource {
    /// Get the resource which spawns a particular unit type.
    pub fn which_buys(unit_type: impl Into<SpawnableUnitType>) -> Self {
        let unit_type: SpawnableUnitType = unit_type.into();
        match unit_type {
            SpawnableUnitType::Mobile(_) => Resource::Bits,
            SpawnableUnitType::Structure(_) => Resource::Cores,
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

    /// Get all mobile units at tile.
    fn mobile_units(c: Coords, map: &MapStateInner) -> Vec<Unit<MobileUnitType>>;

    /// Get optional wall unit at tile.
    fn wall_unit(c: Coords, map: &MapStateInner) -> Option<Unit<StructureUnitType>>;

    fn upgrade_unit(c: Coords, map: &MapStateInner) -> Option<Unit<UpgradeUnitType>>;

    /// Get optional remove unit at tile.
    fn remove_unit(c: Coords, map: &MapStateInner) -> Option<Unit<RemoveUnitType>>;

    /// Can the given number of a given unit type be spawned at this tile? If not, why?
    fn can_spawn(c: Coords, map: &MapStateInner, unit_type: impl Into<UnitType>, quantity: u32) -> CanSpawn;

    /// Can a structure be removed at this tile? If not, why?
    fn can_remove_structure(c: Coords, map: &MapStateInner) -> CanRemove;

    fn can_upgrade(c: Coords, map: &MapStateInner) -> CanUpgrade;

    fn upgrade(c: Coords, map: &mut MapStateInner) -> Result<(), CanUpgrade>;

    /// Attempt to spawn a unit on the board.
    fn spawn(c: Coords, map: &mut MapStateInner, unit_type: impl Into<SpawnableUnitType>) -> Result<(), CanSpawn>;

    /// Attempt to spawn a unit at a location, returning whether successful.
    fn try_spawn(c: Coords, map: &mut MapStateInner, unit_type: impl Into<SpawnableUnitType>) -> bool;

    /// Attempt to remove a Structure from a location on the board.
    fn remove_structure(c: Coords, map: &mut MapStateInner) -> Result<(), CanRemove>;

    /// Attempt to remove a Structure from a location on the board, returning whether successful.
    fn try_remove_structure(c: Coords, map: &mut MapStateInner) -> bool;

    fn try_upgrade(c: Coords, map: &mut MapStateInner) -> bool;
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
    fn cost_of(&self, unit_type: impl Into<SpawnableUnitType>) -> Cost;

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
