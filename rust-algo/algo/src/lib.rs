
extern crate serde;
extern crate serde_json;
#[macro_use]
extern crate serde_derive;
#[macro_use]
extern crate lazy_static;
#[macro_use]
pub extern crate enum_iterator;
extern crate num_traits;

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
}