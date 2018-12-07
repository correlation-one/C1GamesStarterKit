
use std::ops::*;
use std::fmt::{Debug, Formatter};
use std::fmt;

use num_traits::cast::ToPrimitive;
use serde::{Serialize, Deserialize, Serializer, Deserializer};
use serde::ser::SerializeSeq;
use serde::de::{Visitor, SeqAccess};

/// An XY pair of i32 coordinates.
/// De(serializes) as a tuple.
#[derive(Copy, Clone, Eq, PartialEq, Hash, Ord, PartialOrd)]
pub struct Coords {
    pub x: i32,
    pub y: i32,
}
impl Coords {
    /// Construct a new pair of coordinates from x and y.
    pub fn xy(x: i32, y: i32) -> Coords {
        Coords {
            x,
            y
        }
    }

    /// All 4 adjacent coordaintes.
    pub fn neighbors(self) -> [Self; 4] {
        [self + UP, self + DOWN, self + LEFT, self + RIGHT]
    }
}

/// Construct a new pair of coordinates from x and y.
pub fn xy(x: i32, y: i32) -> Coords {
    Coords::xy(x, y)
}

/// Macro version of coordinates constructor, for use in initializing constants.
#[macro_export]
macro_rules! xy {
    ($x:expr, $y:expr) => { Coords {
        x: $x,
        y: $y,
    }}
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

impl Debug for Coords {
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

impl Serialize for Coords {
    fn serialize<S>(&self, serializer: S) -> Result<<S as Serializer>::Ok, <S as Serializer>::Error> where
        S: Serializer {
        let mut seq = serializer.serialize_seq(Some(2))?;
        seq.serialize_element(&self.x)?;
        seq.serialize_element(&self.y)?;
        seq.end()
    }
}

impl<'de> Deserialize<'de> for Coords {
    fn deserialize<D>(deserializer: D) -> Result<Self, <D as Deserializer<'de>>::Error> where
        D: Deserializer<'de> {
        deserializer.deserialize_tuple(2, CoordVisitor)
    }
}
struct CoordVisitor;
impl<'de> Visitor<'de> for CoordVisitor {
    type Value = Coords;

    fn expecting(&self, f: &mut Formatter) -> Result<(), fmt::Error> {
        f.write_str("a tuple of two integers")
    }

    fn visit_seq<A>(self, mut seq: A) -> Result<<Self as Visitor<'de>>::Value, <A as SeqAccess<'de>>::Error> where
        A: SeqAccess<'de>, {
        let x: i32 = seq.next_element()?.unwrap();
        let y: i32 = seq.next_element()?.unwrap();
        Ok(Coords::xy(x, y))
    }
}