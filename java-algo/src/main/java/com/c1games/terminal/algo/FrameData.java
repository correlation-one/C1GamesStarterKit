package com.c1games.terminal.algo;

import com.c1games.terminal.algo.serialization.*;
import com.c1games.terminal.algo.units.UnitType;
import com.c1games.terminal.algo.units.UnitTypeAtlas;
import com.google.gson.*;

import java.util.ArrayList;
import java.util.List;

/**
 * GSON-based representation of the data received every frame denoting the game state.
 */
public class FrameData {
    public static final class TurnInfo {
        public enum Phase {
            Deploy,
            Action,
            EndGame;
        }
        public Phase phase;
        public int turnNumber;
        public int actionPhaseFrameNumber;

        @Override
        public String toString() {
            return "TurnInfo{" +
                    "phase=" + phase +
                    ", turnNumber=" + turnNumber +
                    ", actionPhaseFrameNumber=" + actionPhaseFrameNumber +
                    '}';
        }
    }
    public TurnInfo turnInfo;
    public static final class PlayerStats {
        public float integrity;
        public float cores;
        public float bits;
        public float timeTakenLastTurnMillis;

        @Override
        public String toString() {
            return "PlayerStats{" +
                    "integrity=" + integrity +
                    ", cores=" + cores +
                    ", bits=" + bits +
                    ", timeTakenLastTurnMillis=" + timeTakenLastTurnMillis +
                    '}';
        }
    }
    public PlayerStats p1Stats;
    public PlayerStats p2Stats;
    public static final class PlayerUnit {
        public int x;
        public int y;
        public float stability;
        public String unitId;

        @Override
        public String toString() {
            return "PlayerUnit{" +
                    "x=" + x +
                    ", y=" + y +
                    ", stability=" + stability +
                    ", unitId='" + unitId + '\'' +
                    '}';
        }
    }
    public static final class PlayerUnitList extends ArrayList<PlayerUnit> {
        public PlayerUnitList(List<PlayerUnit> contents) {
            super(contents);
        }
    }
    public static final class PlayerUnits {
        public PlayerUnitList wall;
        public PlayerUnitList support;
        public PlayerUnitList turret;
        public PlayerUnitList scout;
        public PlayerUnitList demolisher;
        public PlayerUnitList interceptor;
        public PlayerUnitList remove;
        public PlayerUnitList upgrade;

        @Override
        public String toString() {
            return "PlayerUnits{" +
                    "wall=" + wall +
                    ", support=" + support +
                    ", turret=" + turret +
                    ", scout=" + scout +
                    ", demolisher=" + demolisher +
                    ", interceptor=" + interceptor +
                    ", remove=" + remove +
                    ", upgrade=" + upgrade +
                    '}';
        }
    }
    public PlayerUnits p1Units;
    public PlayerUnits p2Units;
    public static final class EndStats {
        public static final class PlayerEndStats {
            public float dynamic_resource_spent;
            public float dynamic_resource_destroyed;
            public float dynamic_resource_spoiled;
            public float stationary_resource_spent;
            public float stationary_resource_left_on_board;
            public int points_scored;
            public boolean crashed;
            public float total_computation_time;

            @Override
            public String toString() {
                return "PlayerEndStats{" +
                        "dynamic_resource_spent=" + dynamic_resource_spent +
                        ", dynamic_resource_destroyed=" + dynamic_resource_destroyed +
                        ", dynamic_resource_spoiled=" + dynamic_resource_spoiled +
                        ", stationary_resource_spent=" + stationary_resource_spent +
                        ", stationary_resource_left_on_board=" + stationary_resource_left_on_board +
                        ", points_scored=" + points_scored +
                        ", crashed=" + crashed +
                        ", total_computation_time=" + total_computation_time +
                        '}';
            }
        }
        public PlayerEndStats player1;
        public PlayerEndStats player2;
        public float duration;
        public int turns;
        public int frames;
        public enum Winner {
            Tie,
            Player1,
            Player2,
        }
        public Winner winner;

        @Override
        public String toString() {
            return "EndStats{" +
                    "player1=" + player1 +
                    ", player2=" + player2 +
                    ", duration=" + duration +
                    ", turns=" + turns +
                    ", frames=" + frames +
                    ", winner=" + winner +
                    '}';
        }
    }
    public EndStats endStats; // nullable
    public static final class Events {
        public static final class AttackEvent {
            public Coords source;
            public Coords target;
            public float damage;
            public UnitType attackerType;
            public String sourceUnitId;
            public String targetUnitId;
            public PlayerId sourcePlayer;

