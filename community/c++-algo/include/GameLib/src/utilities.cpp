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

		if (err != "") {
			string errorMsg = "Error parsing string from engine:\n\t" + err;
			throw UtilException(errorMsg.c_str());
		}

		/*
		for (auto entry : state.object_items()) {
			cerr << entry.first << endl;
		}
		*/

		return state;
	}

	void Utilities::sendCommand(string command) {
		command.erase(std::remove(command.begin(), command.end(), '\n'), command.end());
		cout << command << endl;
	}

	void Utilities::debugWrite(string output, bool newline) {
		cerr << output << (newline ? "\n" : "");
		cerr.flush();
	}

}
