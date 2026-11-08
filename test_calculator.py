import unittest

from calculator import CalculatorError, calculate


class CalculateTests(unittest.TestCase):
    def test_basic_operations(self):
        self.assertEqual(calculate("2+3"), "5")
        self.assertEqual(calculate("10-4"), "6")
        self.assertEqual(calculate("6*7"), "42")
        self.assertEqual(calculate("9/3"), "3")
        self.assertEqual(calculate("7/2"), "3.5")

    def test_precedence_and_parentheses(self):
        self.assertEqual(calculate("2+3*4"), "14")
        self.assertEqual(calculate("(2+3)*4"), "20")
        self.assertEqual(calculate("2*(3+(4-1))"), "12")

    def test_friendly_symbols(self):
        self.assertEqual(calculate("6×7"), "42")
        self.assertEqual(calculate("8÷2"), "4")
        self.assertEqual(calculate("5−3"), "2")
        self.assertEqual(calculate("√(9)"), "3")

    def test_decimals(self):
        self.assertEqual(calculate("0.1+0.2"), "0.3")
        self.assertEqual(calculate("1,5+1"), "2.5")  # decimal comma
        self.assertEqual(calculate("1/3"), "0.333333333333")

    def test_unary_minus(self):
        self.assertEqual(calculate("-3+5"), "2")
        self.assertEqual(calculate("2*-3"), "-6")
        self.assertEqual(calculate("--4"), "4")

    def test_power_and_functions(self):
        self.assertEqual(calculate("2^10"), "1024")
        self.assertEqual(calculate("2**3"), "8")
        self.assertEqual(calculate("sqrt(16)"), "4")
        self.assertEqual(calculate("abs(-7)"), "7")
        self.assertEqual(calculate("pi*2"), "6.28318530718")

    def test_percent(self):
        self.assertEqual(calculate("50%"), "0.5")
        self.assertEqual(calculate("200*10%"), "20")
        self.assertEqual(calculate("(2+3)%"), "0.05")
        self.assertEqual(calculate("100/50%"), "200")

    def test_large_numbers_use_scientific_notation(self):
        self.assertIn("e+30", calculate("2^100"))

    def test_errors(self):
        bad = [
            "",
            "   ",
            "2+",
            "abc",
            "1/0",
            "0^-1",
            "sqrt(-1)",
            "(-8)^0.5",
            "9^9^9",
            "%",
            "((1+2)",
            "2(3)",
            "1e999",
            "9" * 300,
        ]
        for expression in bad:
            with self.subTest(expression=expression):
                with self.assertRaises(CalculatorError):
                    calculate(expression)

    def test_rejects_code_injection(self):
        evil = [
            "__import__('os').system('echo hi')",
            "().__class__",
            "open('x')",
            "1; 2",
            "len('a')",
            "[1,2]",
            "lambda: 1",
            "True+1",
        ]
        for expression in evil:
            with self.subTest(expression=expression):
                with self.assertRaises(CalculatorError):
                    calculate(expression)

    def test_non_string(self):
        with self.assertRaises(CalculatorError):
            calculate(42)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
