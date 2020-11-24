
use crate::{
    map::*,
    bounds::*,
    units::*,
    coords::*,
    grid::Grid,
};

use std::{
    u32,
    collections::VecDeque,
    cmp::Ordering,
    fmt::{self, Debug, Formatter, Write},
};

#[derive(Copy, Clone, Eq, PartialEq)]
enum Node {
    Invalid,
    Wall,
    Open {
        visited_idealness: bool,
        pathlength: Option<u32>,
    }
}

impl Debug for Node {
    fn fmt(&self, f: &mut Formatter) -> Result<(), fmt::Error> {
        match self {
            &Node::Invalid => {
                f.write_char('I')
            },
            &Node::Wall => {
                f.write_char('W')
            },
            &Node::Open {
                visited_idealness,
                pathlength
            } => {
                let mut string = String::new();
                if visited_idealness {
                    string.push('V');
                }
                if let Some(pathlength) = pathlength {
                    string.push_str(format!("{}", pathlength).as_ref());
                } else {
                    string.push('N');
                }
                f.write_str(string.as_ref())
            }
        }
    }
}

#[derive(Copy, Clone, Debug, Eq, PartialEq)]
enum LastDirection {
    Horizontal,
    Vertical
}

/// Pathfinding from a particular location will fail if that location is blocked by a wall.
#[derive(Clone, Debug)]
pub struct StartedAtWall(pub Coords, pub Unit<StructureUnitType>);

/// Attempt to pathfind from a particular tile on a map, to a certain map edge.
pub fn pathfind(board: &MapState, start: &MapTile, target: MapEdge) -> Result<Vec<Coords>, StartedAtWall> {
    // we cannot pathfind if we start at a wall
    if let Some(wall) = start.wall_unit() {
        return Err(StartedAtWall(start.coords(), wall));
    }

    // create the grid of nodes
    let mut grid = Grid::from_generator(|c| {
        board[c].if_valid()
            .map(|cell| {
                if cell.wall_unit().is_some() {
                    Node::Wall
                } else {
                    Node::Open {
                        visited_idealness: false,
                        pathlength: None
                    }
                }
            })
            .unwrap_or(Node::Invalid)
    });

    // perform the idealness search of the pocket
    let ideal_tiles = idealness_search(board, start, target, &mut grid);

    // validate the pocket
    validate(board, &mut grid, ideal_tiles);

    // get the path
    let path = get_path(start.coords(), target, &grid);

    Ok(path)
}

fn idealness_search(board: &MapState, start: &MapTile, target: MapEdge, grid: &mut Grid<Node>) -> Box<[Coords]> {
    // short circuit if start is on the edge
    if MAP_BOUNDS.is_on_edge(target, start.coords()) {
        return Box::new(MAP_BOUNDS.coords_on_edge(target).to_owned());
    }

    // set up variables
    let mut queue: VecDeque<Coords> = VecDeque::new();
    queue.push_back(start.coords());

    let mut best_tile = start.coords();
    let mut best_idealness = idealness_of(best_tile, target).unwrap();

    // BFS the pocket
    while let Some(curr) = queue.pop_front() {
        for neighbor in curr.neighbors().iter().cloned()
            .flat_map(|coord| board[coord].if_valid())
            .filter(|cell| cell.wall_unit().is_none())
            .map(|cell| cell.coords()) {

            // don't enter an infinite loop
            match grid.get_mut(neighbor).unwrap() {
                &mut Node::Open {
                    ref mut visited_idealness,
                    ..
                } => if *visited_idealness {
                    continue;
                } else {
                    *visited_idealness = true;
                },
                _ => unreachable!()
            };

            // short circuit if we've reached the edge
            if MAP_BOUNDS.is_on_edge(target, neighbor) {
                return Box::new(MAP_BOUNDS.coords_on_edge(target).to_owned());
            }

            // otherwise, possible replacement
            let neighbor_idealness = idealness_of(neighbor, target).unwrap();

            if neighbor_idealness > best_idealness {
                best_idealness = neighbor_idealness;
                best_tile = neighbor;
            }

            // and then, recursion
            queue.push_back(neighbor);
        }
    }

    // if we reach the edge without short circuiting, this pocket does not reach the edge
    Box::new([best_tile])
}

fn idealness_of(coords: Coords, target: MapEdge) -> Result<u32, Coords> {
    if MAP_BOUNDS.is_in_arena(coords) {
        if MAP_BOUNDS.is_on_edge(target, coords) {
            Ok(u32::MAX)
        } else {
            let coords = [coords.x as u32, coords.y as u32];
            let a = match target {
                MapEdge::TopLeft | MapEdge::TopRight =>
                    BOARD_SIZE as u32 * coords[1],
                MapEdge::BottomLeft | MapEdge::BottomRight =>
                    BOARD_SIZE as u32 * (BOARD_SIZE as u32 - 1 - coords[1]),
            };
            let b = match target {
                MapEdge::TopRight | MapEdge::BottomRight =>
                    coords[0],
                MapEdge::TopLeft | MapEdge::BottomLeft =>
                    BOARD_SIZE as u32 - 1 - coords[0]
            };
            Ok(a + b)
        }
    } else {
        Err(coords)
    }
}

