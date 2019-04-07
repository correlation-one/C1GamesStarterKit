/*
Description: A header to handle basic utility functions like communicating with the engine.
Last Modified: 06 Apr 2019
Author: Isaac Draper
*/

#ifndef UTIL_H
#define UTIL_H

#include <algorithm>
#include <iostream>
#include <string>

#include "json11/json11.hpp"
#include "customExceptions.h"

namespace terminal {

    using std::string;

    /// Handles communication with the engine and other basic functions.
    /// All functions are static and should not be restricted.
    class Util {
    public:
        static json11::Json getCommand();
        static void sendCommand(string command);
        static void debugWrite(string output, bool newline=true);

    };

}

#endif
