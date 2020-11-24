package com.c1games.terminal.algo;

import com.c1games.terminal.algo.map.Unit;
import com.c1games.terminal.algo.serialization.JsonDeserializeEnumFromInt;
import com.c1games.terminal.algo.units.UnitType;
import com.google.gson.*;

import java.lang.reflect.Type;
import java.util.List;
import java.util.Optional;
import java.util.OptionalDouble;
import java.util.OptionalInt;

/**
 * GSON-based representation of the deserialized config file.
 */
public final class Config {
    public static final class Debug {
        public boolean printMapString;
        public boolean printTStrings;
        public boolean printActStrings;
        public boolean printHitStrings;
        public boolean printPlayerInputStrings;
        public boolean printBotErrors;
        public boolean printPlayerGetHitStrings;

        @Override
        public String toString() {
            return "Debug{" +
                    "printMapString=" + printMapString +
                    ", printTStrings=" + printTStrings +
                    ", printActStrings=" + printActStrings +
                    ", printHitStrings=" + printHitStrings +
                    ", printPlayerInputStrings=" + printPlayerInputStrings +
                    ", printBotErrors=" + printBotErrors +
                    ", printPlayerGetHitStrings=" + printPlayerGetHitStrings +
                    '}';
        }
    }
    public Debug debug;
    public interface UnitInformationDisplay {
        String getShorthand();
        String getDisplay();
    }
    public interface RealUnitInformation {
        float[] cost();
    }
    public static final class UnitInformation implements UnitInformationDisplay, RealUnitInformation {
        public OptionalDouble attackDamageTower = OptionalDouble.empty();; //structure
        public OptionalDouble attackDamageWalker = OptionalDouble.empty(); //mobile units
        public OptionalDouble attackRange = OptionalDouble.empty();
        public OptionalDouble getHitRadius = OptionalDouble.empty();
        public OptionalInt unitCategory = OptionalInt.empty();

        public OptionalDouble shieldPerUnit = OptionalDouble.empty();
        public OptionalDouble shieldRange = OptionalDouble.empty();
        public OptionalDouble shieldBonusPerY = OptionalDouble.empty();
        public OptionalDouble shieldDecay = OptionalDouble.empty();

        public OptionalDouble startHealth = OptionalDouble.empty();

        public OptionalDouble speed = OptionalDouble.empty();

        public OptionalDouble cost1 = OptionalDouble.empty(); //SP
        public OptionalDouble cost2 = OptionalDouble.empty(); //MP

        public Optional<String> display = Optional.empty();
        public Optional<String> shorthand = Optional.empty();

        public Optional<String> icon = Optional.empty();
        public OptionalDouble iconxScale = OptionalDouble.empty();
        public OptionalDouble iconyScale = OptionalDouble.empty();

        public Optional<UnitInformation> upgrade = Optional.empty(); // stats that will change when you upgrade
        // Not this only covers most commonly used information about a unit,
        // there are missing variables like selfDestructRange that shouldn't be needed for most strategies and leave you to add.

        public UnitInformation() {

        }

        /**
         * Is a deep copy
         * @param copyFrom
         */
        public UnitInformation(UnitInformation copyFrom) {
            copyFrom.attackDamageTower.ifPresent(newVal -> this.attackDamageTower = OptionalDouble.of(newVal));
            copyFrom.attackDamageWalker.ifPresent(newVal -> this.attackDamageWalker = OptionalDouble.of(newVal));
            copyFrom.attackRange.ifPresent(newVal -> this.attackRange = OptionalDouble.of(newVal));
            copyFrom.getHitRadius.ifPresent(newVal -> this.getHitRadius = OptionalDouble.of(newVal));
            copyFrom.unitCategory.ifPresent(newVal -> this.unitCategory = OptionalInt.of(newVal));

            copyFrom.shieldPerUnit.ifPresent(newVal -> this.shieldPerUnit = OptionalDouble.of(newVal));
            copyFrom.shieldRange.ifPresent(newVal -> this.shieldRange = OptionalDouble.of(newVal));
            copyFrom.shieldBonusPerY.ifPresent(newVal -> this.shieldBonusPerY = OptionalDouble.of(newVal));
            copyFrom.shieldDecay.ifPresent(newVal -> this.shieldDecay = OptionalDouble.of(newVal));

            copyFrom.startHealth.ifPresent(newVal -> this.startHealth = OptionalDouble.of(newVal));
            copyFrom.speed.ifPresent(newVal -> this.speed = OptionalDouble.of(newVal));
            copyFrom.cost1.ifPresent(newVal -> this.cost1 = OptionalDouble.of(newVal));
            copyFrom.cost2.ifPresent(newVal -> this.cost2 = OptionalDouble.of(newVal));

            copyFrom.icon.ifPresent(newVal -> this.icon = Optional.of(newVal));
            copyFrom.iconxScale.ifPresent(newVal -> this.iconxScale = OptionalDouble.of(newVal));
            copyFrom.iconyScale.ifPresent(newVal -> this.iconyScale = OptionalDouble.of(newVal));

            copyFrom.upgrade.ifPresent(newVal -> this.upgrade = Optional.of(new UnitInformation(newVal)));

            copyFrom.display.ifPresent(newVal -> this.display = Optional.of(newVal));
            copyFrom.shorthand.ifPresent(newVal -> this.shorthand = Optional.of(newVal));
        }

