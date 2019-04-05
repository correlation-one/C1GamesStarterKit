#include "utilities.h"

namespace terminal {

	void Utilities::test() {
		JSONValue *value = JSON::Parse("{}");
		std::cerr << "ran test" << std::endl;
	}

}
