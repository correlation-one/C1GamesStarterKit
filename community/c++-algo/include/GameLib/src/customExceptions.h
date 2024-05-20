/*
Description: This is a header to contain custom exceptions for the terminal game.
Last Modified: 06 Apr 2019
Author: Isaac Draper
*/

#ifndef CUSTOM_EXCEPTIONS_H
#define CUSTOM_EXCEPTIONS_H

#include <stdexcept>
#include <string>

namespace terminal {

    using std::string;

    /// A class to act as a custom exception.
    /// It is primarily to be inherrited by any custom exception used by the project.
    class CustomException : public std::exception {
    public:
        CustomException(const string errorMsg="Custom Exception") {
            msg = errorMsg;
        }
        const char* what() {
            return msg.c_str();
        }
    protected:
        string msg; ///< Stores the message for the error.
    };

    /// A Custom Exception to be thrown by any utility critical errors.
    class UtilException : public CustomException {
    public:
        UtilException(const string errorMsg = "Util Exception") : CustomException(errorMsg) {}
    };

    /// An exception to be thrown when there is something wrong with a Unit Type.
    class UnitTypeException : public CustomException {
    public:
        UnitTypeException(const string errorMsg = "Unit Type Exception") : CustomException(errorMsg) {}
    };

    /// An exception to be thrown when there is something wrong with spawning a unit.
    class UnitSpawnException : public CustomException {
    public:
        UnitSpawnException(const string errorMsg = "Unit Spawn Exception") : CustomException(errorMsg) {}
    };

    /// An exception to be thrown when there is something wrong with removing a unit.
    class UnitRemoveException : public CustomException {
    public:
        UnitRemoveException(const string errorMsg = "Unit Remove Exception") : CustomException(errorMsg) {}
    };

    /// An exception to be thrown when there is something wrong with a position.
    class PosException : public CustomException {
    public:
        PosException(const string errorMsg = "Pos Exception") : CustomException(errorMsg) {}
    };

    /// An exception to be thrown when an invalid player index is used.
    class PlayerIndexException : public CustomException {
    public:
        PlayerIndexException(const string errorMsg = "Player Index Exception") : CustomException(errorMsg) {}
    };

    /// An exception to be thrown when something wrong happens with the GameMap.
    class GameMapException : public CustomException {
    public:
        GameMapException(const string errorMsg = "Game Map Exception") : CustomException(errorMsg) {}
    };

}

#endif
