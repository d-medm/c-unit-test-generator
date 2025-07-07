
#include <gtest/gtest.h>
#include "calculator.h"

TEST(Calculator, Add) {
    int result = add(1, 2);
    EXPECT_EQ(result, 3);
}

TEST(Calculator, Subtract) {
    int result = subtract(1, 2);
    EXPECT_EQ(result, -1);
}

TEST(Calculator, Multiply) {
    int result = multiply(2, 3);
    EXPECT_EQ(result, 6);
}

TEST(Calculator, Divide) {
    int result = divide(4, 2);
    EXPECT_EQ(result, 2);
}

#include "calculator.h"

