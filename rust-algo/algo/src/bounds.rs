
use crate::coords::*;
use enum_iterator::IntoEnumIterator;

lazy_static! {
    /// Global cache of the shape of the game map.
    pub static ref MAP_BOUNDS: MapBounds = MapBounds::new();
}

/// Side-length of the game board.
pub const BOARD_SIZE: usize = 28;

/// Cached representation of the shape of the game map.
pub struct MapBounds {
    pub is_on_edge: [[[bool; BOARD_SIZE]; BOARD_SIZE]; 4],
    pub edge_lists: [[Coords; BOARD_SIZE / 2]; 4],
    pub arena: [[bool; BOARD_SIZE]; BOARD_SIZE],
}

impl MapBounds {
    /// Compute a cache of the map bounds.
    pub fn new() -> Self {
        fn populate(
            is_on_edge: &mut [[[bool; BOARD_SIZE]; BOARD_SIZE]; 4],
            edge_lists: &mut [[Coords; BOARD_SIZE / 2]; 4],
            edge: MapEdge,
            calc_coords: impl Fn(usize) -> [usize; 2]
        ) {
            for i in 0..BOARD_SIZE / 2 {
                let c = calc_coords(i);
                is_on_edge[edge as usize][c[0]][c[1]] = true;
                let c = Coords::from(c);
                edge_lists[edge as usize][i] = c;
            }
        }

        let mut is_on_edge = [[[false; BOARD_SIZE]; BOARD_SIZE]; 4];
        let mut edge_lists = [[ORIGIN; BOARD_SIZE / 2]; 4];

        populate(&mut is_on_edge, &mut edge_lists, MapEdge::TopRight,
                       |i| [BOARD_SIZE / 2 + i, BOARD_SIZE - 1 - i]
        );
        populate(&mut is_on_edge, &mut edge_lists, MapEdge::TopLeft,
                       |i| [BOARD_SIZE / 2 - 1 - i, BOARD_SIZE - 1 - i]
        );
        populate(&mut is_on_edge, &mut edge_lists, MapEdge::BottomLeft,
                       |i| [BOARD_SIZE / 2 - 1 - i, i]
        );
        populate(&mut is_on_edge, &mut edge_lists, MapEdge::BottomRight,
                       |i| [BOARD_SIZE / 2 + i, i]
        );

        let mut arena = [[false; BOARD_SIZE]; BOARD_SIZE];

        for i in 0..4 {
            for j in 0..BOARD_SIZE {
                for k in 0..BOARD_SIZE {
                    arena[j][k] |= is_on_edge[i][j][k];
                }
            }
        }

        for y in 0..BOARD_SIZE {
            let mut toggled = false;
            for x in 0..BOARD_SIZE {
                if arena[x][y] {
                    if toggled {
                        break;
                    } else {
                        toggled = true;
                    }
                } else if toggled {
                    arena[x][y] = true;
                }
            }
        }

        MapBounds {
            is_on_edge,
            edge_lists,
            arena
        }
    }

    /// Is the given coord in the arena?
    pub fn is_in_arena(&self, coords: Coords) -> bool {
        coords.x >= 0 &&
            coords.y >= 0 &&
            coords.x < BOARD_SIZE as i32 &&
            coords.y < BOARD_SIZE as i32 &&
            self.arena[coords.x as usize][coords.y as usize]
    }

    /// Is the given coord on the given edge?
    pub fn is_on_edge(&self, edge: MapEdge, coords: Coords) -> bool {
        coords.x >= 0 &&
            coords.y >= 0 &&
            coords.x < BOARD_SIZE as i32 &&
            coords.y < BOARD_SIZE as i32 &&
            self.is_on_edge[edge as usize][coords.x as usize][coords.y as usize]
    }

    /// Reference to all the coords on that edge.
    pub fn coords_on_edge(&self, edge: MapEdge) -> &[Coords; BOARD_SIZE / 2] {
        &self.edge_lists[edge as usize]
    }
}


/// Edge of the map.
#[repr(usize)]
#[derive(Copy, Clone, Eq, PartialEq, Ord, PartialOrd, Hash, IntoEnumIterator)]
pub enum MapEdge {
    TopRight = 0,
    TopLeft = 1,
    BottomLeft = 2,
    BottomRight = 3,
}