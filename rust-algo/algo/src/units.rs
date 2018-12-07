
/// Unit types in the game.

use super::messages::config::UnitInformation;

use enum_iterator::IntoEnumIterator;

use std::collections::HashMap;

/// Any unit type, including the remove type.
#[derive(Debug, Copy, Clone, Eq, PartialEq, PartialOrd, Ord, Hash, IntoEnumIterator)]
#[repr(u32)]
pub enum UnitType {
    Filter,
    Encryptor,
    Destructor,
    Ping,
    Emp,
    Scrambler,
    Remove,
}
impl UnitType {
    /// Attempt to convert to a FirewallUnitType.
    pub fn as_firewall(self) -> Option<FirewallUnitType> {
        match self {
            UnitType::Filter => Some(FirewallUnitType::Filter),
            UnitType::Encryptor => Some(FirewallUnitType::Encryptor),
            UnitType::Destructor => Some(FirewallUnitType::Destructor),
            _ => None
        }
    }

    /// Whether self is a FirewallUnitTYpe.
    pub fn is_firewall(self) -> bool {
        match self {
            UnitType::Filter | UnitType::Encryptor | UnitType::Destructor => true,
            _ => false
        }
    }

    /// Attempt to convert to an InfoUnitType.
    pub fn as_info(self) -> Option<InfoUnitType> {
        match self {
            UnitType::Ping => Some(InfoUnitType::Ping),
            UnitType::Emp => Some(InfoUnitType::Emp),
            UnitType::Scrambler => Some(InfoUnitType::Scrambler),
            _ => None
        }
    }

    /// Whether self is an InfoUnitType.
    pub fn is_info(self) -> bool {
        match self {
            UnitType::Ping | UnitType::Emp | UnitType::Scrambler => true,
            _ => false
        }
    }

    /// Whether self is a unit type which can be spawned.
    pub fn is_spawnable(self) -> bool {
        self.is_firewall() || self.is_info()
    }

    /// Attempt to convert to a SpawnableUnitType.
    pub fn as_spawnable(self) -> Option<SpawnableUnitType> {
        if let Some(info) = self.as_info() {
            Some(SpawnableUnitType::Info(info))
        } else if let Some(wall) = self.as_firewall() {
            Some(SpawnableUnitType::Firewall(wall))
        } else {
            None
        }
    }
}

/// A type of firewall unit.
#[derive(Debug, Copy, Clone, Eq, PartialEq, Hash, IntoEnumIterator)]
pub enum FirewallUnitType {
    Filter,
    Encryptor,
    Destructor,
}

impl Into<UnitType> for FirewallUnitType {
    fn into(self) -> UnitType {
        match self {
            FirewallUnitType::Filter => UnitType::Filter,
            FirewallUnitType::Encryptor => UnitType::Encryptor,
            FirewallUnitType::Destructor => UnitType::Destructor,
        }
    }
}

impl Into<SpawnableUnitType> for FirewallUnitType {
    fn into(self) -> SpawnableUnitType {
        SpawnableUnitType::Firewall(self)
    }
}

/// A type of info unit.
#[derive(Debug, Copy, Clone, Eq, PartialEq, Hash, IntoEnumIterator)]
pub enum InfoUnitType {
    Ping,
    Emp,
    Scrambler,
}

impl Into<UnitType> for InfoUnitType {
    fn into(self) -> UnitType {
        match self {
            InfoUnitType::Ping => UnitType::Ping,
            InfoUnitType::Emp => UnitType::Emp,
            InfoUnitType::Scrambler => UnitType::Scrambler,
        }
    }
}

impl Into<SpawnableUnitType> for InfoUnitType {
    fn into(self) -> SpawnableUnitType {
        SpawnableUnitType::Info(self)
    }
}

/// A unit-like struct which represents the remove unit type.
#[derive(Debug, Copy, Clone, Eq, PartialEq, Hash)]
pub struct RemoveUnitType;
impl Into<UnitType> for RemoveUnitType {
    fn into(self) -> UnitType {
        UnitType::Remove
    }
}

/// The unit types which can be spawned; a union if InfoUnitType and FirewallUnitType.
#[derive(Debug, Copy, Clone, Eq, PartialEq, Hash)]
pub enum SpawnableUnitType {
    Info(InfoUnitType),
    Firewall(FirewallUnitType),
}
impl SpawnableUnitType {
    /// Is this an InfoUnitType?
    pub fn is_info(&self) -> bool {
        match self {
            &SpawnableUnitType::Info(_) => true,
            &SpawnableUnitType::Firewall(_) => false,
        }
    }

    /// Is this a FirewallUnitType?
    pub fn is_firewall(&self) -> bool {
        match self {
            &SpawnableUnitType::Info(_) => false,
            &SpawnableUnitType::Firewall(_) => true,
        }
    }
}
impl Into<UnitType> for SpawnableUnitType {
    fn into(self) -> UnitType {
        match self {
            SpawnableUnitType::Info(unit_type) => unit_type.into(),
            SpawnableUnitType::Firewall(unit_type) => unit_type.into(),
        }
    }
}

/// Translations between unit types, integers, and shorthand strings.
pub struct UnitTypeAtlas {
    unit_information: [UnitInformation; 7],
    unit_type_lookup: HashMap<String, UnitType>,
}
impl UnitTypeAtlas {
    /// Construct a UnitTypeAtlas from the array of 7 UnitInformation found in the Config.
    pub fn new(unit_information: [UnitInformation; 7]) -> Self {
        let mut lookup = HashMap::new();
        for unit_type in UnitType::into_enum_iter() {
            lookup.insert(unit_information[unit_type as usize].shorthand().to_owned(),
                          unit_type);
        }
        UnitTypeAtlas {
            unit_information,
            unit_type_lookup: lookup
        }
    }

    /// Convert a unit type integer into a UnitType.
    pub fn type_from_u32(&self, n: u32) -> Option<UnitType> {
        UnitType::into_enum_iter().nth(n as usize)
    }

    /// Convert a unit type shorthand into a UnitType.
    pub fn type_from_shorthand(&self, shorthand: &String) -> Option<UnitType> {
        self.unit_type_lookup.get(shorthand).cloned()
    }

    /// Convert a unit type into its shorthand.
    pub fn type_into_shorthand(&self, unit_type: UnitType) -> &String {
        self.unit_information[unit_type as u32 as usize].shorthand()
    }
}

