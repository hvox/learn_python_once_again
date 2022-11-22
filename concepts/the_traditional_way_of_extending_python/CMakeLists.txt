cmake_minimum_required(VERSION 3.10)
project(aboba)
find_package(PythonInterp 3.10 REQUIRED)
find_package(PythonLibs 3.10 REQUIRED)
include_directories ("${PYTHON_INCLUDE_DIRS}")
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

add_library(aboba SHARED "${CMAKE_SOURCE_DIR}/aboba.c")
set_target_properties(
    aboba
    PROPERTIES
        PREFIX ""
        OUTPUT_NAME "aboba"
        LINKER_LANGUAGE C
    )
