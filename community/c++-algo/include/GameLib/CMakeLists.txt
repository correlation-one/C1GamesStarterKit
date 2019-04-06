cmake_minimum_required (VERSION 2.6)
project (GameLib)

set(HEADERS
	src/utilities.h
	src/utilities.cpp
)

add_library(GameLib ${HEADERS})

target_include_directories (GameLib PRIVATE "${CMAKE_SOURCE_DIR}/include")

target_link_libraries(GameLib SimpleJSON)
