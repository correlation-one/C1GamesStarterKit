/*
Description: Contains useful enums describing game data.
Last Modified: 11 Apr 2019
Author: Isaac Draper
*/

#ifndef ENUMS_H
#define ENUMS_H

namespace terminal {

    enum UNIT_TYPE {
        FILTER,         ///< Represents a filter unit type.
        ENCRYPTOR,      ///< Represents an encryptor unit type.
        DESTRUCTOR,     ///< Represents a destructor unit type.
        PING,           ///< Represents a ping unit type.
        EMP,            ///< Represents an emp unit type.
        SCRAMBLER,      ///< Represents a scrambler unit type.
        REMOVE          ///< Represents a remove command.
    };

    enum RESOURCE {
        BITS,           ///< Represents the bit resource.
        CORES           ///< Represents the core resource.
    };

    enum EDGE {
        TOP_RIGHT,      ///< Represents the top right edge of the map.
        TOP_LEFT,       ///< Represents the top left edge of the map.
        BOTTOM_LEFT ,   ///< Represents the bottom left edge of the map.
        BOTTOM_RIGHT    ///< Represents the bottom right edge of the map.
    };

    enum VERBOSITY {
        SUPPRESS,       ///< Means no errors will be printed. 
        WARNING,        ///< Will print warning level message.
        INVARIANT,      ///< Will throw invariant level and below exceptions.
        CRASH,          ///< Will throw all types of errors.
    };
}

#endif
