import unittest
import sys
import io
import os

# 將專案路徑加入 sys.path 以便匯入模組
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer import Lexer, TokenType, LexerError
from parser_impl import Parser, ParserError
from compiler import Compiler
from vm import VM
from ast_nodes import LiteralNode, BinOpNode, ProgramNode

class TestLexer(unittest.TestCase):
    def test_basic_tokens(self):
        source = 'x = 10 + 20 * "hello" # 這是註解\nprint(x)'
        lexer = Lexer(source)
        tokens = lexer.scan_tokens()
        
        # 預期 Tokens: IDENTIFIER(x), ASSIGN(=), NUMBER(10), PLUS(+), NUMBER(20), MUL(*), STRING(hello), PRINT, LPAREN, IDENTIFIER(x), RPAREN, EOF
        expected_types = [
            TokenType.IDENTIFIER, TokenType.ASSIGN, TokenType.NUMBER, TokenType.PLUS,
            TokenType.NUMBER, TokenType.MUL, TokenType.STRING,
            TokenType.PRINT, TokenType.LPAREN, TokenType.IDENTIFIER, TokenType.RPAREN,
            TokenType.EOF
        ]
        self.assertEqual([t.type for t in tokens], expected_types)
        self.assertEqual(tokens[0].value, "x")
        self.assertEqual(tokens[2].value, "10")
        self.assertEqual(tokens[6].value, "hello")

    def test_lexer_errors(self):
        with self.assertRaises(LexerError):
            Lexer('x = 10 @ 20').scan_tokens()
        with self.assertRaises(LexerError):
            Lexer('x = "unterminated').scan_tokens()


class TestParser(unittest.TestCase):
    def test_expression_precedence(self):
        # 1 + 2 * 3 應解析為 1 + (2 * 3) 而不是 (1 + 2) * 3
        lexer = Lexer("1 + 2 * 3")
        parser = Parser(lexer.scan_tokens())
        ast = parser.parse()
        
        self.assertIsInstance(ast, ProgramNode)
        self.assertEqual(len(ast.statements), 1)
        expr = ast.statements[0]
        
        self.assertIsInstance(expr, BinOpNode)
        self.assertEqual(expr.operator, "+")
        self.assertIsInstance(expr.left, LiteralNode)
        self.assertEqual(expr.left.value, 1)
        self.assertIsInstance(expr.right, BinOpNode)
        self.assertEqual(expr.right.operator, "*")

    def test_parser_errors(self):
        with self.assertRaises(ParserError):
            Parser(Lexer("if x > 5 { 10").scan_tokens()).parse()  # 缺少的 }


class TestCompilerAndVM(unittest.TestCase):
    def run_lumi_code(self, source: str) -> str:
        # 重導向 stdout 以擷取 print 的結果
        lexer = Lexer(source)
        parser = Parser(lexer.scan_tokens())
        ast = parser.parse()
        compiler = Compiler()
        program = compiler.compile(ast)
        
        vm = VM(program)
        captured_output = io.StringIO()
        sys.stdout = captured_output
        try:
            vm.run()
        finally:
            sys.stdout = sys.__stdout__
        return captured_output.getvalue().strip()

    def test_arithmetic(self):
        code = "print((10 + 2) * 3 - 6 / 2)"
        output = self.run_lumi_code(code)
        # (12) * 3 - 3 = 36 - 3 = 33
        self.assertEqual(float(output), 33.0)

    def test_if_expression(self):
        code = """
        x = 10
        y = if x > 5 {
            100
        } else {
            200
        }
        print(y)
        """
        output = self.run_lumi_code(code)
        self.assertEqual(output, "100")

    def test_while_loop(self):
        code = """
        sum = 0
        i = 1
        while i <= 5 {
            sum = sum + i
            i = i + 1
        }
        print(sum)
        """
        output = self.run_lumi_code(code)
        self.assertEqual(output, "15")

    def test_recursive_function(self):
        code = """
        def factorial(n) {
            if n <= 1 {
                1
            } else {
                n * factorial(n - 1)
            }
        }
        print(factorial(5))
        """
        output = self.run_lumi_code(code)
        self.assertEqual(output, "120")

    def test_short_circuit_logic(self):
        code = """
        print(true || false)
        print(true && false)
        print(false && (1 / 0 == 0)) # 應短路，不應發生除以零錯誤
        """
        output = self.run_lumi_code(code).split('\n')
        self.assertEqual(output[0], "True")
        self.assertEqual(output[1], "False")
        self.assertEqual(output[2], "False")

if __name__ == "__main__":
    unittest.main()
