
use coords::Coords;
use super::units::*;
use super::messages::{PlayerId, FrameData, Config, frame, config::UnitInformation};
use super::bounds::{MAP_BOUNDS, BOARD_SIZE, MapEdge};
use super::grid::Grid;
use super::pathfinding::StartedAtWall;
use super::pathfinding;

use serde_json;
use enum_iterator::IntoEnumIterator;

use std::sync::Arc;

/// A random-access, mutable representation of the map.
pub struct Map {
    config: Arc<Config>,
    frame: Box<FrameData>,
    walls: Grid<Option<Unit<FirewallUnitType>>>,
    remove: Grid<Option<Unit<RemoveUnitType>>>,
    info: Grid<Vec<Unit<InfoUnitType>>>,
}

/// A unit on the map. Generic over the set of unit type.
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

/// All the ways in which a map can fail to parse from a string.
#[derive(Debug)]
pub enum MapParseError {
    UnitInIllegalPosition(Coords),
    MultipleWallsSamePosition(Coords),
    MultipleRemovesSamePosition(Coords),
    DeserializeError(serde_json::Error),
}

impl Map {
    /// Attempt to parse a new map from a deserialized config and frame data.
    pub fn new(config: Arc<Config>, frame: Box<FrameData>) -> Result<Self, MapParseError> {
        // create the grids
        let mut walls = Grid::new(|_| None);
        let mut remove = Grid::new(|_| None);
        let mut info = Grid::new(|_| Vec::new());

        // for each player
        for &player in PlayerId::all() {
            let units: &frame::PlayerUnits = match player {
                PlayerId::Player1 => &frame.p1_units,
                PlayerId::Player2 => &frame.p2_units,
            };

            // fill in the info units
            for unit_type in InfoUnitType::into_enum_iter() {
                let unit_data_vec: &Vec<frame::PlayerUnit> = match unit_type {
                    InfoUnitType::Ping => units.ping(),
                    InfoUnitType::Emp => units.emp(),
                    InfoUnitType::Scrambler => units.scrambler(),
                };
                for unit_data in unit_data_vec {
                    info.get_mut(unit_data.coords())
                        .ok_or(MapParseError::UnitInIllegalPosition(unit_data.coords()))?
                        .push(Unit {
                            unit_type,
                            stability: unit_data.stability(),
                            id: Some(unit_data.unit_id().clone()),
                            owner: player,
                        });
                }
            }

            // fill in the wall units
            for unit_type in FirewallUnitType::into_enum_iter() {
                let unit_data_vec: &Vec<frame::PlayerUnit> = match unit_type {
                    FirewallUnitType::Filter => units.filter(),
                    FirewallUnitType::Encryptor => units.encryptor(),
                    FirewallUnitType::Destructor => units.destructor()
                };
                for unit_data in unit_data_vec {
                    let slot: &mut Option<Unit<FirewallUnitType>> = walls.get_mut(unit_data.coords())
                        .ok_or(MapParseError::UnitInIllegalPosition(unit_data.coords()))?;
                    if slot.is_some() {
                        return Err(MapParseError::MultipleWallsSamePosition(unit_data.coords()));
                    }
                    *slot = Some(Unit {
                        unit_type,
                        stability: unit_data.stability(),
                        id: Some(unit_data.unit_id().clone()),
                        owner: player
                    });
                }
            }

            // fill in the remove units
            for unit_data in units.remove() {
                let slot: &mut Option<Unit<RemoveUnitType>> = remove.get_mut(unit_data.coords())
                    .ok_or(MapParseError::UnitInIllegalPosition(unit_data.coords()))?;
                if slot.is_some() {
                    return Err(MapParseError::MultipleRemovesSamePosition(unit_data.coords()));
                }
                *slot = Some(Unit {
                    unit_type: RemoveUnitType,
                    stability: unit_data.stability(),
                    id: Some(unit_data.unit_id().clone()),
                    owner: player
                });
            }
        }

        Ok(Map {
            config,
            frame,
            walls,
            remove,
            info
        })
    }

    /// Get the MapReadTile at some coordinates.
    pub fn tile(&self, coords: Coords) -> Option<MapReadTile> {
        if MAP_BOUNDS.in_arena(coords) {
            Some(MapReadTile {
                coords,
                map: self
            })
        } else {
            None
        }
    }

