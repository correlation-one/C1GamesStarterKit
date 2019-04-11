/*
Description: A header to handle basic utility functions like communicating with the engine.
Last Modified: 08 Apr 2019
Author: Isaac Draper
*/

#ifndef UTIL_H
#define UTIL_H

#include <algorithm>
#include <iostream>
#include <string>

#include "json11/json11.hpp"
#include "customExceptions.h"
#include "enums.h"

namespace terminal {

    using std::string;
    using std::cerr;

    /// Handles communication with the engine and other basic functions.
    /// All functions are static and should not be restricted.
    class Util {
    public:
        static json11::Json getCommand();
        static void sendCommand(string command);

        /// This prints a message to the game's debug console using cerr.
        /// @param obj An object to print. This would typically be a string.
        /// @param newline Whether or not to print a newline at the end of the message.
        template <typename T>
        static void debugWrite(T obj, bool newline=true) {
            cerr << obj << (newline ? "\n" : "");
            cerr.flush();
        }

        /// This prints or thows an error depending on the level you set it at.
        /// INVARIANT and CRASH levels will throw an exception,
        /// WARNING simply prints the error, and 
        /// SUPPRESS hides all errors.
        /// This is a template function where you specify the type
        /// of exception (must inhert from CustomException) to throw.
        /// @param warning The warning to either print or throw.
        /// @param warningLevel The level to throw this type of warning.
        /// @param currentLevel The level the user currently has it set at.
        template <typename CE>
        static void printError(std::string warning, VERBOSITY warningLevel, VERBOSITY currentLevel) {
            if (currentLevel >= warningLevel) {
                if (currentLevel >= INVARIANT)
                    throw CE(warning);
                else
                    debugWrite(warning);
            }
        }
    };

}

#endif
