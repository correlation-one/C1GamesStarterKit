
use coords::*;
pub const BOARD_SIZE: usize = 28;

/// A struct holding calculated map-bound information.
pub struct MapBounds {
    pub is_on_edge: [[[bool; BOARD_SIZE]; BOARD_SIZE]; 4],
    pub edge_lists: [[Coords; BOARD_SIZE / 2]; 4],
    pub arena: [[bool; BOARD_SIZE]; BOARD_SIZE],
}
impl MapBounds {
    pub fn new() -> Self {
        let mut is_on_edge = [[[false; BOARD_SIZE]; BOARD_SIZE]; 4];
        let mut edge_lists = [[ORIGIN; BOARD_SIZE / 2]; 4];

        Self::populate(&mut is_on_edge, &mut edge_lists, MapEdge::TopRight,
                       |i| [BOARD_SIZE / 2 + i, BOARD_SIZE - 1 - i]
        );
        Self::populate(&mut is_on_edge, &mut edge_lists, MapEdge::TopLeft,
                       |i| [BOARD_SIZE / 2 - 1 - i, BOARD_SIZE - 1 - i]
        );
        Self::populate(&mut is_on_edge, &mut edge_lists, MapEdge::BottomLeft,
                       |i| [BOARD_SIZE / 2 - 1 - i, i]
        );
        Self::populate(&mut is_on_edge, &mut edge_lists, MapEdge::BottomRight,
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

    /// Construction helper function.
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

    /// Is the given coord in the arena?
    pub fn in_arena(&self, coords: Coords) -> bool {
        coords.x >= 0 &&
            coords.y >= 0 &&
            coords.x < BOARD_SIZE as i32 &&
            coords.y < BOARD_SIZE as i32 &&
            self.arena[coords.x as usize][coords.y as usize]
    }

    /// Is the given coord on the given edge?
    pub fn on_edge(&self, edge: MapEdge, coords: Coords) -> bool {
        coords.x >= 0 &&
            coords.y >= 0 &&
            coords.x < BOARD_SIZE as i32 &&
            coords.y < BOARD_SIZE as i32 &&
            self.is_on_edge[edge as usize][coords.x as usize][coords.y as usize]
    }

    /// Reference to all the coords on that edge.
    pub fn edge(&self, edge: MapEdge) -> &[Coords; BOARD_SIZE / 2] {
        &self.edge_lists[edge as usize]
    }
}

/// A static reference to the map bounds data.
lazy_static! {
    pub static ref MAP_BOUNDS: MapBounds = MapBounds::new();
}

/// An edge of the map.
#[repr(usize)]
#[derive(Copy, Clone, Eq, PartialEq, Hash, IntoEnumIterator)]
pub enum MapEdge {
    TopRight = 0,
    TopLeft = 1,
    BottomLeft = 2,
    BottomRight = 3,
}