
use crate::{
    messages::{FrameData, Config, frame},
    map::{
        MapState,
        parse::{
            self,
            MapParseError,
        },
    },
    units::UnitTypeAtlas,
};
use std::{
    io::{stdin, BufRead},
    sync::Arc,
};
use serde::Deserialize;
use serde_json;

/// A IO object for receiving and storing the Config from the game engine, creating from the Config
/// and UnitTypeAtlas, and then receiving all subsequent frames.
pub struct GameDataReader {
    config: Option<(Arc<Config>, Arc<UnitTypeAtlas>)>,
}

fn deser_json<'a, T: Deserialize<'a>>(string: &'a str) -> Result<T, serde_json::Error> {
    serde_json::from_str(string)
}

impl GameDataReader {
    pub fn new() -> Self {
        GameDataReader {
            config: None
        }
    }

    /// Get the config, and unit type atlas, waiting for it if necessary.
    pub fn config(&mut self) -> Result<(Arc<Config>, Arc<UnitTypeAtlas>), serde_json::Error> {
        match &mut self.config {
            &mut Some(ref mut config) => Ok(config.clone()),
            config_holder => {
                let stdin = stdin();
                let lock = stdin.lock();
                let mut lines = lock.lines();
                let line = lines.next();
                let line = line.unwrap().unwrap();
                let config: Arc<Config> = Arc::new(deser_json(line.as_ref())?);
                let atlas = Arc::new(UnitTypeAtlas::new(config.unit_information.clone()));
                *config_holder = Some((config.clone(), atlas.clone()));
                Ok((config, atlas))
            }
        }
    }

    /// Wait for the next frame. If necessary, wait for the config.
    pub fn next_frame_any_type(&mut self) -> Result<Box<FrameData>, serde_json::Error> {
        // ensure that the first line we read is the config, or we will enter a bad state
        self.config()?;

        let stdin = stdin();
        let line = stdin.lock().lines().next().unwrap().unwrap();

        deser_json(line.as_ref())
            .map(|data| Box::new(data))
    }

    /// Get the next frame of the deploy phase.
    pub fn next_turn_frame(&mut self) -> Result<Box<FrameData>, serde_json::Error> {
        loop {
            let frame = self.next_frame_any_type()?;
            if frame.turn_info.phase == frame::Phase::Deploy {
                return Ok(frame);
            }
        }
    }

    /// Get the next frame of the deploy phase, and then use it in conjunction with the Config
    /// and UnitTypeAtlas to attempt to parse a Map.
    pub fn next_turn_map(&mut self) -> Result<MapState, MapParseError> {
        let (config, atlas) = self.config()
            .map_err(|e| MapParseError::DeserializeError(e))?;
        let frame = self.next_turn_frame()
            .map_err(|e| MapParseError::DeserializeError(e))?;
        parse::parse_frame(config, frame, atlas)
    }
}