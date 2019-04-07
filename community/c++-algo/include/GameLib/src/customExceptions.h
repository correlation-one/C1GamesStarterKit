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
        string msg;
    };

    /// A Custom Exception to be thrown by any utility critical errors.
    class UtilException : public CustomException {
    public:
        UtilException(const string errorMsg = "Util Exception") : CustomException(errorMsg) {}
    };

}


#endif
