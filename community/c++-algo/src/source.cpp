#include <iostream>
#include <string>

#include "json11/json11.hpp"
#include "GameLib/src/utilities.h"

int main(int argc, char * argv[]) {

	using std::cout;
	using std::cerr;
	using std::endl;
	using json11::Json;
	using terminal::Utilities;

    cerr << "Starting C++ Starter Algo" << endl;

    for (int i = 0; i < 200; i++) {
		Json state = Utilities::getCommand();

		cout << "[]\n";
		cout << "[]\n";
    }

    return 0;
}