fn validate(board: &MapState, grid: &mut Grid<Node>, ideal_tiles: Box<[Coords]>) {
    // set the first tiles' pathlength, mark them as validate-visited, and add them to a queue
    let mut queue: VecDeque<Coords> = VecDeque::new();
    for ideal_tile in ideal_tiles.iter().cloned() {
        match grid.get_mut(ideal_tile) {
            Some(&mut Node::Open {
                ref mut pathlength,
                ..
            }) => {
                *pathlength = Some(0);
                queue.push_back(ideal_tile);
            },
            Some(&mut Node::Wall) => (),
            bad => unreachable!("{:#?}", bad),
        };
    }

    // BFS the pocket
    while let Some(curr) = queue.pop_front() {
        let curr_pathlength = match grid.get(curr).unwrap() {
            &Node::Open {
                pathlength: Some(pathlength),
                ..
            } => pathlength,
            _ => unreachable!()
        };

        for neighbor in curr.neighbors().iter().cloned()
            .flat_map(|coord| board[coord].if_valid())
            .filter(|cell| cell.wall_unit().is_none())
            .map(|cell| cell.coords()) {

            match grid.get_mut(neighbor).unwrap() {
                &mut Node::Open {
                    ref mut pathlength,
                    ..
                } => {
                    // don't enter an infinite loop
                    if pathlength.is_none() {
                        // mark pathlength and recurse
                        *pathlength = Some(curr_pathlength + 1);
                        queue.push_back(neighbor);
                    }
                }
                _ => unreachable!()
            };
        }
    }
}

fn get_path(start: Coords, target: MapEdge, grid: &Grid<Node>) -> Vec<Coords> {
    let mut path = Vec::new();
    path.push(start);

    let mut curr = start;
    let mut curr_direction = None;

    // just follow the best path based on computed data until the end of the path is reached
    while match grid.get(curr).unwrap() {
        &Node::Open {
            pathlength: Some(pathlength),
            ..
        } => pathlength != 0,
        wrong => unreachable!("{:?} {:#?}", start, wrong),
    } {
        // get the next tile
        let next = next_move(curr, target, grid, curr_direction).unwrap();

        // update curr direction
        curr_direction = Some(direction_difference(curr, next).unwrap());

        // build the list
        curr = next;
        path.push(next);
    }

    path
}

fn next_move(curr: Coords, target: MapEdge, grid: &Grid<Node>, curr_direction: Option<LastDirection>) -> Option<Coords> {
    let possible: Vec<(Coords, u32)> = curr.neighbors().iter().cloned()
        .filter(|&neighbor| MAP_BOUNDS.is_in_arena(neighbor))
        .flat_map(|neighbor| match grid.get(neighbor) {
            Some(&Node::Open {
                pathlength: Some(pathlength),
                ..
            }) => Some((neighbor, pathlength)),
            _ => None
        })
        .collect();
    possible.iter().cloned()
        .map(|(_, pathlength)| pathlength)
        .min()
        .map(|best_pathlength| possible.iter().cloned()
            .filter(|&(_, pathlength)| pathlength == best_pathlength)
            .map(|(possible, _)| possible)
            .max_by(|&c1, &c2|
                compare_by_directional_correctness(curr, c1, c2, curr_direction, target)
                    .unwrap())
            .unwrap())
}

fn direction_difference(from: Coords, to: Coords) -> Result<LastDirection, [Coords; 2]> {
    if from.x == to.x && from.y != to.y {
        Ok(LastDirection::Vertical)
    } else if from.x != to.x && from.y == to.y {
        Ok(LastDirection::Horizontal)
    } else {
        Err([from, to])
    }
}

fn compare_by_directional_correctness(curr: Coords, c1: Coords, c2: Coords,
                                      curr_direction: Option<LastDirection>, target: MapEdge)
                                      -> Result<Ordering, [Coords; 2]> {

    let direction1 = direction_difference(curr, c1)?;
    let direction2 = direction_difference(curr, c2)?;

    match curr_direction {
        // rule 3: if this is the first movement, they will want to move vertically
        None => match (direction1, direction2) {
            (LastDirection::Vertical, LastDirection::Horizontal) => {
                Ok(Ordering::Greater)
            },
            (LastDirection::Horizontal, LastDirection::Vertical) => {
                Ok(Ordering::Less)
            },
            _ => unreachable!(),
        },
        Some(curr_direction) => {
            // rule 2: we want to change direction
            match (curr_direction != direction1, curr_direction != direction2) {
                (true, false) => {
                    return Ok(Ordering::Greater);
                },
                (false, true) => {
                    return Ok(Ordering::Less);
                },
                _ => (),
            };

            // rule 4: move towards target edge
            if match target {
                MapEdge::TopRight => c2.x > c1.x || c2.y > c1.y,
                MapEdge::TopLeft => c2.x < c1.x || c2.y > c1.y,
                MapEdge::BottomRight => c2.x > c1.x || c2.y < c1.y,
                MapEdge::BottomLeft => c2.x < c1.x || c2.y < c1.y,
            } {
                Ok(Ordering::Less)
            } else {
                Ok(Ordering::Greater)
            }
        }
    }
}