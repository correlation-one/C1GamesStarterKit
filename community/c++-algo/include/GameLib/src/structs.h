/*
Description: Contains useful structs for storing game data.
Last Modified: 07 Apr 2019
Author: Isaac Draper
*/

#ifndef STRUCTS_H
#define STRUCTS_H

#include "enums.h"

namespace terminal {

    struct Player {
        double BITS;
        double CORES;
        int HEALTH;
        int TIME;
    };

}

#endif
