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

}

#endif
