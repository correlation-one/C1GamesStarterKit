/*
Description: Contains useful structs for storing game data.
Last Modified: 08 Apr 2019
Author: Isaac Draper
*/

#ifndef STRUCTS_H
#define STRUCTS_H

#include "enums.h"

namespace terminal {

    /// This represents a position on the board.
    struct Pos {
        int x;
        int y;
    };

    /// This represents a player and stores its data.
    struct Player {
        double bits;
        double cores;
        int health;
        int time;
        int id;
    };

    /// This sends a representation of the Pos struct to a stream.
    /// @return The stream passed to the function.
    inline std::ostream& operator<<(std::ostream& os, Pos const& pos) {
        os << "(" << pos.x << ", " << pos.y << ")";
        return os;
    }

    /// This sends a representation of the Player struct to a stream.
    /// @return The stream passed to the function.
    inline std::ostream& operator<<(std::ostream& os, Player const& player) {
        os << "Player " << player.id << ":   Bits(" <<
            player.bits << ")  Cores(" <<
            player.cores << ")  Health(" <<
            player.health << ")";
        return os;
    }

}

#endif