        @Override
        public String toString() {
            return "UnitInformation{" +
                    "icon='" + icon + "''" + 
                    "iconxScale=" + iconxScale +
                    "iconyScale=" + iconyScale +
                    "display='" + display + "'" +
                    "shorthand='" + shorthand + "'" +
                    "attackDamageTower=" + attackDamageTower +
                    "attackDamageWalker=" + attackDamageWalker +
                    "attackRange=" + attackRange +
                    "getHitRadius=" + getHitRadius +
                    "unitCategory=" + unitCategory +
                    "shieldPerUnit=" + shieldPerUnit +
                    "shieldRange=" + shieldRange +
                    "shieldBonusPerY=" + shieldBonusPerY +
                    "shieldDecay=" + shieldDecay +
                    "startHealth=" + startHealth +
                    "speed=" + speed +
                    "cost1=" + cost1 +
                    "cost2=" + cost2 +
                    "upgrade=\n" + upgrade +
                    '}';
        }

        /**
         * This function should only be called by Unit.java
         * Because this should never be called on the unit information in the config directly but on an instance copy of this in a unit.
         * Otherwise you will modify the default values of a unit.
         */
        public void upgrade() {
            if (upgrade.get() != null) {

                upgrade.get().attackDamageTower.ifPresent(newVal -> this.attackDamageTower = OptionalDouble.of(newVal));
                upgrade.get().attackDamageWalker.ifPresent(newVal -> this.attackDamageWalker = OptionalDouble.of(newVal));
                upgrade.get().attackRange.ifPresent(newVal -> this.attackRange = OptionalDouble.of(newVal));
                upgrade.get().getHitRadius.ifPresent(newVal -> this.getHitRadius = OptionalDouble.of(newVal));
                upgrade.get().unitCategory.ifPresent(newVal -> this.unitCategory = OptionalInt.of(newVal));

                upgrade.get().shieldPerUnit.ifPresent(newVal -> this.shieldPerUnit = OptionalDouble.of(newVal));
                upgrade.get().shieldRange.ifPresent(newVal -> this.shieldRange = OptionalDouble.of(newVal));
                upgrade.get().shieldBonusPerY.ifPresent(newVal -> this.shieldBonusPerY = OptionalDouble.of(newVal));
                upgrade.get().shieldDecay.ifPresent(newVal -> this.shieldDecay = OptionalDouble.of(newVal));

                upgrade.get().startHealth.ifPresent(newVal -> this.startHealth = OptionalDouble.of(newVal));
                upgrade.get().speed.ifPresent(newVal -> this.speed = OptionalDouble.of(newVal));
                upgrade.get().cost1.ifPresent(newVal -> this.cost1 = OptionalDouble.of(newVal + (this.cost1.isPresent() ? this.cost1.getAsDouble() : 0) ));
                upgrade.get().cost2.ifPresent(newVal -> this.cost2 = OptionalDouble.of(newVal + (this.cost2.isPresent() ? this.cost2.getAsDouble() : 0) ));

                this.upgrade = Optional.empty();
            }
        };

        @Override
        public String getShorthand() {
            return shorthand.orElse(null);
        }
        @Override
        public String getDisplay() {
            return display.orElse(null);
        }

        @Override
        public float[] cost() {
            float[] ret = new float[2];
            cost1.ifPresent(c -> ret[0] = (float)c);
            cost2.ifPresent(c -> ret[1] = (float)c);
            return ret;
        }
    }

    public List<UnitInformation> unitInformation;
    public static final class Resources {
        public float turnIntervalForBitCapSchedule;
        public float turnIntervalForBitSchedule;
        public float bitRampBitCapGrowthRate;
        public float roundStartBitRamp;
        public float bitGrowthRate;
        public float startingHP;
        public float maxBits;
        public float bitsPerRound;
        public float coresPerRound;
        public float coresForPlayerDamage;
        public float startingBits;
        public float bitDecayPerRound;
        public float startingCores;

