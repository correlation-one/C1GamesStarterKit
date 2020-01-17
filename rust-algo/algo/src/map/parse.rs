
use super::*;

pub fn parse_frame(
    config: Arc<Config>,
    frame: Box<FrameData>,
    atlas: Arc<UnitTypeAtlas>,
) -> Result<MapState, MapParseError> {
// create the grids
    let mut walls: Grid<Option<Unit<FirewallUnitType>>> =
        Grid::from_generator(|_| None);
    let mut remove: Grid<Option<Unit<RemoveUnitType>>> =
        Grid::from_generator(|_| None);
    let mut info: Grid<Vec<Unit<InfoUnitType>>> =
        Grid::from_generator(|_| Vec::new());

    // for each player
    for player in PlayerId::into_enum_iter() {
        let units: &frame::PlayerUnits = match player {
            PlayerId::Player1 => &frame.p1_units,
            PlayerId::Player2 => &frame.p2_units,
        };

        // fill in the info units
        for unit_type in InfoUnitType::into_enum_iter() {
            let unit_data_vec: &[frame::PlayerUnit] = match unit_type {
                InfoUnitType::Ping => &units.ping,
                InfoUnitType::Emp => &units.emp,
                InfoUnitType::Scrambler => &units.scrambler,
            };
            for unit_data in unit_data_vec {
                info.get_mut(unit_data.coords)
                    .ok_or(MapParseError::UnitInIllegalPosition(unit_data.coords))?
                    .push(Unit {
                        unit_type,
                        stability: unit_data.stability,
                        id: Some(unit_data.unit_id.clone()),
                        owner: player,
                    });
            }
        }

        // fill in the wall units
        for unit_type in FirewallUnitType::into_enum_iter() {
            let unit_data_vec: &[frame::PlayerUnit] = match unit_type {
                FirewallUnitType::Filter => &units.filter,
                FirewallUnitType::Encryptor => &units.encryptor,
                FirewallUnitType::Destructor => &units.destructor,
            };
            for unit_data in unit_data_vec {
                let slot: &mut Option<Unit<FirewallUnitType>> = walls.get_mut(unit_data.coords)
                    .ok_or(MapParseError::UnitInIllegalPosition(unit_data.coords))?;
                if slot.is_some() {
                    return Err(MapParseError::MultipleWallsSamePosition(unit_data.coords));
                }
                *slot = Some(Unit {
                    unit_type,
                    stability: unit_data.stability,
                    id: Some(unit_data.unit_id.clone()),
                    owner: player
                });
            }
        }

        // fill in the remove units
        for unit_data in &units.remove {
            let slot: &mut Option<Unit<RemoveUnitType>> = remove.get_mut(unit_data.coords)
                .ok_or(MapParseError::UnitInIllegalPosition(unit_data.coords))?;
            if slot.is_some() {
                return Err(MapParseError::MultipleRemovesSamePosition(unit_data.coords));
            }
            *slot = Some(Unit {
                unit_type: RemoveUnitType,
                stability: unit_data.stability,
                id: Some(unit_data.unit_id.clone()),
                owner: player
            });
        }
    }

    let inner = MapStateInner {
        config,
        frame,

        walls,
        remove,
        info,

        atlas,
        build_stack: Vec::new(),
        deploy_stack: Vec::new(),
    };
    let inner = Rc::new(RefCell::new(inner));

    let tile_grid = Grid::from_generator(|c| {
        if c.is_in_arena() {
            MapTile::Some(MapTileInner {
                coords: c,
                state: inner.clone(),
            })
        } else {
            MapTile::None
        }
    });

    Ok(MapState {
        inner,
        tile_grid,
    })
}

/// All the ways in which a map can fail to parse from a string.
#[derive(Debug)]
pub enum MapParseError {
    UnitInIllegalPosition(Coords),
    MultipleWallsSamePosition(Coords),
    MultipleRemovesSamePosition(Coords),
    DeserializeError(serde_json::Error),
}
