import re

# =========================
# DEFINISI AST NODE
# =========================

class AST:
    pass


class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right


class Num(AST):
    def __init__(self, value):
        self.value = value


class Var(AST):
    def __init__(self, name):
        self.name = name


class ParserError(Exception):
    pass


# =========================
# MINI COMPILER
# =========================

class MiniCompiler:

    def __init__(self, source, env):

        # Lexer / Tokenizer
        # Sudah mendukung operator ^
        self._tokens = iter(
            re.findall(
                r'[a-zA-Z_]\w*|\d+(?:\.\d+)?|[+*/()\-^]',
                source
            ) + ['?']
        )

        self._current = None
        self._env = env

        self._temp_count = 0

        self.advance()

    # =========================
    # TOKEN HANDLER
    # =========================

    def advance(self):
        try:
            self._current = next(self._tokens)
        except StopIteration:
            self._current = None

    def expect(self, expected):

        if self._current != expected and not (
            expected == "ID" and self._current.isalnum()
        ):
            raise ParserError(
                f"Expected {expected}, found {self._current}"
            )

        token = self._current
        self.advance()

        return token

    # =========================
    # FACTOR
    # =========================

    def factor(self):

        token = self._current

        # Number
        if token is not None and token.replace('.', '', 1).isdigit():

            self.advance()

            if '.' in token:
                return Num(float(token))
            else:
                return Num(int(token))

        # Variable
        elif token and token.isalpha():

            # Semantic Analysis
            if token not in self._env:
                raise ParserError(
                    f"Semantic Error: Undefined variable '{token}'"
                )

            self.advance()

            return Var(token)

        # Parentheses
        elif token == '(':

            self.advance()

            node = self.expr()

            self.expect(')')

            return node

        raise ParserError(f"Unexpected token: {token}")

    # =========================
    # POWER (^)
    # =========================

    def power(self):

        node = self.factor()

        while self._current == '^':

            op = self._current

            self.advance()

            node = BinOp(
                left=node,
                op=op,
                right=self.factor()
            )

        return node

    # =========================
    # TERM (* dan /)
    # =========================

    def term(self):

        node = self.power()

        while self._current in ('*', '/'):

            op = self._current

            self.advance()

            node = BinOp(
                left=node,
                op=op,
                right=self.power()
            )

        return node

    # =========================
    # EXPRESSION (+ dan -)
    # =========================

    def expr(self):

        node = self.term()

        while self._current in ('+', '-'):

            op = self._current

            self.advance()

            node = BinOp(
                left=node,
                op=op,
                right=self.term()
            )

        return node

    # =========================
    # GENERATE TAC
    # =========================

    def generate_tac(self, node):

        # Number
        if isinstance(node, Num):
            return str(node.value)

        # Variable
        if isinstance(node, Var):
            return node.name

        # Recursive Generate
        left_val = self.generate_tac(node.left)
        right_val = self.generate_tac(node.right)

        self._temp_count += 1

        temp_name = f"t{self._temp_count}"

        print(f"{temp_name} = {left_val} {node.op} {right_val}")

        return temp_name


# =========================
# MAIN PROGRAM
# =========================

source_code = "a ^ 2 + b * c"

symbol_table = {
    'a': 5,
    'b': 10,
    'c': 2
}

try:

    print("===================================")
    print(" MINI COMPILER - TEKNIK KOMPILASI ")
    print("===================================")

    print(f"\nInput Source Code : {source_code}")

    compiler = MiniCompiler(source_code, symbol_table)

    ast_root = compiler.expr()

    print("\n--- OUTPUT THREE ADDRESS CODE (TAC) ---")

    compiler.generate_tac(ast_root)

    print("\nProgram selesai tanpa error.")

except Exception as e:

    print("\nTerjadi Error:")
    print(e)