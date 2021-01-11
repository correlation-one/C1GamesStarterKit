
use super::*;

pub fn parse_frame(
    config: Arc<Config>,
    frame: Box<FrameData>,
    atlas: Arc<UnitTypeAtlas>,
) -> Result<MapState, MapParseError> {
// create the grids
    let mut walls: Grid<Option<Unit<StructureUnitType>>> =
        Grid::from_generator(|_| None);
    let mut remove: Grid<Option<Unit<RemoveUnitType>>> =
        Grid::from_generator(|_| None);
    let mut upgrade: Grid<Option<Unit<UpgradeUnitType>>> =
        Grid::from_generator(|_| None);
    let mut mobile: Grid<Vec<Unit<MobileUnitType>>> =
        Grid::from_generator(|_| Vec::new());

    // for each player
    for player in PlayerId::into_enum_iter() {
        let units: &frame::PlayerUnits = match player {
            PlayerId::Player1 => &frame.p1_units,
            PlayerId::Player2 => &frame.p2_units,
        };

        // fill in the mobile units
        for unit_type in MobileUnitType::into_enum_iter() {
            let unit_data_vec: &[frame::PlayerUnit] = match unit_type {
                MobileUnitType::Scout => &units.scout,
                MobileUnitType::Demolisher => &units.demolisher,
                MobileUnitType::Interceptor => &units.interceptor,
            };
            for unit_data in unit_data_vec {
                mobile.get_mut(unit_data.coords)
                    .ok_or(MapParseError::UnitInIllegalPosition(unit_data.coords))?
                    .push(Unit {
                        unit_type,
                        health: unit_data.stability,
                        id: Some(unit_data.unit_id.clone()),
                        owner: player,
                    });
            }
        }

        // fill in the wall units
        for unit_type in StructureUnitType::into_enum_iter() {
            let unit_data_vec: &[frame::PlayerUnit] = match unit_type {
                StructureUnitType::Wall => &units.wall,
                StructureUnitType::Support => &units.support,
                StructureUnitType::Turret => &units.turret,
            };
            for unit_data in unit_data_vec {
                let slot: &mut Option<Unit<StructureUnitType>> = walls.get_mut(unit_data.coords)
                    .ok_or(MapParseError::UnitInIllegalPosition(unit_data.coords))?;
                if slot.is_some() {
                    return Err(MapParseError::MultipleWallsSamePosition(unit_data.coords));
                }
                *slot = Some(Unit {
                    unit_type,
                    health: unit_data.stability,
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
                health: unit_data.stability,
                id: Some(unit_data.unit_id.clone()),
                owner: player
            });
        }

        // fill in the upgrade units
        for unit_data in &units.upgrade {
            let slot: &mut Option<Unit<UpgradeUnitType>> = upgrade.get_mut(unit_data.coords)
                .ok_or(MapParseError::UnitInIllegalPosition(unit_data.coords))?;
            if slot.is_some() {
                return Err(MapParseError::MultipleUpgradesSamePosition(unit_data.coords));
            }
            *slot = Some(Unit {
                unit_type: UpgradeUnitType,
                health: unit_data.stability,
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
        mobile,
        upgrade,

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
    MultipleUpgradesSamePosition(Coords),
    DeserializeError(serde_json::Error),
}
