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