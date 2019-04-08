/*
Description: Contains useful structs for storing game data.
Last Modified: 07 Apr 2019
Author: Isaac Draper
*/

#ifndef STRUCTS_H
#define STRUCTS_H

#include "enums.h"

namespace terminal {

    struct Pos {
        int x;
        int y;
    };

    struct Player {
        double bits;
        double cores;
        int health;
        int time;
        int id;
    };

}

#endif
