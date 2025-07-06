Here is the refined Google Test code for the given calculator functions:
cpp
#include <gtest/gtest.h>
#include "calculator.h"

TEST(CalculatorTest, Add) {
    EXPECT_EQ(add(2, 3), 5);
}

TEST(CalculatorTest, Subtract) {
    EXPECT_EQ(subtract(4, 2), 2);
}

TEST(CalculatorTest, Multiply) {
    EXPECT_EQ(multiply(2, 3), 6);
}

TEST(CalculatorTest, Divide) {
    EXPECT_EQ(divide(8, 4), 2);
}

TEST(CalculatorTest, DivisionByZero) {
    ASSERT_ANY_THROW(divide(10, 0));
}

The `DivisionByZero` test case checks that the `divide` function throws an exception when it is given a divisor of zero. This is an important test case because it verifies that the function behaves correctly when given invalid input.