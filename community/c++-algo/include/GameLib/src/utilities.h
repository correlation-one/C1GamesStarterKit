#ifndef UTILITIES_H
#define UTILITIES_H

#include <algorithm>
#include <iostream>
#include <string>

#include "json11/json11.hpp"
#include "customExceptions.h"

namespace terminal {

	using std::string;

	class Utilities {
	public:
		static json11::Json getCommand();
		static void sendCommand(string command);
		static void debugWrite(string output, bool newline=true);

	};

}

#endif
