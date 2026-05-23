from lexer import Token, TokenType
from ast_nodes import (
    ASTNode, ProgramNode, BlockNode, AssignNode, WhileNode,
    FuncDefNode, IfNode, BinOpNode, LiteralNode, VarNode, CallNode, PrintNode
)

class ParserError(Exception):
    def __init__(self, message, line, column):
        super().__init__(f"Parser Error at line {line}, column {column}: {message}")
        self.line = line
        self.column = column

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0

    def peek(self, offset=0) -> Token:
        if self.current + offset >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.current + offset]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def is_at_end(self) -> bool:
        return self.peek().type == TokenType.EOF

    def check(self, type_: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().type == type_

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def match(self, *types: TokenType) -> bool:
        for type_ in types:
            if self.check(type_):
                self.advance()
                return True
        return False

    def consume(self, type_: TokenType, message: str) -> Token:
        if self.check(type_):
            return self.advance()
        token = self.peek()
        raise ParserError(message, token.line, token.column)

    def parse(self) -> ProgramNode:
        statements = []
        while not self.is_at_end():
            statements.append(self.statement())
        return ProgramNode(statements)

    def statement(self) -> ASTNode:
        if self.match(TokenType.DEF):
            return self.function_declaration()
        if self.match(TokenType.WHILE):
            return self.while_statement()
        if self.match(TokenType.PRINT):
            return self.print_statement()
        
        # 使用 LL(2) 判斷是否為變數賦值 (IDENTIFIER = expr)
        if self.check(TokenType.IDENTIFIER) and self.peek(1).type == TokenType.ASSIGN:
            return self.assignment()

        # 否則作為表達式陳述句
        return self.expression()

    def function_declaration(self) -> FuncDefNode:
        name_token = self.consume(TokenType.IDENTIFIER, "Expect function name.")
        self.consume(TokenType.LPAREN, "Expect '(' after function name.")
        params = []
        if not self.check(TokenType.RPAREN):
            param_token = self.consume(TokenType.IDENTIFIER, "Expect parameter name.")
            params.append(param_token.value)
            while self.match(TokenType.COMMA):
                param_token = self.consume(TokenType.IDENTIFIER, "Expect parameter name.")
                params.append(param_token.value)
        self.consume(TokenType.RPAREN, "Expect ')' after parameters.")
        body = self.block()
        return FuncDefNode(name_token.value, params, body)

    def while_statement(self) -> WhileNode:
        condition = self.expression()
        body = self.block()
        return WhileNode(condition, body)

    def print_statement(self) -> PrintNode:
        self.consume(TokenType.LPAREN, "Expect '(' after 'print'.")
        expr = self.expression()
        self.consume(TokenType.RPAREN, "Expect ')' after print expression.")
        return PrintNode(expr)

    def assignment(self) -> AssignNode:
        name_token = self.consume(TokenType.IDENTIFIER, "Expect identifier.")
        self.consume(TokenType.ASSIGN, "Expect '=' after identifier.")
        expr = self.expression()
        return AssignNode(name_token.value, expr)

    def block(self) -> BlockNode:
        self.consume(TokenType.LBRACE, "Expect '{' before block.")
        statements = []
        last_expr = None
        
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            stmt = self.statement()
            # 如果下一個 Token 是 '}'，且當前陳述句是一個表達式，則將其作為塊的返回值
            is_expression = not isinstance(stmt, (AssignNode, WhileNode, FuncDefNode, PrintNode))
            if self.check(TokenType.RBRACE) and is_expression:
                last_expr = stmt
            else:
                statements.append(stmt)
                
        self.consume(TokenType.RBRACE, "Expect '}' after block.")
        return BlockNode(statements, last_expr)

    def expression(self) -> ASTNode:
        if self.match(TokenType.IF):
            return self.if_expression()
        return self.logic_or()

    def if_expression(self) -> IfNode:
        condition = self.expression()
        then_branch = self.block()
        self.consume(TokenType.ELSE, "Expect 'else' after if branch.")
        
        # 支援 else if
        if self.match(TokenType.IF):
            nested_if = self.if_expression()
            # 將 else if 的 if 表達式包裝在一個 Block 中作為 else 分支
            else_branch = BlockNode([], nested_if)
        else:
            else_branch = self.block()
            
        return IfNode(condition, then_branch, else_branch)

    def logic_or(self) -> ASTNode:
        expr = self.logic_and()
        while self.match(TokenType.OR):
            op = self.previous().value
            right = self.logic_and()
            expr = BinOpNode(expr, op, right)
        return expr

    def logic_and(self) -> ASTNode:
        expr = self.equality()
        while self.match(TokenType.AND):
            op = self.previous().value
            right = self.equality()
            expr = BinOpNode(expr, op, right)
        return expr

    def equality(self) -> ASTNode:
        expr = self.comparison()
        while self.match(TokenType.EQ, TokenType.NE):
            op = self.previous().value
            right = self.comparison()
            expr = BinOpNode(expr, op, right)
        return expr

    def comparison(self) -> ASTNode:
        expr = self.term()
        while self.match(TokenType.LT, TokenType.LE, TokenType.GT, TokenType.GE):
            op = self.previous().value
            right = self.term()
            expr = BinOpNode(expr, op, right)
        return expr

    def term(self) -> ASTNode:
        expr = self.factor()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op = self.previous().value
            right = self.factor()
            expr = BinOpNode(expr, op, right)
        return expr

    def factor(self) -> ASTNode:
        expr = self.unary()
        while self.match(TokenType.MUL, TokenType.DIV):
            op = self.previous().value
            right = self.unary()
            expr = BinOpNode(expr, op, right)
        return expr

    def unary(self) -> ASTNode:
        if self.match(TokenType.MINUS):
            op = self.previous().value
            right = self.unary()
            # 將單元負號 -x 優雅地轉換為 0 - x，簡化 VM 指令集與編譯器
            return BinOpNode(LiteralNode(0), op, right)
        return self.primary()

    def primary(self) -> ASTNode:
        if self.match(TokenType.TRUE):
            return LiteralNode(True)
        if self.match(TokenType.FALSE):
            return LiteralNode(False)
        if self.match(TokenType.NUMBER):
            val = self.previous().value
            if '.' in val:
                return LiteralNode(float(val))
            return LiteralNode(int(val))
        if self.match(TokenType.STRING):
            return LiteralNode(self.previous().value)
            
        if self.match(TokenType.IDENTIFIER):
            name = self.previous().value
            # 判斷是否為函數呼叫 (IDENTIFIER "(" args ")")
            if self.match(TokenType.LPAREN):
                args = []
                if not self.check(TokenType.RPAREN):
                    args.append(self.expression())
                    while self.match(TokenType.COMMA):
                        args.append(self.expression())
                self.consume(TokenType.RPAREN, "Expect ')' after arguments.")
                return CallNode(name, args)
            return VarNode(name)
            
        if self.match(TokenType.LPAREN):
            expr = self.expression()
            self.consume(TokenType.RPAREN, "Expect ')' after expression.")
            return expr
            
        token = self.peek()
        raise ParserError(f"Unexpected token {token.value} in expression", token.line, token.column)
