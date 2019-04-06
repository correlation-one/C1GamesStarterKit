#include "utilities.h"

namespace terminal {

	using std::cin;
	using std::cout;
	using std::cerr;
	using std::endl;
	using std::string;
	using json11::Json;

	Json Utilities::getCommand() {
		string stateStr, err;
		cin >> stateStr;

		Json state = Json::parse(stateStr, err);

		/*
		for (auto entry : state.object_items()) {
			cerr << entry.first << endl;
		}
		*/

		return state;
	}


}
