/*
Description: Contains useful structs for storing game data.
Last Modified: 08 Apr 2019
Author: Isaac Draper
*/

#ifndef STRUCTS_H
#define STRUCTS_H

#include <iostream>

#include "enums.h"
#include "customExceptions.h"

namespace terminal {

    /// This represents a position on the board.
    struct Pos {
        int x;
        int y;
        /// This allows for python location indexing to be transferrable
        /// @param index The index of the position coordinate
        /// @return The value of the coordinate
        inline int operator[](int index) {
            if (index == 0) return x;
            if (index == 1) return y;
            throw PosException("Invalid position index (0 or 1)");
            return 0;
        }
        /// This allows for comparison between positions
        /// @param rhs Right hand side position
        /// @return The boolean answer to whether two positions are the same.
        inline bool operator==(const Pos &rhs) {
            return x == rhs.x && y == rhs.y;
        }
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