    /// How much of a specific resource do we currently own.
    pub fn resource_owned(&self, resource: Resource) -> f32 {
        match resource {
            Resource::Cores => self.frame.p1_stats.cores(),
            Resource::Bits => self.frame.p1_stats.bits(),
        }
    }

    /// How much does a certain unit type cost to spawn, in its respective resource unit.
    pub fn cost_of(&self, unit_type: impl Into<SpawnableUnitType>) -> f32 {
        let unit_type: UnitType = unit_type.into().into();
        self.config.unit_information[unit_type as usize].cost().unwrap()
    }

    /// How many of a certain unit type can we afford to spawn.
    pub fn number_affordable(&self, unit_type: impl Into<SpawnableUnitType>) -> u32 {
        let unit_type: SpawnableUnitType = unit_type.into();
        let cost = self.cost_of(unit_type);
        let wealth = match unit_type {
            SpawnableUnitType::Info(_) => self.frame.p1_stats.bits(),
            SpawnableUnitType::Firewall(_) => self.frame.p1_stats.cores()
        };
        (wealth / cost) as u32
    }

    /// Combine self with a UnitTypeAtlas into a MoveBuilder.
    pub fn builder(self, atlas: Arc<UnitTypeAtlas>) -> GameState {
        GameState {
            map: self,
            atlas,
            build_stack: Vec::new(),
            deploy_stack: Vec::new(),
        }
    }

    /// Access the inner frame data.
    pub fn data(&self) -> &FrameData {
        &self.frame
    }
}

/// A reference to a valid tile on a map.
#[derive(Copy, Clone)]
pub struct MapReadTile<'a> {
    coords: Coords,
    map: &'a Map,
}

/// The operations on a map cell are implemented via default trait methods, to conveniently
/// implement them on both mutable and immutable cells.
pub trait MapTile {
    /// The coordinates of this tile.
    fn coords(&self) -> Coords;

    /// The borrowed map.
    fn map(&self) -> &Map;

    /// Get the vec of info units at this tile.
    fn get_info(&self) -> &Vec<Unit<InfoUnitType>> {
        self.map().info.get(self.coords()).unwrap()
    }

    /// Get the optional firewall unit at this tile.
    fn get_wall(&self) -> Option<Unit<FirewallUnitType>> {
        self.map().walls.get(self.coords()).unwrap().to_owned()
    }

    /// Get the optional remove unit at this tile.
    fn get_remove(&self) -> Option<Unit<RemoveUnitType>> {
        self.map().remove.get(self.coords()).unwrap().to_owned()
    }