            @Override
            public String toString() {
                return "AttackEvent{" +
                        "source=" + source +
                        ", target=" + target +
                        ", damage=" + damage +
                        ", attackerType=" + attackerType +
                        ", sourceUnitId='" + sourceUnitId + '\'' +
                        ", targetUnitId='" + targetUnitId + '\'' +
                        ", sourcePlayer=" + sourcePlayer +
                        '}';
            }
        }
        public List<AttackEvent> attack;
        public static final class BreachEvent {
            public Coords coords;
            public float damage;
            public UnitType breacherType;
            public String breacherId;
            public PlayerId unitOwner;

            @Override
            public String toString() {
                return "BreachEvent{" +
                        "coords=" + coords +
                        ", damage=" + damage +
                        ", breacherType=" + breacherType +
                        ", breacherId='" + breacherId + '\'' +
                        ", unitOwner=" + unitOwner +
                        '}';
            }
        }
        public List<BreachEvent> breach;
        public static final class DamageEvent {
            public Coords coords;
            public float damage;
            public UnitType breacherType;
            public String damagerId;
            public PlayerId unitOwner;

            @Override
            public String toString() {
                return "DamageEvent{" +
                        "coords=" + coords +
                        ", damage=" + damage +
                        ", breacherType=" + breacherType +
                        ", damagerId='" + damagerId + '\'' +
                        ", unitOwner=" + unitOwner +
                        '}';
            }
        }
        public List<DamageEvent> damage;
        public static final class DeathEvent {
            public Coords coords;
            public UnitType destroyedUnitType;
            public String unitId;
            public PlayerId unitOwner;

            @Override
            public String toString() {
                return "DeathEvent{" +
                        "coords=" + coords +
                        ", destroyedUnitType=" + destroyedUnitType +
                        ", unitId='" + unitId + '\'' +
                        ", unitOwner=" + unitOwner +
                        '}';
            }
        }
        public List<DeathEvent> death;
        public static final class MeleeEvent {
            public Coords attackerLocation;
            public Coords victimLocation;
            public float damageDealt;
            public UnitType attackerUnitType;
            public String attackerUnitId;
            public PlayerId attackerPlayerId;

            @Override
            public String toString() {
                return "MeleeEvent{" +
                        "attackerLocation=" + attackerLocation +
                        ", victimLocation=" + victimLocation +
                        ", damageDealt=" + damageDealt +
                        ", attackerUnitType=" + attackerUnitType +
                        ", attackerUnitId='" + attackerUnitId + '\'' +
                        ", attackerPlayerId=" + attackerPlayerId +
                        '}';
            }
        }
        public List<MeleeEvent> melee;
        public static final class MoveEvent {
            public Coords oldLocation;
            public Coords newLocation;
            public Coords desiredNextLocation;
            public UnitType unitType;
            public String unitId;
            public PlayerId owner;

            @Override
            public String toString() {
                return "MoveEvent{" +
                        "oldLocation=" + oldLocation +
                        ", newLocation=" + newLocation +
                        ", desiredNextLocation=" + desiredNextLocation +
                        ", unitType=" + unitType +
                        ", unitId='" + unitId + '\'' +
                        ", owner=" + owner +
                        '}';
            }
        }
        public List<MoveEvent> move;
        public static final class SelfDestructEvent {
            public Coords source;
            public List<Coords> targets;
            public float damage;
            public UnitType unitType;
            public String explodingUnitId;
            public PlayerId explodingUnitOwner;

            @Override
            public String toString() {
                return "SelfDestructEvent{" +
                        "source=" + source +
                        ", targets=" + targets +
                        ", damage=" + damage +
                        ", unitType=" + unitType +
                        ", explodingUnitId='" + explodingUnitId + '\'' +
                        ", explodingUnitOwner=" + explodingUnitOwner +
                        '}';
            }
        }
        public List<SelfDestructEvent> selfDestruct;
        public static final class ShieldEvent {
            public Coords supportCoords;
            public Coords mobileUnitCoords;
            public float shieldAmount;
            public UnitType supportType;
            public String supportUnitId;
            public String mobileUnitId;
            public PlayerId supportOwner;

