import unittest
from src.calculator import tokenize, parse_expression, CalculatorError


class TestCalculator(unittest.TestCase):

    def test_addition(self):
        self.assertEqual(parse_expression(tokenize("2 + 3")), 5)
        self.assertEqual(parse_expression(tokenize("10 + 20")), 30)
        self.assertEqual(parse_expression(tokenize("5.5 + 4.5")), 10.0)

    def test_subtraction(self):
        self.assertEqual(parse_expression(tokenize("5 - 2")), 3)
        self.assertEqual(parse_expression(tokenize("20 - 10")), 10)
        self.assertEqual(parse_expression(tokenize("10.0 - 4.5")), 5.5)

    def test_multiplication(self):
        self.assertEqual(parse_expression(tokenize("2 * 3")), 6)
        self.assertEqual(parse_expression(tokenize("10 * 0.5")), 5.0)
        self.assertEqual(parse_expression(tokenize("7 * 8")), 56)

    def test_division(self):
        self.assertEqual(parse_expression(tokenize("10 / 2")), 5.0)
        self.assertEqual(parse_expression(tokenize("7 / 2")), 3.5)
        self.assertEqual(parse_expression(tokenize("100 / 10")), 10.0)

    def test_operator_precedence_and_parentheses(self):
        self.assertEqual(parse_expression(tokenize("2 + 3 * 4")), 14)
        self.assertEqual(parse_expression(tokenize("(2 + 3) * 4")), 20)
        self.assertEqual(parse_expression(tokenize("10 - 4 / 2")), 8)
        self.assertEqual(parse_expression(tokenize("(10 - 4) / 2")), 3)
        self.assertEqual(parse_expression(tokenize("2 * (3 + 4) - 5")), 9)

    def test_division_by_zero(self):
        with self.assertRaisesRegex(CalculatorError, "Error: Division by zero"):
            parse_expression(tokenize("10 / 0"))
        with self.assertRaisesRegex(CalculatorError, "Error: Division by zero"):
            parse_expression(tokenize("5 / (3 - 3)"))

    def test_invalid_expression_syntax(self):
        with self.assertRaisesRegex(CalculatorError, "Error: Invalid character 'a' in expression"):
            parse_expression(tokenize("2 + abc"))
        with self.assertRaisesRegex(CalculatorError, "Error: Unexpected token: +"):
            parse_expression(tokenize("2 ++ 3"))
        with self.assertRaisesRegex(CalculatorError, "Error: Unexpected end of expression"):
            parse_expression(tokenize("2 + "))

    def test_empty_or_whitespace_input(self):
        with self.assertRaisesRegex(CalculatorError, "Error: Empty expression"):
            tokenize("")
        with self.assertRaisesRegex(CalculatorError, "Error: Empty expression"):
            tokenize("   \t\n")
