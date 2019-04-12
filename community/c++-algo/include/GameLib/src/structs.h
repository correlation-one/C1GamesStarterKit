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
    /// It requires the positions be positive since
    /// the terminal map only has positive points.
    struct Pos {
        unsigned int x;     ///< The x position of this location.
        unsigned int y;     ///< The y position of this location.

        /// Simple constructor to create the position.
        /// @param x X coordinate to set.
        /// @param y Y coordinate to set.
        Pos(unsigned int x, unsigned int y) : x(x), y(y) {}

        /// This allows for python location indexing to be transferrable.
        /// For example, to get the x position you can do: pos[0]
        /// @param index The index of the position coordinate.
        /// @return The value of the coordinate.
        inline int operator[](unsigned int index) {
            if (index == 0) return x;
            if (index == 1) return y;
            throw PosException("Invalid position index (0 or 1)");
            return 0;
        }
        
        /// This allows for comparison between positions.
        /// Two positions are equal if they have the same x and y values.
        /// @param rhs Right hand side position.
        /// @return Whether two positions are the same.
        inline bool operator==(const Pos &rhs) const {
            return x == rhs.x && y == rhs.y;
        }

    };

    /// This represents a player and stores its data.
    struct Player {
        double bits;        ///< The number of bits a player has.
        double cores;       ///< The number of cores a player has.
        int health;         ///< The health of a player.
        int time;           ///< The time a player took for their turn.
        int id;             ///< The player index, or number.
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
