package test;

import com.c1games.terminal.algo.Config;
import com.c1games.terminal.algo.map.SpawnCommand;
import com.c1games.terminal.algo.units.UnitType;
import com.c1games.terminal.algo.units.UnitTypeAtlas;
import com.google.gson.Gson;
import org.junit.Test;

public class SpawnCommandSerializeTest {
    @Test public void test() {
        String configData = "{\n" +
                "  \"debug\": {\n" +
                "    \"printMapString\": false,\n" +
                "    \"printTStrings\": false,\n" +
                "    \"printActStrings\": false,\n" +
                "    \"printHitStrings\": false,\n" +
                "    \"printPlayerInputStrings\": false,\n" +
                "    \"printBotErrors\": false,\n" +
                "    \"printPlayerGetHitStrings\": false\n" +
                "  },\n" +
                "  \"unitInformation\": [\n" +
                "    {\n" +
                "      \"damage\": 0.0,\n" +
                "      \"cost\": 1.0,\n" +
                "      \"getHitRadius\": 0.51,\n" +
                "      \"display\": \"Filter\",\n" +
                "      \"range\": 3.0,\n" +
                "      \"shorthand\": \"FF\",\n" +
                "      \"stability\": 60.0\n" +
                "    },\n" +
                "    {\n" +
                "      \"damage\": 0.0,\n" +
                "      \"cost\": 4.0,\n" +
                "      \"getHitRadius\": 0.51,\n" +
                "      \"shieldAmount\": 10.0,\n" +
                "      \"display\": \"Encryptor\",\n" +
                "      \"range\": 3.0,\n" +
                "      \"shorthand\": \"EF\",\n" +
                "      \"stability\": 30.0\n" +
                "    },\n" +
                "    {\n" +
                "      \"damage\": 4.0,\n" +
                "      \"cost\": 3.0,\n" +
                "      \"getHitRadius\": 0.51,\n" +
                "      \"display\": \"Destructor\",\n" +
                "      \"range\": 3.0,\n" +
                "      \"shorthand\": \"DF\",\n" +
                "      \"stability\": 75.0\n" +
                "    },\n" +
                "    {\n" +
                "      \"damageI\": 1.0,\n" +
                "      \"damageToPlayer\": 1.0,\n" +
                "      \"cost\": 1.0,\n" +
                "      \"getHitRadius\": 0.51,\n" +
                "      \"damageF\": 1.0,\n" +
                "      \"display\": \"Ping\",\n" +
                "      \"range\": 3.0,\n" +
                "      \"shorthand\": \"PI\",\n" +
                "      \"stability\": 15.0,\n" +
                "      \"speed\": 0.5\n" +
                "    },\n" +
                "    {\n" +
                "      \"damageI\": 3.0,\n" +
                "      \"damageToPlayer\": 1.0,\n" +
                "      \"cost\": 3.0,\n" +
                "      \"getHitRadius\": 0.51,\n" +
                "      \"damageF\": 3.0,\n" +
                "      \"display\": \"EMP\",\n" +
                "      \"range\": 5.0,\n" +
                "      \"shorthand\": \"EI\",\n" +
                "      \"stability\": 5.0,\n" +
                "      \"speed\": 0.25\n" +
                "    },\n" +
                "    {\n" +
                "      \"damageI\": 10.0,\n" +
                "      \"damageToPlayer\": 1.0,\n" +
                "      \"cost\": 1.0,\n" +
                "      \"getHitRadius\": 0.51,\n" +
                "      \"damageF\": 0.0,\n" +
                "      \"display\": \"Scrambler\",\n" +
                "      \"range\": 3.0,\n" +
                "      \"shorthand\": \"SI\",\n" +
                "      \"stability\": 40.0,\n" +
                "      \"speed\": 0.25\n" +
                "    },\n" +
                "    {\n" +
                "      \"display\": \"Remove\",\n" +
                "      \"shorthand\": \"RM\"\n" +
                "    }\n" +
                "  ],\n" +
                "  \"timingAndReplay\": {\n" +
                "    \"waitTimeBotMax\": 70000,\n" +
                "    \"waitTimeManual\": 1820000,\n" +
                "    \"waitForever\": false,\n" +
                "    \"waitTimeBotSoft\": 40000,\n" +
                "    \"replaySave\": 0,\n" +
                "    \"storeBotTimes\": true\n" +
                "  },\n" +
                "  \"resources\": {\n" +
                "    \"turnIntervalForBitCapSchedule\": 10,\n" +
                "    \"turnIntervalForBitSchedule\": 10,\n" +
                "    \"bitRampBitCapGrowthRate\": 5.0,\n" +
                "    \"roundStartBitRamp\": 10,\n" +
                "    \"bitGrowthRate\": 1.0,\n" +
                "    \"startingHP\": 30.0,\n" +
                "    \"maxBits\": 999999.0,\n" +
                "    \"bitsPerRound\": 5.0,\n" +
                "    \"coresPerRound\": 4.0,\n" +
                "    \"coresForPlayerDamage\": 1.0,\n" +
                "    \"startingBits\": 5.0,\n" +
                "    \"bitDecayPerRound\": 0.33333,\n" +
                "    \"startingCores\": 25.0\n" +
                "  },\n" +
                "  \"mechanics\": {\n" +
                "    \"basePlayerHealthDamage\": 1.0,\n" +
                "    \"damageGrowthBasedOnY\": 0.0,\n" +
                "    \"bitsCanStackOnDeployment\": true,\n" +
                "    \"destroyOwnUnitRefund\": 0.5,\n" +
                "    \"destroyOwnUnitsEnabled\": true,\n" +
                "    \"stepsRequiredSelfDestruct\": 5,\n" +
                "    \"selfDestructRadius\": 1.5,\n" +
                "    \"shieldDecayPerFrame\": 0.15,\n" +
                "    \"meleeMultiplier\": 0,\n" +
                "    \"destroyOwnUnitDelay\": 1,\n" +
                "    \"rerouteMidRound\": true,\n" +
                "    \"firewallBuildTime\": 0\n" +
                "  }\n" +
                "}\n";
        System.out.println(configData);
        Config config = Config.GSON.fromJson(configData, Config.class);
        UnitTypeAtlas atlas = new UnitTypeAtlas(config);
        Gson gson = SpawnCommand.gson(atlas);
        SpawnCommand command = new SpawnCommand(UnitType.Encryptor, 4, 7);
        String ser = gson.toJson(command);
        assert ser.equals("[\"EF\",4,7]");
    }
}
