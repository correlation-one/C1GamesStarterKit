/*
Description: This is the main entry point for your algo.
Last Modified: 06 Apr 2019
Author: Isaac Draper
*/

#include <iostream>
#include <string>

#include "json11/json11.hpp"
#include "GameLib/src/utilities.h"

int main(int argc, char * argv[]) {

    using json11::Json;
    using terminal::Utilities;

    std::cerr << "Starting C++ Starter Algo" << std::endl;

    for (int i = 0; i < 200; i++) {
        try {
            Json state = Utilities::getCommand();
        }
        catch (terminal::UtilException e) {
            Utilities::debugWrite(e.what());
        }

        Utilities::sendCommand("[]");
        Utilities::sendCommand("[]");

    }

    return 0;
}
