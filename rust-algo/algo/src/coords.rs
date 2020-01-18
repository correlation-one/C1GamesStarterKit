
use crate::{
    messages::serde_util::{
        SerializeAs,
        DeserializeAs,
        RoundNumber,
    },
    bounds::{MAP_BOUNDS, MapEdge},
};
use std::{
    ops::*,
    fmt::{self, Debug, Display, Formatter}
};

use num_traits::cast::ToPrimitive;
use serde::Serializer;

/// An XY pair of i32 coordinates.
///
/// De(serializes) as a tuple.
#[derive(Copy, Clone, Eq, PartialEq, Ord, PartialOrd, Hash)]
pub struct Coords {
    pub x: i32,
    pub y: i32,
}

impl Coords {
    /// Construct a new pair of coordinates from x and y.
    pub const fn xy(x: i32, y: i32) -> Coords {
        Coords { x, y }
    }

    /// All 4 adjacent coordinates.
    pub fn neighbors(self) -> [Self; 4] {
        [self + UP, self + DOWN, self + LEFT, self + RIGHT]
    }

    /// Is this coord in the `bounds::BOARD_SIZE` arena?
    pub fn is_in_arena(self) -> bool {
        MAP_BOUNDS.is_in_arena(self)
    }

    /// Is this coord on the given edge of `bounds::BOARD_SIZE`?
    pub fn is_on_edge(self, edge: MapEdge) -> bool {
        MAP_BOUNDS.is_on_edge(edge, self)
    }
}

/// Construct a new pair of coordinates from x and y.
pub const fn xy(x: i32, y: i32) -> Coords {
    Coords::xy(x, y)
}

/// Macro version of coordinates constructor, for use in initializing constants.
#[macro_export]
macro_rules! xy {
    ($x:expr, $y:expr)=>{ Coords {
        x: $x,
        y: $y,
    }};
}

/// <0, 0> coordinate constant.
pub const ORIGIN: Coords = Coords { x: 0, y: 0 };
/// <0, 1> coordinate constant.
pub const UP: Coords = Coords { x: 0, y: 1 };
/// <0, -1> coordinate constant.
pub const DOWN: Coords = Coords { x: 0, y: -1 };
/// <-1, 1> coordinate constant.
pub const LEFT: Coords = Coords { x: -1, y: 0 };
/// <1, 0> coordinate constant.
pub const RIGHT: Coords = Coords { x: 1, y: 0 };

// ==== boilerplate implementation ====

impl SerializeAs for Coords {
    type Model = (i32, i32);

    fn to_model(&self) -> Self::Model {
        (self.x, self.y)
    }
}

impl DeserializeAs for Coords {
    type Model = (RoundNumber, RoundNumber);

    fn from_model((x, y): Self::Model) -> Self {
        xy(x.int() as i32, y.int() as i32)
    }
}

ser_as!(Coords);
deser_as!(Coords);


impl Debug for Coords {
    fn fmt(&self, f: &mut Formatter) -> Result<(), fmt::Error> {
        f.write_str(&format!("[{},{}]", self.x, self.y))
    }
}

impl Display for Coords {
    fn fmt(&self, f: &mut Formatter) -> Result<(), fmt::Error> {
        f.write_str(&format!("<{},{}>", self.x, self.y))
    }
}


impl<I: ToPrimitive> From<[I; 2]> for Coords {
    fn from(components: [I; 2]) -> Self {
        Coords::xy(
            components[0].to_i32().unwrap(),
            components[1].to_i32().unwrap(),
        )
    }
}

impl<I: ToPrimitive> From<(I, I)> for Coords {
    fn from(components: (I, I)) -> Self {
        Coords::xy(
            components.0.to_i32().unwrap(),
            components.1.to_i32().unwrap(),
        )
    }
}

impl<I: ToPrimitive> Index<I> for Coords {
    type Output = i32;

    fn index(&self, index: I) -> &i32 {
        match index.to_u8() {
            Some(0) => &self.x,
            Some(1) => &self.y,
            oob => panic!("coord index out of bounds: {:?}", oob),
        }
    }
}

impl<I: ToPrimitive> IndexMut<I> for Coords {
    fn index_mut(&mut self, index: I) -> &mut i32 {
        match index.to_u8() {
            Some(0) => &mut self.x,
            Some(1) => &mut self.y,
            oob => panic!("coord index out of bounds: {:?}", oob),
        }
    }
}

// ==== arithmetic implementations ====

impl Add for Coords {
    type Output = Self;

    fn add(self, rhs: Self) -> Self {
        Self::xy(self.x + rhs.x, self.y + rhs.y)
    }
}

impl AddAssign for Coords {
    fn add_assign(&mut self, rhs: Self) {
        self.x += rhs.x;
        self.y += rhs.y;
    }
}

impl Sub for Coords {
    type Output = Self;

    fn sub(self, rhs: Self) -> Self {
        Self::xy(self.x - rhs.x, self.y - rhs.y)
    }
}

impl SubAssign for Coords {
    fn sub_assign(&mut self, rhs: Self) {
        self.x -= rhs.x;
        self.y -= rhs.y;
    }
}

impl Mul<i32> for Coords {
    type Output = Self;

    fn mul(self, rhs: i32) -> Self {
        Self::xy(self.x * rhs, self.y * rhs)
    }
}

impl MulAssign<i32> for Coords {
    fn mul_assign(&mut self, rhs: i32) {
        self.x *= rhs;
        self.y *= rhs;
    }
}

impl Div<i32> for Coords {
    type Output = Self;

    fn div(self, rhs: i32) -> Self {
        Self::xy(self.x / rhs, self.y / rhs)
    }
}

impl DivAssign<i32> for Coords {
    fn div_assign(&mut self, rhs: i32) {
        self.x /= rhs;
        self.y /= rhs;
    }
}

impl Rem<i32> for Coords {
    type Output = Self;

    fn rem(self, rhs: i32) -> Self {
        Self::xy(self.x % rhs, self.y % rhs)
    }
}

impl RemAssign<i32> for Coords {
    fn rem_assign(&mut self, rhs: i32) {
        self.x %= rhs;
        self.y %= rhs;
    }
}