        @Override
        public String toString() {
            return "Resources{" +
                    "turnIntervalForBitCapSchedule=" + turnIntervalForBitCapSchedule +
                    ", turnIntervalForBitSchedule=" + turnIntervalForBitSchedule +
                    ", bitRampBitCapGrowthRate=" + bitRampBitCapGrowthRate +
                    ", roundStartBitRamp=" + roundStartBitRamp +
                    ", bitGrowthRate=" + bitGrowthRate +
                    ", startingHP=" + startingHP +
                    ", maxBits=" + maxBits +
                    ", bitsPerRound=" + bitsPerRound +
                    ", coresPerRound=" + coresPerRound +
                    ", coresForPlayerDamage=" + coresForPlayerDamage +
                    ", startingBits=" + startingBits +
                    ", bitDecayPerRound=" + bitDecayPerRound +
                    ", startingCores=" + startingCores +
                    '}';
        }
    }
    public Resources resources;
    public static final class Mechanics {
        public float basePlayerHealthDamage;
        public float damageGrowthBasedOnY;
        public boolean bitsCanStackOnDeployment;
        public float destroyOwnUnitRefund;
        public boolean destroyOwnUnitsEnabled;
        public int stepsRequiredSelfDestruct;
        public float selfDestructRadius;
        public float shieldDecayPerFrame;
        public float meleeMultiplier;
        public float destroyOwnUnitDelay;
        public boolean rerouteMidRound;
        public float structureBuildTime;

        @Override
        public String toString() {
            return "Mechanics{" +
                    "basePlayerHealthDamage=" + basePlayerHealthDamage +
                    ", damageGrowthBasedOnY=" + damageGrowthBasedOnY +
                    ", bitsCanStackOnDeployment=" + bitsCanStackOnDeployment +
                    ", destroyOwnUnitRefund=" + destroyOwnUnitRefund +
                    ", destroyOwnUnitsEnabled=" + destroyOwnUnitsEnabled +
                    ", stepsRequiredSelfDestruct=" + stepsRequiredSelfDestruct +
                    ", selfDestructRadius=" + selfDestructRadius +
                    ", shieldDecayPerFrame=" + shieldDecayPerFrame +
                    ", meleeMultiplier=" + meleeMultiplier +
                    ", destroyOwnUnitDelay=" + destroyOwnUnitDelay +
                    ", rerouteMidRound=" + rerouteMidRound +
                    ", structureBuildTime=" + structureBuildTime +
                    '}';
        }
    }
    public Mechanics mechanics;

    private static final class OptionalDoubleDeserializer implements JsonDeserializer<OptionalDouble> {
        @Override
        public OptionalDouble deserialize(JsonElement jsonElement, Type type, JsonDeserializationContext jsonDeserializationContext) throws JsonParseException {
            try {
                return OptionalDouble.of(jsonElement.getAsDouble());
            } catch (Exception e) {
                throw new JsonParseException(e);
            }
        }
    }
    private static final class OptionalIntDeserializer implements JsonDeserializer<OptionalInt> {
        @Override
        public OptionalInt deserialize(JsonElement jsonElement, Type type, JsonDeserializationContext jsonDeserializationContext) throws JsonParseException {
            try {
                try {
                    return OptionalInt.of(jsonElement.getAsInt());
                } catch (UnsupportedOperationException e) {
                    return OptionalInt.of((int) jsonElement.getAsDouble());
                }
            } catch (Exception e) {
                throw new JsonParseException(e);
            }
        }
    }
    private static final class OptionalDeserializer implements JsonDeserializer<Optional> {
        @Override
        public Optional deserialize(JsonElement jsonElement, Type type, JsonDeserializationContext jsonDeserializationContext) throws JsonParseException {
            try {
                try {
                    if (jsonElement.isJsonObject()) {
                        return Optional.of(jsonDeserializationContext.deserialize(jsonElement, UnitInformation.class));
                    } else {
                        return Optional.of(jsonElement.getAsString());
                    }
                } catch (UnsupportedOperationException e) {
                    return Optional.of(jsonElement.getAsString());
                }
            } catch (Exception e) {
                throw new JsonParseException(e);
            }
        }
    }

    public static final Gson GSON;
    static {
        GSON = new GsonBuilder()
                .registerTypeAdapter(OptionalDouble.class, new OptionalDoubleDeserializer())
                .registerTypeAdapter(OptionalInt.class, new OptionalIntDeserializer())
                .registerTypeAdapter(Optional.class, new OptionalDeserializer())
                .create();
    }

    @Override
    public String toString() {
        return "Config{" +
                "debug=" + debug +
                ", unitInformation=" + unitInformation +
                ", resources=" + resources +
                ", mechanics=" + mechanics +
                '}';
    }
}
