
#[macro_use]
extern crate lazy_static;
extern crate serde;
extern crate serde_json;
extern crate enum_iterator;
extern crate num_enum;
extern crate num_traits;

#[macro_use]
pub mod messages;
pub mod units;
#[macro_use]
pub mod map;
pub mod bounds;
pub mod grid;
pub mod io;
pub mod gameloop;
pub mod pathfinding;
pub mod coords;

pub use enum_iterator::IntoEnumIterator;

/// Common re-exports.
pub mod prelude {
    pub use super::units::*;
    pub use super::map::*;
    pub use super::bounds::*;
    pub use super::io::*;
    pub use super::gameloop::*;
    pub use super::messages::{Config, PlayerId};
    pub use super::grid::Grid;
    pub use super::coords::*;
    pub use std::sync::Arc;
    pub use enum_iterator::IntoEnumIterator;
}