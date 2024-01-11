/*
Description: Implmentations for the util header.
Last Modified: 08 Apr 2019
Author: Isaac Draper
*/

#include "util.h"

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
    Json Util::getCommand() {
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
    /// @param command A Json formatted string to send to the engine.
    void Util::sendCommand(string command) {
        command.erase(std::remove(command.begin(), command.end(), '\n'), command.end());
        cout << command << endl;
        cout.flush();
    }

}
