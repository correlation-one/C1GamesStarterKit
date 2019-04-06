/*
Description: Implmentations for the Utilities.h header.
Last Modified: 06 Apr 2019
Author: Isaac Draper
*/

#include "utilities.h"

namespace terminal {

    using std::cin;
    using std::cout;
    using std::cerr;
    using std::endl;
    using std::string;
    using json11::Json;

    /// This gets the next command from the terminal engine through cin.
    /// It then attempts to parse the command to return a Json object.
    /// @return Json object of command from the engine.
    Json Utilities::getCommand() {
        string stateStr, err;
        cin >> stateStr;

        Json state = Json::parse(stateStr, err);

        if (err != "") {
            string errorMsg = "Error parsing string from engine:\n\t" + err;
            throw UtilException(errorMsg.c_str());
        }

        return state;
    }

    /// This sends a command to the terminal engine through cout.
    /// It also removes all newline characters already inside the string.
    void Utilities::sendCommand(string command) {
        command.erase(std::remove(command.begin(), command.end(), '\n'), command.end());
        cout << command << endl;
    }

    /// This prints a message to the game's debug console using cerr.
    /// @param newline 
    void Utilities::debugWrite(string output, bool newline) {
        cerr << output << (newline ? "\n" : "");
        cerr.flush();
    }

}
