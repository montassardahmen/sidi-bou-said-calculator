"""Safe arithmetic engine for the Sidi Bou Said calculator.

Expressions are parsed with Python's ``ast`` module and evaluated by a small
whitelist-based interpreter, so user input is never passed to ``eval``.

Supported:  + - * /   ^ (power)   % (percent)   ( )   sqrt()   abs()   pi
Percent means "divide by 100", so ``50%`` is ``0.5`` and ``200*10%`` is ``20``.
"""

from __future__ import annotations

import ast
import math
import operator
import re
import sys

MAX_EXPRESSION_LENGTH = 200
MAX_EXPONENT = 1000
MAX_RESULT_BITS = 10_000  # guards against gigantic integer powers

# Characters accepted after symbol normalisation. No underscores, quotes or
# semicolons, so nothing exotic can reach the parser.
_ALLOWED = re.compile(r"[0-9A-Za-z+\-*/().%\s]+")

# Friendly symbols (and French-style decimal commas) mapped to Python syntax.
_REPLACEMENTS = {
    "×": "*",
    "÷": "/",
    "−": "-",
    "–": "-",
    "√": "sqrt",
    "^": "**",
    ",": ".",
}

_BINARY_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}
_UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}
_FUNCTIONS = {"sqrt": math.sqrt, "abs": abs}
_CONSTANTS = {"pi": math.pi}


class CalculatorError(ValueError):
    """Raised when an expression cannot be evaluated."""


def _expand_percent(expr: str) -> str:
    """Rewrite every ``X%`` as ``(X/100)`` where X is a number or a (...) group."""
    while "%" in expr:
        i = expr.index("%")
        j = i - 1
        if j < 0:
            raise CalculatorError("Percent needs a number before it")
        if expr[j] == ")":
            depth = 0
            while j >= 0:
                if expr[j] == ")":
                    depth += 1
                elif expr[j] == "(":
                    depth -= 1
                    if depth == 0:
                        break
                j -= 1
            if j < 0:
                raise CalculatorError("Unbalanced parentheses")
            while j > 0 and expr[j - 1].isalpha():  # keep a function name attached
                j -= 1
        else:
            while j >= 0 and (expr[j].isdigit() or expr[j] == "."):
                j -= 1
            j += 1
            if j == i:
                raise CalculatorError("Percent needs a number before it")
        expr = f"{expr[:j]}({expr[j:i]}/100){expr[i + 1:]}"
    return expr


def _power(base, exponent):
    if abs(exponent) > MAX_EXPONENT:
        raise CalculatorError("That exponent is too big for the souk")
    if isinstance(base, int) and isinstance(exponent, int):
        if base.bit_length() * abs(exponent) > MAX_RESULT_BITS:
            raise CalculatorError("Result is too large")
    if base < 0 and exponent != int(exponent):
        raise CalculatorError("No real result for that power")
    return base**exponent


def _eval(node):
    if isinstance(node, ast.Expression):
        return _eval(node.body)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return node.value
        raise CalculatorError("Only numbers are allowed")
    if isinstance(node, ast.BinOp):
        left, right = _eval(node.left), _eval(node.right)
        if isinstance(node.op, ast.Pow):
            return _power(left, right)
        op = _BINARY_OPS.get(type(node.op))
        if op is None:
            raise CalculatorError("That operator is not supported")
        return op(left, right)
    if isinstance(node, ast.UnaryOp):
        op = _UNARY_OPS.get(type(node.op))
        if op is None:
            raise CalculatorError("That operator is not supported")
        return op(_eval(node.operand))
    if isinstance(node, ast.Call):
        if (
            not isinstance(node.func, ast.Name)
            or node.func.id not in _FUNCTIONS
            or node.keywords
            or len(node.args) != 1
        ):
            raise CalculatorError("Unknown function")
        return _FUNCTIONS[node.func.id](_eval(node.args[0]))
    if isinstance(node, ast.Name):
        if node.id in _CONSTANTS:
            return _CONSTANTS[node.id]
        raise CalculatorError(f"Unknown name: {node.id}")
    raise CalculatorError("That doesn't look like a valid sum")


def format_number(value) -> str:
    """Turn a result into a tidy string (12 significant digits, no 0.30000000000000004)."""
    if isinstance(value, int):
        if abs(value) < 10**15:
            return str(value)
        value = float(value)
    if not math.isfinite(value):
        raise CalculatorError("Result is out of range")
    if value == int(value) and abs(value) < 1e15:
        return str(int(value))
    return f"{value:.12g}"


def calculate(expression: str) -> str:
    """Evaluate ``expression`` and return the result as a string.

    Raises ``CalculatorError`` with a human-friendly message on any problem.
    """
    if not isinstance(expression, str):
        raise CalculatorError("Expression must be text")
    expr = expression.strip()
    if not expr:
        raise CalculatorError("Type a sum first")
    if len(expr) > MAX_EXPRESSION_LENGTH:
        raise CalculatorError("That sum is too long")

    for old, new in _REPLACEMENTS.items():
        expr = expr.replace(old, new)
    if not _ALLOWED.fullmatch(expr):
        raise CalculatorError("That sum has characters I don't understand")

    expr = _expand_percent(expr)
    try:
        tree = ast.parse(expr, mode="eval")
    except (SyntaxError, ValueError, MemoryError, RecursionError):
        raise CalculatorError("That doesn't look like a valid sum") from None

    try:
        return format_number(_eval(tree))
    except CalculatorError:
        raise
    except ZeroDivisionError:
        raise CalculatorError("Can't divide by zero") from None
    except OverflowError:
        raise CalculatorError("Result is too large") from None
    except RecursionError:
        raise CalculatorError("That sum is too complicated") from None
    except ValueError:  # e.g. sqrt of a negative number
        raise CalculatorError("No real result for that") from None


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if args:
        try:
            print(calculate(" ".join(args)))
        except CalculatorError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        return 0

    print("Sidi Bou Said calculator - type a sum, or 'q' to quit.")
    while True:
        try:
            line = input("> ")
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if line.strip().lower() in {"q", "quit", "exit"}:
            return 0
        if not line.strip():
            continue
        try:
            print(calculate(line))
        except CalculatorError as exc:
            print(f"Error: {exc}")


if __name__ == "__main__":
    raise SystemExit(main())
