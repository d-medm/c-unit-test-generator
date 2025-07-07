
#include <gtest/gtest.h>
#include "calculator.h"

TEST(CalculatorRefined, Add) {
    int result = add(1, 2);
    EXPECT_EQ(result, 3);
}

TEST(CalculatorRefined, Subtract) {
    int result = subtract(1, 2);
    EXPECT_EQ(result, -1);
}

TEST(CalculatorRefined, Multiply) {
    int result = multiply(2, 3);
    EXPECT_EQ(result, 6);
}

TEST(CalculatorRefined, Divide) {
    int result = divide(4, 2);
    EXPECT_EQ(result, 2);
}

TEST(CalculatorRefined, DivideByZero) {
    EXPECT_THROW(divide(1, 0), std::invalid_argument);
}


