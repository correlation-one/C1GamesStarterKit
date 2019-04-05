#include <iostream>
#include <string>

#include "SimpleJSON\src\JSON.h"
#include "GameLib\src\utilities.h"

int main(int argc, char * argv[]) {

    std::cerr << "Starting C++ Starter Algo" << std::endl;
    
    std::string cmd_str;

    for (int i = 0; i < 200; i++) {
		std::cin >> cmd_str;
        std::cerr << cmd_str << std::endl;

		std::cout << "[]\n";
		std::cout << "[]\n";
    }

    return 0;
}
