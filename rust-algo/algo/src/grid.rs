
use crate::{
    coords::*,
    bounds::BOARD_SIZE,
};

use std::{
    mem::{MaybeUninit, ManuallyDrop},
    fmt::{self, Debug, Formatter},
    ops::{Index, IndexMut},
    ptr,
};

/// A grid of elements equal in size to the game board.
///
/// This type will pretty-print.
pub struct Grid<T> {
    data: [[T; BOARD_SIZE]; BOARD_SIZE],
}

impl<T> Grid<T> {
    /// Build a grid, using a callback to construct each element.
    pub fn from_generator(mut generator: impl FnMut(Coords) -> T) -> Self {
        unsafe {
            let mut data: ManuallyDrop<MaybeUninit<[[T; BOARD_SIZE]; BOARD_SIZE]>> =
                ManuallyDrop::new(MaybeUninit::uninit());

            for x in 0..BOARD_SIZE {
                for y in 0..BOARD_SIZE {
                    let value = generator(xy(x as i32, y as i32));

                    let addr: *mut [[T; BOARD_SIZE]; BOARD_SIZE] = data.as_mut_ptr();
                    let addr: *mut [T; BOARD_SIZE] = addr as _;
                    let addr: *mut [T; BOARD_SIZE] = addr.offset(x as isize);
                    let addr: *mut T = addr as _;
                    let addr: *mut T = addr.offset(y as isize);

                    ptr::write(addr, value);
                }
            }

            let data: [[T; BOARD_SIZE]; BOARD_SIZE] =
                MaybeUninit::assume_init(ManuallyDrop::into_inner(data));

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

impl<T> Index<Coords> for Grid<T> {
    type Output = T;

    fn index(&self, index: Coords) -> &T {
        self.get(index)
            .unwrap_or_else(|| panic!("index out of bounds: {}", index))
    }
}

impl<T> IndexMut<Coords> for Grid<T> {
    fn index_mut(&mut self, index: Coords) -> &mut T {
        self.get_mut(index)
            .unwrap_or_else(|| panic!("index out of bounds: {}", index))
    }
}

impl<T: Debug> Debug for Grid<T> {
    fn fmt(&self, f: &mut Formatter) -> Result<(), fmt::Error> {
        let strings: Grid<String> =
            Grid::from_generator(|c| format!("{:?}", self.get(c).unwrap()));

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
                let elem = strings.get(Coords::from([x, y])).unwrap();
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