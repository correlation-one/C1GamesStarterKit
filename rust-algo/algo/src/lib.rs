#[macro_use]
extern crate lazy_static;
extern crate enum_iterator;
extern crate num_enum;
extern crate num_traits;
extern crate serde;
extern crate serde_json;

#[macro_use]
pub mod messages;
pub mod units;
#[macro_use]
pub mod map;
pub mod bounds;
pub mod coords;
pub mod gameloop;
pub mod grid;
pub mod io;
pub mod pathfinding;

pub use enum_iterator::IntoEnumIterator;

/// Common re-exports.
pub mod prelude {
    pub use super::bounds::*;
    pub use super::coords::*;
    pub use super::gameloop::*;
    pub use super::grid::Grid;
    pub use super::io::*;
    pub use super::map::*;
    pub use super::messages::{Config, PlayerId};
    pub use super::units::*;
    pub use enum_iterator::IntoEnumIterator;
    pub use std::sync::Arc;
}
