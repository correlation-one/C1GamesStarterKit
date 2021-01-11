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
                "  \"seasonCompatibilityModeP1\": 5,\n" +
                "  \"seasonCompatibilityModeP2\": 5,\n" +
                "  \"debug\":{\n" +
                "    \"printMapString\":false,\n" +
                "    \"printTStrings\":false,\n" +
                "    \"printActStrings\":false,\n" +
                "    \"printHitStrings\":false,\n" +
                "    \"printPlayerInputStrings\":false,\n" +
                "    \"printBotErrors\":true,\n" +
                "    \"printPlayerGetHitStrings\":false\n" +
                "  },\n" +
                "  \"unitInformation\": [\n" +
                "    {\n" +
                "      \"cost1\": 1.0,\n" +
                "      \"getHitRadius\":0.01,\n" +
                "      \"display\":\"Filter\",\n" +
                "      \"shorthand\":\"FF\",\n" +
                "      \"startHealth\":60.0,\n" +
                "      \"unitCategory\": 0,\n" +
                "      \"refundPercentage\": 0.75,\n" +
                "      \"turnsRequiredToRemove\": 1,\n" +
                "      \"upgrade\": {\n" +
                "        \"startHealth\": 120.0\n" +
                "      }\n" +
                "    },\n" +
                "    {\n" +
                "      \"cost1\":4.0,\n" +
                "      \"getHitRadius\":0.01,\n" +
                "      \"shieldPerUnit\":3.0,\n" +
                "      \"display\":\"Encryptor\",\n" +
                "      \"shieldRange\":3.5,\n" +
                "      \"shorthand\":\"EF\",\n" +
                "      \"startHealth\":30.0,\n" +
                "      \"unitCategory\": 0,\n" +
                "      \"shieldBonusPerY\": 0.0,\n" +
                "      \"refundPercentage\": 0.75,\n" +
                "      \"shieldDecay\": 0.0,\n" +
                "      \"turnsRequiredToRemove\": 1,\n" +
                "      \"upgrade\": {\n" +
                "        \"shieldRange\": 7,\n" +
                "        \"shieldPerUnit\":4\n" +
                "      }\n" +
                "    },\n" +
                "    {\n" +
                "      \"attackDamageWalker\":16.0,\n" +
                "      \"cost1\":6.0,\n" +
                "      \"getHitRadius\":0.01,\n" +
                "      \"display\":\"Destructor\",\n" +
                "      \"attackRange\":3.5,\n" +
                "      \"shorthand\":\"DF\",\n" +
                "      \"startHealth\":75.0,\n" +
                "      \"unitCategory\": 0,\n" +
                "      \"refundPercentage\": 0.75,\n" +
                "      \"turnsRequiredToRemove\": 1,\n" +
                "      \"upgrade\": {\n" +
                "        \"attackDamageWalker\":32.0\n" +
                "      }\n" +
                "    },\n" +
                "\n" +
                "\n" +
                "    {\n" +
                "      \"attackDamageTower\":2.0,\n" +
                "      \"attackDamageWalker\":2.0,\n" +
                "      \"playerBreachDamage\":1.0,\n" +
                "      \"cost2\":1.0,\n" +
                "      \"getHitRadius\":0.01,\n" +
                "      \"display\":\"Ping\",\n" +
                "      \"attackRange\":3.5,\n" +
                "      \"shorthand\":\"PI\",\n" +
                "      \"startHealth\":15.0,\n" +
                "      \"speed\":1,\n" +
                "      \"unitCategory\": 1,\n" +
                "      \"selfDestructDamageWalker\": 15.0,\n" +
                "      \"selfDestructDamageTower\": 15.0,\n" +
                "      \"metalForBreach\": 1.0,\n" +
                "      \"selfDestructRange\": 1.5,\n" +
                "      \"selfDestructStepsRequired\": 5\n" +
                "    },\n" +
                "    {\n" +
                "      \"attackDamageWalker\":8.0,\n" +
                "      \"attackDamageTower\":8.0,\n" +
                "      \"playerBreachDamage\":1.0,\n" +
                "      \"cost2\":3.0,\n" +
                "      \"getHitRadius\":0.01,\n" +
                "      \"display\":\"EMP\",\n" +
                "      \"attackRange\":4.5,\n" +
                "      \"shorthand\":\"EI\",\n" +
                "      \"startHealth\":5.0,\n" +
                "      \"speed\":0.5,\n" +
                "      \"unitCategory\": 1,\n" +
                "      \"selfDestructDamageWalker\": 5.0,\n" +
                "      \"selfDestructDamageTower\": 5.0,\n" +
                "      \"metalForBreach\": 1.0,\n" +
                "      \"selfDestructRange\": 1.5,\n" +
                "      \"selfDestructStepsRequired\": 5\n" +
                "    },\n" +
                "    {\n" +
                "      \"attackDamageWalker\":20.0,\n" +
                "      \"playerBreachDamage\":1.0,\n" +
                "      \"cost2\":1.0,\n" +
                "      \"getHitRadius\":0.01,\n" +
                "      \"display\":\"Scrambler\",\n" +
                "      \"attackRange\":4.5,\n" +
                "      \"shorthand\":\"SI\",\n" +
                "      \"startHealth\":40.0,\n" +
                "      \"speed\":0.25,\n" +
                "      \"unitCategory\": 1,\n" +
                "      \"selfDestructDamageWalker\": 40.0,\n" +
                "      \"selfDestructDamageTower\": 40.0,\n" +
                "      \"metalForBreach\": 1.0,\n" +
                "      \"selfDestructRange\": 1.5,\n" +
                "      \"selfDestructStepsRequired\": 5\n" +
                "    },\n" +
                "    {\n" +
                "      \"display\":\"Remove\",\n" +
                "      \"shorthand\":\"RM\"\n" +
                "    },\n" +
                "    {\n" +
                "      \"display\":\"Upgrade\",\n" +
                "      \"shorthand\":\"UP\"\n" +
                "    }\n" +
                "  ],\n" +
                "  \"timingAndReplay\":{\n" +
                "    \"waitTimeBotMax\":35000,\n" +
                "    \"playWaitTimeBotMax\":40000,\n" +
                "    \"waitTimeManual\":1820000,\n" +
                "    \"waitForever\":false,\n" +
                "    \"waitTimeBotSoft\":5000,\n" +
                "    \"playWaitTimeBotSoft\":10000,\n" +
                "    \"replaySave\":1,\n" +
                "    \"playReplaySave\":0,\n" +
                "    \"storeBotTimes\":true,\n" +
                "    \"waitTimeStartGame\":3000,\n" +
                "    \"waitTimeEndGame\":3000\n" +
                "  },\n" +
                "  \"resources\":{\n" +
                "    \"turnIntervalForBitCapSchedule\":10,\n" +
                "    \"turnIntervalForBitSchedule\":10,\n" +
                "    \"bitRampBitCapGrowthRate\":5.0,\n" +
                "    \"roundStartBitRamp\":10,\n" +
                "    \"bitGrowthRate\":1.0,\n" +
                "    \"startingHP\":30.0,\n" +
                "    \"maxBits\":150.0,\n" +
                "    \"bitsPerRound\":5.0,\n" +
                "    \"coresPerRound\":5.0,\n" +
                "    \"coresForPlayerDamage\":1.0,\n" +
                "    \"startingBits\":5.0,\n" +
                "    \"bitDecayPerRound\":0.25,\n" +
                "    \"startingCores\":40.0\n" +
                "  }\n" +
                "}\n";
        System.out.println(configData);
        Config config = Config.GSON.fromJson(configData, Config.class);
        UnitTypeAtlas atlas = new UnitTypeAtlas(config);
        Gson gson = SpawnCommand.gson(atlas);
        SpawnCommand command = new SpawnCommand(UnitType.Support, 4, 7);
        String ser = gson.toJson(command);
        assert ser.equals("[\"EF\",4,7]");
    }
}