    /// Can the given number of a given unit type be spawned at this tile? If not, why?
    fn can_spawn(&self, unit_type: impl Into<UnitType>, quantity: u32) -> CanSpawn {
        let unit_type = unit_type.into();
        if let Some(not_enough_resources) = {
            unit_type.as_spawnable().and_then(|spawnable| {
                let resource = Resource::which_buys(spawnable);
                let have = self.map().resource_owned(resource);
                let need = self.map().cost_of(spawnable) * quantity as f32;
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
        } else if unit_type != UnitType::Remove && self.get_wall().is_some() {
            CanSpawn::UnitAlreadyPresent {
                coords: self.coords(),
                unit_present: UnitPresent::Wall,
            }
        } else if unit_type.is_firewall() && self.get_info().len() > 0 {
            CanSpawn::UnitAlreadyPresent {
                coords: self.coords(),
                unit_present: UnitPresent::Info,
            }
        } else if self.coords().y < 0 || self.coords().y >= BOARD_SIZE as i32 / 2 {
            CanSpawn::WrongSideOfMap(self.coords())
        } else if !MAP_BOUNDS.in_arena(self.coords()) {
            CanSpawn::OutOfBounds(self.coords())
        } else if unit_type.is_info() && !(
            MAP_BOUNDS.is_on_edge[MapEdge::BottomLeft as usize][self.coords().x as usize][self.coords().y as usize] ||
                MAP_BOUNDS.is_on_edge[MapEdge::BottomRight as usize][self.coords().x as usize][self.coords().y as usize]
        ) {
            CanSpawn::NotOnEdge(self.coords())
        } else {
            CanSpawn::Yes
        }
    }

    /// Can a firewall be removed at this tile? If not, why?
    fn can_remove_firewall(&self) -> CanRemove {
        if !MAP_BOUNDS.in_arena(self.coords()) {
            CanRemove::OutOfBounds(self.coords())
        } else if self.coords().y >= BOARD_SIZE as i32 / 2 {
            CanRemove::WrongSideOfMap(self.coords())
        } else if self.get_info().len() > 0 {
            CanRemove::InfoUnitPresent(self.coords())
        } else if self.get_wall().is_none() {
            CanRemove::NoUnitPresent(self.coords())
        } else {
            CanRemove::Yes
        }
    }

    /// If a ping were spawned at this tile, and it navigated through the map without any walls
    /// changing or the ping dying, what path would it take?
    fn pathfind(&self, target: MapEdge) -> Result<Vec<Coords>, StartedAtWall> {
        pathfinding::pathfind(self.map(), MapReadTile {
            coords: self.coords(),
            map: self.map(),
        }, target)
    }
}

impl<'a> MapTile for MapReadTile<'a> {
    fn coords(&self) -> Coords {
        self.coords
    }

    fn map(&self) -> &Map {
        &self.map
    }
}

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
impl CanSpawn {
    /// Whether self is CanSpawn::Yes
    pub fn affirmative(self) -> bool {
        self == CanSpawn::Yes
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
impl CanRemove {
    /// Whether self is CanRemove::Yes
    pub fn affirmative(self) -> bool {
        self == CanRemove::Yes
    }
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

/// A wrapper around a map which allows mutation of the map in the form of valid game moves, which
/// can then be submitted to the game.
pub struct GameState {
    map: Map,
    atlas: Arc<UnitTypeAtlas>,
    build_stack: Vec<SpawnCommand>,
    deploy_stack: Vec<SpawnCommand>,
}

impl GameState {
    /// Get the atlas, as a normal reference
    pub fn atlas(&self) -> &UnitTypeAtlas {
        &self.atlas
    }

    /// Get the referenced map, which may be mutated by move builder operations.
    pub fn map(&self) -> &Map {
        &self.map
    }

    /// Get the builder tile at some coords.
    pub fn tile(&mut self, coords: Coords) -> Option<StateTile> {
        if MAP_BOUNDS.in_arena(coords) {
            Some(StateTile {
                coords,
                builder: self
            })
        } else {
            None
        }
    }

    /// Attempt to simultaneously borrow out multiple BuilderTiles.
    pub fn multiple_tiles<'a>(&'a mut self, holders: &mut [StateTileOutputVar<'a>]) {
        let mut gotten = Grid::new(|_| false);
        for holder in holders {
            if let Some(coord) = match holder {
                &mut StateTileOutputVar::Get(coord) => Some(coord),
                _ => None
            } {
                if *gotten.get(coord).unwrap() {
                    *holder = StateTileOutputVar::Err(RequestedSameTileTwice(coord));
                } else {
                    *gotten.get_mut(coord).unwrap() = true;
                    *holder = StateTileOutputVar::Got(unsafe {
                        (&mut*(self as *mut Self)).tile(coord)
                    });
                }
            }
        }
    }

    /// Attempt to spawn a unit type at several coords, returning the number of successes, or
    /// failing if a tile is invalid. This operation is not atomic in terms of success/failure.
    pub fn attempt_spawn_multiple(&mut self, coords: &[Coords],
                                  unit_type: impl Into<SpawnableUnitType>) -> Result<u32, InvalidTile> {
        let unit_type = unit_type.into();
        let mut successful = 0;
        for &coord in coords {
            if self.tile(coord)
                .ok_or(InvalidTile(coord))?
                .attempt_spawn(unit_type) {
                successful += 1;
            }
        }
        Ok(successful)
    }

    /// Attempt to remove firewalls at several coords, returning the number of successes, or
    /// failing if a tile is invalid. This operation is not atomic in terms of success/failure.
    pub fn attempt_remove_multiple(&mut self, coords: &[Coords]) -> Result<u32, InvalidTile> {
        let mut successful = 0;
        for &coord in coords {
            if self.tile(coord)
                .ok_or(InvalidTile(coord))?
                .attempt_remove_firewall() {
                successful += 1;
            }
        }
        Ok(successful)
    }

    /// Submit the recorded spawn commands to the game engine.
    pub fn submit(self) -> Self {
        let line = serde_json::to_string(&self.build_stack).unwrap();
        println!("{}", line);
        let line = serde_json::to_string(&self.deploy_stack).unwrap();
        println!("{}", line);
        self
    }
}

/// Error type for attempting an operation on an invalid tile.
#[derive(Debug)]
pub struct InvalidTile(pub Coords);

#[derive(Debug, Clone, Serialize)]
struct SpawnCommand(String, i32, i32);
impl SpawnCommand {
    fn new(unit_type: UnitType, coords: Coords, atlas: &UnitTypeAtlas) -> Self {
        SpawnCommand(atlas.type_into_shorthand(unit_type).clone(), coords.x, coords.y)
    }
}

/// A mutable MoveBuilder tile, which has the functionality of a normal MapTile, but also
/// the ability to mutate the Map in the form of valid moves.
pub struct StateTile<'a> {
    coords: Coords,
    builder: &'a mut GameState,
}

impl<'a> MapTile for StateTile<'a> {
    fn coords(&self) -> Coords {
        self.coords
    }

    fn map(&self) -> &Map {
        &self.builder.map
    }
}

impl<'a> StateTile<'a> {
    /// View this mutable tile as an immutable tile. This should be rarely necessary, as all
    /// MapTile ops are already implemented on BuilderTile.
    pub fn as_read_tile(&self) -> MapReadTile {
        MapReadTile {
            coords: self.coords,
            map: &self.builder.map
        }
    }

    /// Transform this mutable tile into an immutable tile.
    pub fn into_read_tile(self) -> MapReadTile<'a> {
        MapReadTile {
            coords: self.coords,
            map: &self.builder.map
        }
    }

    /// Attempt to spawn a unit on the board.
    pub fn spawn(&mut self, unit_type: impl Into<SpawnableUnitType>) -> Result<(), CanSpawn> {
        let coords = self.coords();

        let unit_type = unit_type.into();
        // assert that the move is valid
        match self.can_spawn(unit_type, 1) {
            CanSpawn::Yes => (),
            cannot => return Err(cannot)
        };

        // subtract the cost from our wealth
        let resource = Resource::which_buys(unit_type);
        let cost = self.map().cost_of(unit_type);
        match resource {
            Resource::Cores => *self.builder.map.frame.p1_stats.cores_mut() -= cost,
            Resource::Bits => *self.builder.map.frame.p1_stats.bits_mut() -= cost,
        };

        match unit_type {
            SpawnableUnitType::Firewall(unit_type) => {
                if let UnitInformation::Wall{stability,..} = self.builder.atlas.type_info(unit_type.into()) {
                    let unit = Unit {
                        unit_type,
                        stability: *stability,
                        id: None,
                        owner: PlayerId::Player1
                    };
                    *self.builder.map.walls.get_mut(coords).unwrap() = Some(unit);
                }
            },
            SpawnableUnitType::Info(unit_type) => {
                if let UnitInformation::Data{stability,..} = self.builder.atlas.type_info(unit_type.into()) {
                    let unit = Unit {
                        unit_type,
                        stability: *stability,
                        id: None,
                        owner: PlayerId::Player1
                    };
                    self.builder.map.info.get_mut(coords).unwrap().push(unit);
                }
            }
        }

        // add it to the command stack
        let unit_type: UnitType = unit_type.into();
        let spawn = SpawnCommand::new(unit_type, coords, &*self.builder.atlas);
        if unit_type.is_firewall() || unit_type == UnitType::Remove {
            self.builder.build_stack.push(spawn);
        } else {
            self.builder.deploy_stack.push(spawn);
        }

        // success
        Ok(())
    }

    /// Attempt to spawn a unit at a location, returning whether successful.
    pub fn attempt_spawn(&mut self, unit_type: impl Into<SpawnableUnitType>) -> bool {
        self.spawn(unit_type).is_ok()
    }

    /// Attempt to remove a firewall from a location on the board.
    pub fn remove_firewall(&mut self) -> Result<(), CanRemove> {
        let coords = self.coords();

        match self.can_remove_firewall() {
            CanRemove::Yes => (),
            cannot => return Err(cannot),
        };

        // remove the unit, saving the unit type and asserting that the unit previously existed
        let unit_type = self.builder.map.walls.get_mut(coords).unwrap().take().unwrap().unit_type;

        // add the remove unit
        *self.builder.map.remove.get_mut(coords).unwrap() = Some(Unit {
            unit_type: RemoveUnitType,
            stability: 1.0,
            id: None,
            owner: PlayerId::Player1
        });

        // refund the cost
        let resource = Resource::which_buys(unit_type);
        let cost = self.map().cost_of(unit_type);
        match resource {
            Resource::Cores => *self.builder.map.frame.p1_stats.cores_mut() += cost,
            Resource::Bits => *self.builder.map.frame.p1_stats.bits_mut() += cost,
        };

        // add it to the command stack
        self.builder.build_stack.push(SpawnCommand::new(
            UnitType::Remove, coords, &*self.builder.atlas));

        // success
        Ok(())
    }

    /// Attempt to remove a firewall from a location on the board, returning whether successful.
    pub fn attempt_remove_firewall(&mut self) -> bool {
        self.remove_firewall().is_ok()
    }
}

/// Enum used to retrieve multiple builder tiles on the same map simultaneously.
pub enum StateTileOutputVar<'a> {
    Get(Coords),
    Got(Option<StateTile<'a>>),
    Err(RequestedSameTileTwice),
    Taken,
}

/// Error that occurs when retrieving multiple builder tiles on the same map simultaneously.
#[derive(Debug, Copy, Clone)]
pub enum GetMultipleStateTilesError {
    RequestedSameTileTwice(Coords),
    InvalidCoord(Coords),
}

/// Error that occurs when retrieving multiple builder tiles on the same map simultaneously,
/// due to requesting the same tile twice.
#[derive(Debug, Copy, Clone)]
pub struct RequestedSameTileTwice(pub Coords);

/// The `multiple_builder_tiles!` macro accepts a move builder, then several coordinates, and expresses an
/// array of `Option<BuilderTile>`. The array is fixed-size, and equal in length to the number of coordinates given to the macro.
/// A particular tile will be `None` if it is an invalid tile, or borrowed twice.
#[macro_export]
macro_rules! multiple_builder_tiles {
    ($builder:expr, $( $coord:expr ),* ) => {{
        macro_rules! phantom_macro {
            ($e:expr) => { () }
        }

        use std::mem;

        let mut gets = [$( BuilderTileOutputVar::Get($coord), )*];
        $builder.multiple_tiles(&mut gets[..]);
        let mut out = [
            $({{
                let _ = phantom_macro!($coord);
                None
            }},)*
        ];
        for i in 0..gets.len() {
            match mem::replace(&mut gets[i], BuilderTileOutputVar::Taken) {
                BuilderTileOutputVar::Got(Some(tile)) => {
                    out[i] = Some(tile);
                },
                BuilderTileOutputVar::Got(None) | BuilderTileOutputVar::Err(_) => (),
                BuilderTileOutputVar::Taken => panic!("BuilderTileOutputVar::Taken"),
                BuilderTileOutputVar::Get(c) => panic!("BuilderTileOutputVar::Get({:?})", c),
            };
        }
        out
    }}
}

/// The `all_state_tiles!` macro works similarly to multiple_state_tiles!, and accepts the same
/// types of parameters. However, it will fail if any of the tile acquisitions fail. It expresses a
/// `Result<[StateTile; N], GetMultipleStateTilesError>`.
#[macro_export]
macro_rules! all_state_tiles {
    ($builder:expr, $( $coord:expr ),* ) => {unsafe {
        macro_rules! phantom_macro {
            ($e:expr) => { () }
        }

        use std::mem;
        use std::ptr;

        let coords = [$( $coord, )*];
        let mut gets = [$( StateTileOutputVar::Get($coord), )*];
        $builder.multiple_tiles(&mut gets[..]);
        let mut out = [
            $({{
                let _ = phantom_macro!($coord);
                mem::uninitialized::<StateTile>()
            }},)*
        ];
        let mut i = 0;
        loop {
            if i == gets.len() {
                break Ok(out);
            }

            match mem::replace(&mut gets[i], StateTileOutputVar::Taken) {
                StateTileOutputVar::Got(Some(tile)) => {
                    ptr::write(&mut out[i], tile);
                },
                StateTileOutputVar::Got(None) => {
                    for j in 0..i {
                        ptr::drop_in_place(&mut out[j]);
                    }
                    mem::forget(out);
                    break Err(GetMultipleStateTilesError::InvalidCoord(coords[i]));
                },
                StateTileOutputVar::Err(RequestedSameTileTwice(c)) => {
                    for j in 0..i {
                        ptr::drop_in_place(&mut out[j]);
                    }
                    mem::forget(out);
                    break Err(GetMultipleStateTilesError::RequestedSameTileTwice(c));
                },
                StateTileOutputVar::Taken => panic!("StateTileOutputVar::Taken"),
                StateTileOutputVar::Get(c) => panic!("StateTileOutputVar::Get({:?})", c),
            };

            i += 1;
        }
    }}
}