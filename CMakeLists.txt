cmake_minimum_required(VERSION 3.15)
project(CalculatorTest)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -g -O0 --coverage")

find_package(GTest REQUIRED)
include_directories(${GTEST_INCLUDE_DIRS})

include_directories(${PROJECT_SOURCE_DIR}/src)

add_executable(calculator_test
    src/calculator.cpp
    output/tests/calculator_test.cpp
    output/tests/calculator_test_refined.cpp
)
target_link_libraries(calculator_test ${GTEST_LIBRARIES} gtest_main pthread)