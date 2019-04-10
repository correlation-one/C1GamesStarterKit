/*
Description: Contains useful enums describing game data.
Last Modified: 07 Apr 2019
Author: Isaac Draper
*/

#ifndef ENUMS_H
#define ENUMS_H

namespace terminal {

    enum UNIT_TYPE {
        FILTER,
        ENCRYPTOR,
        DESTRUCTOR,
        PING,
        EMP,
        SCRAMBLER,
        REMOVE
    };

    enum RESOURCE {
        BITS,
        CORES
    };

    enum STATS {
        HEALTH,
        TIME
    };

    enum EDGE {
        TOP_RIGHT,
        TOP_LEFT,
        BOTTOM_LEFT,
        BOTTOM_RIGHT
    };
    enum VERBOSITY {
        SUPPRESS,
        WARNING,
        INVARIENT,
        CRASH,
    };}

#endif
