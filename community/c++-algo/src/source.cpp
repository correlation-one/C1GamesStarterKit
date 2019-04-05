#include <iostream>
#include <string>

#include "SimpleJSON\src\JSON.h"

int main(int argc, char * argv[]) {

    std::cerr << "Starting C++ Starter Algo" << std::endl;
    
    std::string cmd_str;

    for (int i = 0; i < 200; i++) {
		std::cin >> cmd_str;
        std::cerr << cmd_str << std::endl;

		JSONValue *value = JSON::Parse(cmd_str.c_str());

        if (value == NULL) {
			std::cerr << "Error parsing JSON from engine" << std::endl;
        }
		else {
			// Do stuff
		}

		std::cout << "[]\n";
		std::cout << "[]\n";
    }

    return 0;
}
