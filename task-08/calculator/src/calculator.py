# src/calculator.py

import re


class CalculatorError(Exception):
    pass


def tokenize(expression):
    expression = expression.strip()
    if not expression:
        raise CalculatorError("Error: Empty expression")

    # Regular expression to match numbers (integers and floats) and operators
    # This pattern specifically excludes whitespace, as it's stripped above.
    token_spec = re.compile(r"\d+\.\d+|\d+|[+\-*/()]")

    tokens = []
    last_end = 0
    for match in token_spec.finditer(expression):
        start, end = match.span()
        if start > last_end:
            # There's an unmatched character between the last token and this one
            invalid_char = expression[last_end:start].strip()
            if invalid_char:
                raise CalculatorError(f"Error: Invalid character '{invalid_char[0]}' in expression")
        tokens.append(match.group(0))
        last_end = end

    if last_end < len(expression):
        # There's an unmatched character after the last token
        invalid_char = expression[last_end:].strip()
        if invalid_char:
            raise CalculatorError(f"Error: Invalid character '{invalid_char[0]}' in expression")

    return tokens


def parse_expression(tokens):
    # This is a simplified recursive descent parser for demonstration.
    # It handles addition, subtraction, multiplication, and division,
    # and respects operator precedence.

    if not tokens:
        # This case should ideally be caught by the tokenizer for empty expressions
        # But if somehow it gets here, it's an error.
        raise CalculatorError("Error: Empty expression after tokenization")

    # Helper to consume tokens
    class Parser:
        def __init__(self, tokens):
            self.tokens = tokens
            self.pos = 0

        def current_token(self):
            return self.tokens[self.pos] if self.pos < len(self.tokens) else None

        def advance(self):
            self.pos += 1
            return self.current_token()

        def consume(self, expected_token_type):
            if self.current_token() != expected_token_type:
                raise CalculatorError(f"Error: Expected {expected_token_type}, got {self.current_token()}")
            self.advance()

    parser = Parser(tokens)

    def parse_factor():
        token = parser.current_token()
        if token is None:
            raise CalculatorError("Error: Unexpected end of expression")
        if token == "(":
            parser.consume("(")
            result = parse_expression_recursive()
            parser.consume(")")
            return result
        elif re.match(r"\d+(\.\d+)?", token):
            parser.advance()
            return float(token) if "." in token else int(token)
        else:
            raise CalculatorError(f"Error: Unexpected token: {token}")

    def parse_term():
        result = parse_factor()
        while parser.current_token() in ("*", "/"):
            operator = parser.current_token()
            parser.advance()
            right = parse_factor()
            if operator == "*":
                result *= right
            elif operator == "/":
                if right == 0:
                    raise CalculatorError("Error: Division by zero")
                result /= right
        return result

    def parse_expression_recursive():
        result = parse_term()
        while parser.current_token() in ("+", "-"):
            operator = parser.current_token()
            parser.advance()
            right = parse_term()
            if operator == "+":
                result += right
            elif operator == "-":
                result -= right
        return result

    result = parse_expression_recursive()
    if parser.current_token() is not None:
        raise CalculatorError(f"Error: Unexpected tokens at end of expression: {' '.join(parser.tokens[parser.pos:])}")
    return result


def calculate(expression):
    tokens = tokenize(expression)
    result = parse_expression(tokens)
    return result
