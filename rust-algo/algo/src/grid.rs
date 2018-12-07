
use coords::*;
use super::bounds::BOARD_SIZE;

use std::mem;
use std::ptr;
use std::fmt::{Debug, Formatter};
use std::fmt;

/// A grid of elements equal in size to the game board.
///
/// The grid is designed to be pretty-printed.
#[derive(Eq, PartialEq, Hash, Clone)]
pub struct Grid<T> {
    data: [[T; BOARD_SIZE]; BOARD_SIZE],
}
impl<T> Grid<T> {
    /// Construct a new grid, initializing each element from a function of the coordinates.
    pub fn new(mut generate: impl FnMut(Coords) -> T) -> Self {
        unsafe {
            let mut data: [[T; BOARD_SIZE]; BOARD_SIZE] = mem::uninitialized();
            for x in 0..BOARD_SIZE {
                for y in 0..BOARD_SIZE {
                    let elem = generate(Coords::from([x, y]));
                    ptr::write(&mut data[x][y], elem);
                }
            }
            Grid {
                data
            }
        }
    }

    /// Get the element at some coordinates, by reference.
    pub fn get(&self, coords: Coords) -> Option<&T> {
        self.data
            .get(coords.x as usize)
            .and_then(|column| column.get(coords.y as usize))
    }

    /// Get the elements at some coordinates, by mutable reference.
    pub fn get_mut(&mut self, coords: Coords) -> Option<&mut T> {
        self.data
            .get_mut(coords.x as usize)
            .and_then(|column| column.get_mut(coords.y as usize))
    }
}

impl<T: Debug> Debug for Grid<T> {
    fn fmt(&self, f: &mut Formatter) -> Result<(), fmt::Error> {
        let strings: Grid<String> =
            Grid::new(|c| format!("{:?}", self.get(c).unwrap()));

        let mut max_len = None;
        for x in 0..BOARD_SIZE {
            for y in 0..BOARD_SIZE {
                let len = strings.get(Coords::from([x, y])).unwrap()
                    .chars().collect::<Vec<char>>().len();
                if let Some(max) = max_len {
                    if len > max {
                        max_len = Some(len);
                    }
                } else {
                    max_len = Some(len);
                }
            }
        }
        let max_len = max_len.unwrap();

        let mut builder = String::new();
        builder.push_str("[\n");
        for y in (0..BOARD_SIZE).rev() {
            builder.push_str("  [");
            for x in 0..BOARD_SIZE {
                let mut elem = strings.get(Coords::from([x, y])).unwrap();
                builder.push_str(elem);
                let elem_len = elem.chars().collect::<Vec<char>>().len();
                for _ in 0..max_len - elem_len {
                    builder.push(' ');
                }
                if x < BOARD_SIZE - 1 {
                    builder.push_str(",");
                }
            }
            builder.push(']');
            if y > 0 {
                builder.push(',');
            }
            builder.push('\n');
        }
        builder.push(']');

        f.write_str(builder.as_ref())
    }
}