            @Override
            public String toString() {
                return "ShieldEvent{" +
                        "supportCoords=" + supportCoords +
                        ", mobileUnitCoords=" + mobileUnitCoords +
                        ", shieldAmount=" + shieldAmount +
                        ", supportType=" + supportType +
                        ", supportUnitId='" + supportUnitId + '\'' +
                        ", mobileUnitId='" + mobileUnitId + '\'' +
                        ", supportOwner=" + supportOwner +
                        '}';
            }
        }
        public List<ShieldEvent> shield;
        public static final class SpawnEvent {
            public Coords spawnLocation;
            public UnitType spawningUnitType;
            public String spawningUnitId;
            public PlayerId owner;

            @Override
            public String toString() {
                return "SpawnEvent{" +
                        "spawnLocation=" + spawnLocation +
                        ", spawningUnitType=" + spawningUnitType +
                        ", spawningUnitId='" + spawningUnitId + '\'' +
                        ", owner=" + owner +
                        '}';
            }
        }
        public List<SpawnEvent> spawn;

        @Override
        public String toString() {
            return "Events{" +
                    "attack=" + attack +
                    ", breach=" + breach +
                    ", damage=" + damage +
                    ", death=" + death +
                    ", melee=" + melee +
                    ", move=" + move +
                    ", selfDestruct=" + selfDestruct +
                    ", shield=" + shield +
                    ", spawn=" + spawn +
                    '}';
        }
    }
    public Events events;

    @Override
    public String toString() {
        return "FrameData{" +
                "turnInfo=" + turnInfo +
                ", p1Stats=" + p1Stats +
                ", p2Stats=" + p2Stats +
                ", p1Units=" + p1Units +
                ", p2Units=" + p2Units +
                '}';
    }

    public static Gson gson(UnitTypeAtlas atlas) {
        return new GsonBuilder()
                .registerTypeAdapter(Coords.class, new JsonDeserializeClassFromTuple<>(Coords.class, () -> new Coords(-1, -1)))
                .registerTypeAdapter(UnitType.class, new UnitTypeDeserializer(atlas))
                .registerTypeAdapter(TurnInfo.Phase.class, new JsonDeserializeEnumFromInt<>(TurnInfo.Phase.class))
                .registerTypeAdapter(TurnInfo.class, new JsonDeserializeClassFromTuple<>(TurnInfo.class, TurnInfo::new))
                .registerTypeAdapter(PlayerStats.class, new JsonDeserializeClassFromTuple<>(PlayerStats.class, PlayerStats::new))
                .registerTypeAdapter(PlayerUnit.class, new JsonDeserializeClassFromTuple<>(PlayerUnit.class, PlayerUnit::new))
                .registerTypeAdapter(PlayerUnitList.class, new TypedListDeserializer<>(PlayerUnitList::new, PlayerUnit.class))
                .registerTypeAdapter(PlayerUnits.class, new JsonDeserializeClassFromTuple<>(PlayerUnits.class, PlayerUnits::new))
                .registerTypeAdapter(EndStats.Winner.class, new JsonDeserializeEnumFromInt<>(EndStats.Winner.class))
                .registerTypeAdapter(Events.AttackEvent.class, new JsonDeserializeClassFromTuple<>(Events.AttackEvent.class, Events.AttackEvent::new))
                .registerTypeAdapter(Events.BreachEvent.class, new JsonDeserializeClassFromTuple<>(Events.BreachEvent.class, Events.BreachEvent::new))
                .registerTypeAdapter(Events.DamageEvent.class, new JsonDeserializeClassFromTuple<>(Events.DamageEvent.class, Events.DamageEvent::new))
                .registerTypeAdapter(Events.DeathEvent.class, new JsonDeserializeClassFromTuple<>(Events.DeathEvent.class, Events.DeathEvent::new))
                .registerTypeAdapter(Events.MeleeEvent.class, new JsonDeserializeClassFromTuple<>(Events.MeleeEvent.class, Events.MeleeEvent::new))
                .registerTypeAdapter(Events.MoveEvent.class, new JsonDeserializeClassFromTuple<>(Events.MoveEvent.class, Events.MoveEvent::new))
                .registerTypeAdapter(Events.SelfDestructEvent.class, new JsonDeserializeClassFromTuple<>(Events.SelfDestructEvent.class, Events.SelfDestructEvent::new))
                .registerTypeAdapter(Events.ShieldEvent.class, new JsonDeserializeClassFromTuple<>(Events.ShieldEvent.class, Events.ShieldEvent::new))
                .registerTypeAdapter(Events.SpawnEvent.class, new JsonDeserializeClassFromTuple<>(Events.SpawnEvent.class, Events.SpawnEvent::new))
                .create();
    }
}
