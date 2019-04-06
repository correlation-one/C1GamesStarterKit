cmake_minimum_required (VERSION 2.6)
project (StarterAlgo)

set(out_dir ${CMAKE_SOURCE_DIR}/algo-target)

# First for the generic no-config case (e.g. with mingw)
set( CMAKE_RUNTIME_OUTPUT_DIRECTORY ${out_dir} )
set( CMAKE_LIBRARY_OUTPUT_DIRECTORY ${out_dir}/lib )
set( CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${out_dir}/lib )
# Second, for multi-config builds (e.g. msvc)
foreach( OUTPUTCONFIG ${CMAKE_CONFIGURATION_TYPES} )
    string( TOUPPER ${OUTPUTCONFIG} OUTPUTCONFIG )
    set( CMAKE_RUNTIME_OUTPUT_DIRECTORY_${OUTPUTCONFIG} ${out_dir} )
    set( CMAKE_LIBRARY_OUTPUT_DIRECTORY_${OUTPUTCONFIG} ${out_dir}/lib )
    set( CMAKE_ARCHIVE_OUTPUT_DIRECTORY_${OUTPUTCONFIG} ${out_dir}/lib )
endforeach( OUTPUTCONFIG CMAKE_CONFIGURATION_TYPES )

add_executable(StarterAlgo ${CMAKE_SOURCE_DIR}/src/source.cpp)

target_include_directories (StarterAlgo PRIVATE ${CMAKE_SOURCE_DIR}/include/)

add_subdirectory(${CMAKE_SOURCE_DIR}/include/json11/)
add_subdirectory(${CMAKE_SOURCE_DIR}/include/GameLib/)

target_link_libraries(StarterAlgo json11 GameLib)
