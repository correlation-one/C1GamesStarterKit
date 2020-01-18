
/// Implement Deserialize that translates integer
/// constants to enum variants.
macro_rules! serde_enum_from_int {
    ($type:ty, {
        $(
            $int:expr => $variant:expr
        ),* $(,)?
    })=>{

        impl<'de> serde::de::Deserialize<'de> for $type {
            fn deserialize<D>(d: D) -> Result<Self, D::Error>
            where
                D: serde::de::Deserializer<'de>
            {
                use serde::de::{self, Visitor};
                use std::fmt::{self, Formatter};

                struct V;
                impl<'de2> Visitor<'de2> for V {
                    type Value = $type;

                    fn expecting(&self, f: &mut Formatter) -> fmt::Result {
                        let vec = vec![$($int),*];
                        f.write_str(&format!("integer in the set {:?}", vec))
                    }

                    fn visit_u64<E>(self, n: u64) -> Result<$type, E>
                    where
                        E: de::Error
                    {
                        match n {
                            $(
                            $int => Ok($variant),
                            )*
                            n => Err(E::custom(format!("invalid integer: {}", n)))
                        }
                    }
                }

                d.deserialize_u64(V)
            }
        }

    };
}

/// Allows implementation of `Deserialize` through a delegate
/// data model type, which this type then converts from.
pub trait DeserializeAs: Sized {
    type Model: for<'de> serde::de::Deserialize<'de>;

    fn from_model(model: Self::Model) -> Self;
}

/// Implement `Serialize` for a type by delegating to its
/// implementation of `DeserializeAs`.
macro_rules! deser_as {
    ($t:ty)=>{
        impl<'de> serde::de::Deserialize<'de> for $t {
            fn deserialize<D>(d: D) -> Result<Self, D::Error>
            where
                D: serde::de::Deserializer<'de>
            {
                use $crate::messages::serde_util::DeserializeAs;

                let model = <$t as DeserializeAs>::Model::deserialize(d)?;
                Ok(DeserializeAs::from_model(model))
            }
        }
    };
}


/// Allows implementation of `Serialize` through a delegate
/// data model type, which this type first converts into.
pub trait SerializeAs: Sized {
    type Model: serde::ser::Serialize;

    fn to_model(&self) -> Self::Model;
}

/// Implement `Serialize` for a type by delegating to its
/// implementation of `SerializeAs`.
macro_rules! ser_as {
    ($t:ty)=>{
        impl serde::ser::Serialize for $t {
            fn serialize<S>(&self, s: S) -> Result<S::Ok, S::Error>
            where
                S: Serializer,
            {
                use $crate::messages::serde_util::SerializeAs;

                let model = SerializeAs::to_model(self);
                <$t as SerializeAs>::Model::serialize(&model, s)
            }
        }
    }
}


/// Implement `DeserializeAs` for a struct, by directly
/// mirroring its named fields into a tuple.
macro_rules! deser_as_tuple {
    ($struct_ty:ident, (
        $(
            $field:ident: $field_ty:ty
        ),* $(,)?
    ))=>{
        impl $crate::messages::serde_util::DeserializeAs for $struct_ty {
            type Model = (
                $($field_ty,)*
            );

            fn from_model(model: Self::Model) -> Self {
                let (
                    $( $field, )*
                ) = model;

                $struct_ty {
                    $( $field, )*
                }
            }
        }

        deser_as!($struct_ty);
    }
}

/// An integer which can deserialize from a float.
#[derive(Copy, Clone, Debug)]
pub struct RoundNumber(f64);

impl<'de> serde::de::Deserialize<'de> for RoundNumber {
    fn deserialize<D>(d: D) -> Result<Self, D::Error>
        where
            D: serde::de::Deserializer<'de>
    {
        use serde::de::{Error, Visitor};
        use std::fmt::{self, Formatter};

        struct V;
        impl<'de2> Visitor<'de2> for V {
            type Value = RoundNumber;

            fn expecting(&self, f: &mut Formatter) -> fmt::Result {
                f.write_str("a round number")
            }

            fn visit_i64<E>(self, v: i64) -> Result<Self::Value, E>
            where
                E: Error,
            {
                Ok(RoundNumber::new(v))
            }

            fn visit_u64<E>(self, v: u64) -> Result<Self::Value, E>
            where
                E: Error,
            {
                Ok(RoundNumber::new(v as i64))
            }

            fn visit_f64<E>(self, v: f64) -> Result<Self::Value, E>
            where
                E: Error,
            {
                if v % 1.0 == 0.0 {
                    Ok(RoundNumber::new(v as i64))
                } else {
                    Err(E::custom(&format!("float is not round: {}", v)))
                }
            }
        }

        d.deserialize_any(V)
    }
}
impl RoundNumber {
    pub fn new(n: i64) -> Self {
        RoundNumber(n as f64)
    }

    pub fn int(self) -> i64 {
        self.0 as i64
    }
}