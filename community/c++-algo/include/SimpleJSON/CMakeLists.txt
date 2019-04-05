cmake_minimum_required (VERSION 2.6)
project (SimpleJSON)

set(HEADERS
	src/JSON.h
	src/JSON.cpp
	src/JSONValue.h
	src/JSONValue.cpp
)

add_library(SimpleJSON ${HEADERS})
