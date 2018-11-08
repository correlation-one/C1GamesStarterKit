package com.c1games.terminal.algo;

import com.google.gson.*;

import java.lang.reflect.Type;
import java.util.List;
import java.util.OptionalDouble;

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
    public interface UnitInformation {
        String getShorthand();
    }
    public interface RealUnitInformation {
        float cost();
    }
    public static final class WallUnitInformation implements UnitInformation, RealUnitInformation {
        public float damage;
        public float cost;
        public float getHitRadius;
        public String display;
        public float range;
        public String shorthand;
        public float stability;
        public OptionalDouble shieldAmount;

        public WallUnitInformation() {
            shieldAmount = OptionalDouble.empty();
        }

        @Override
        public String toString() {
            return "WallUnitInformation{" +
                    "damage=" + damage +
                    ", cost=" + cost +
                    ", getHitRadius=" + getHitRadius +
                    ", display='" + display + '\'' +
                    ", range=" + range +
                    ", shorthand='" + shorthand + '\'' +
                    ", stability=" + stability +
                    ", shieldAmount=" + shieldAmount +
                    '}';
        }

        @Override
        public String getShorthand() {
            return shorthand;
        }

        @Override
        public float cost() {
            return cost;
        }
    }
    public static final class DataUnitInformation implements UnitInformation, RealUnitInformation {
        public float damageI;
        public float damageToPlayer;
        public float cost;
        public float getHitRadius;
        public float damageF;
        public String display;
        public float range;
        public String shorthand;
        public float stability;
        public float speed;

        @Override
        public String toString() {
            return "DataUnitInformation{" +
                    "damageI=" + damageI +
                    ", damageToPlayer=" + damageToPlayer +
                    ", cost=" + cost +
                    ", getHitRadius=" + getHitRadius +
                    ", damageF=" + damageF +
                    ", display='" + display + '\'' +
                    ", range=" + range +
                    ", shorthand='" + shorthand + '\'' +
                    ", stability=" + stability +
                    ", speed=" + speed +
                    '}';
        }

        @Override
        public String getShorthand() {
            return shorthand;
        }

        @Override
        public float cost() {
            return cost;
        }
    }
    public static final class RemoveUnitInformation implements UnitInformation {
        public String display;
        public String shorthand;

        @Override
        public String toString() {
            return "RemoveUnitInformation{" +
                    "display='" + display + '\'' +
                    ", shorthand='" + shorthand + '\'' +
                    '}';
        }

        @Override
        public String getShorthand() {
            return shorthand;
        }
    }
    private static final class UnitInformationDeserializer implements com.google.gson.JsonDeserializer<UnitInformation> {
        @Override
        public UnitInformation deserialize(JsonElement jsonElement, Type type, JsonDeserializationContext jsonDeserializationContext) throws JsonParseException {
            try {
                JsonObject object = jsonElement.getAsJsonObject();
                if (object.has("damage")) {
                    return jsonDeserializationContext.deserialize(jsonElement, WallUnitInformation.class);
                } else if (object.has("damageI")) {
                    return jsonDeserializationContext.deserialize(jsonElement, DataUnitInformation.class);
                } else {
                    return jsonDeserializationContext.deserialize(jsonElement, RemoveUnitInformation.class);
                }
            } catch (Exception e) {
                throw new JsonParseException(e);
            }
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
        public float firewallBuildTime;

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
                    ", firewallBuildTime=" + firewallBuildTime +
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

    public static final Gson GSON;
    static {
        GSON = new GsonBuilder()
                .registerTypeAdapter(UnitInformation.class, new UnitInformationDeserializer())
                .registerTypeAdapter(OptionalDouble.class, new OptionalDoubleDeserializer())
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
