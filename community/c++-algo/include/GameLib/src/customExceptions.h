#ifndef CUSTOM_EXCEPTIONS_H
#define CUSTOM_EXCEPTIONS_H

#include <stdexcept>
#include <string>

namespace terminal {

	using std::string;

	class CustomException : public std::exception {
	public:
		CustomException(const string errorMsg="Custom Exception") {
			msg = errorMsg;
		}
		const char* what() {
			return msg.c_str();
		}
	protected:
		string msg;
	};

	class UtilException : public CustomException {
	public:
		UtilException(const string errorMsg = "Utilities Exception") : CustomException(errorMsg) {}
	};

}


#endif
