import enum

class TokenType(enum.Enum):
    # 關鍵字
    DEF = "def"
    IF = "if"
    ELSE = "else"
    WHILE = "while"
    TRUE = "true"
    FALSE = "false"
    PRINT = "print"
    
    # 字面量
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"
    STRING = "STRING"
    
    # 運算子
    ASSIGN = "="
    PLUS = "+"
    MINUS = "-"
    MUL = "*"
    DIV = "/"
    EQ = "=="
    NE = "!="
    LT = "<"
    LE = "<="
    GT = ">"
    GE = ">="
    AND = "&&"
    OR = "||"
    
    # 分隔符
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    COMMA = ","
    
    # 特殊
    EOF = "EOF"

class Token:
    def __init__(self, type_: TokenType, value: str, line: int, column: int):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type.name}, {repr(self.value)}, line={self.line}, col={self.column})"

class LexerError(Exception):
    def __init__(self, message, line, column):
        super().__init__(f"Lexer Error at line {line}, column {column}: {message}")
        self.line = line
        self.column = column

class Lexer:
    KEYWORDS = {
        "def": TokenType.DEF,
        "if": TokenType.IF,
        "else": TokenType.ELSE,
        "while": TokenType.WHILE,
        "true": TokenType.TRUE,
        "false": TokenType.FALSE,
        "print": TokenType.PRINT,
    }

    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.length = len(source)

    def peek(self, offset=0) -> str:
        if self.position + offset >= self.length:
            return '\0'
        return self.source[self.position + offset]

    def advance(self) -> str:
        char = self.peek()
        self.position += 1
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char

    def match(self, expected: str) -> bool:
        if self.peek() == expected:
            self.advance()
            return True
        return False

    def scan_tokens(self) -> list[Token]:
        tokens = []
        while self.position < self.length:
            char = self.peek()
            
            # 跳過空白字元
            if char in (' ', '\t', '\r', '\n'):
                self.advance()
                continue
                
            # 跳過註解 (以 # 開頭)
            if char == '#':
                while self.peek() != '\n' and self.peek() != '\0':
                    self.advance()
                continue

            # 記錄當前 Token 開始的行列號
            start_line = self.line
            start_col = self.column

            # 雙字元/單字元運算子
            if char == '=':
                self.advance()
                if self.match('='):
                    tokens.append(Token(TokenType.EQ, "==", start_line, start_col))
                else:
                    tokens.append(Token(TokenType.ASSIGN, "=", start_line, start_col))
            elif char == '!':
                self.advance()
                if self.match('='):
                    tokens.append(Token(TokenType.NE, "!=", start_line, start_col))
                else:
                    raise LexerError("Unexpected character '!' (did you mean '!='?)", start_line, start_col)
            elif char == '<':
                self.advance()
                if self.match('='):
                    tokens.append(Token(TokenType.LE, "<=", start_line, start_col))
                else:
                    tokens.append(Token(TokenType.LT, "<", start_line, start_col))
            elif char == '>':
                self.advance()
                if self.match('='):
                    tokens.append(Token(TokenType.GE, ">=", start_line, start_col))
                else:
                    tokens.append(Token(TokenType.GT, ">", start_line, start_col))
            elif char == '&':
                self.advance()
                if self.match('&'):
                    tokens.append(Token(TokenType.AND, "&&", start_line, start_col))
                else:
                    raise LexerError("Unexpected character '&' (did you mean '&&'?)", start_line, start_col)
            elif char == '|':
                self.advance()
                if self.match('|'):
                    tokens.append(Token(TokenType.OR, "||", start_line, start_col))
                else:
                    raise LexerError("Unexpected character '|' (did you mean '||'?)", start_line, start_col)
            
            # 單字元符號
            elif char == '+':
                self.advance()
                tokens.append(Token(TokenType.PLUS, "+", start_line, start_col))
            elif char == '-':
                self.advance()
                tokens.append(Token(TokenType.MINUS, "-", start_line, start_col))
            elif char == '*':
                self.advance()
                tokens.append(Token(TokenType.MUL, "*", start_line, start_col))
            elif char == '/':
                self.advance()
                tokens.append(Token(TokenType.DIV, "/", start_line, start_col))
            elif char == '(':
                self.advance()
                tokens.append(Token(TokenType.LPAREN, "(", start_line, start_col))
            elif char == ')':
                self.advance()
                tokens.append(Token(TokenType.RPAREN, ")", start_line, start_col))
            elif char == '{':
                self.advance()
                tokens.append(Token(TokenType.LBRACE, "{", start_line, start_col))
            elif char == '}':
                self.advance()
                tokens.append(Token(TokenType.RBRACE, "}", start_line, start_col))
            elif char == ',':
                self.advance()
                tokens.append(Token(TokenType.COMMA, ",", start_line, start_col))

            # 字串字面量
            elif char == '"':
                tokens.append(self.scan_string())

            # 數字字面量
            elif char.isdigit():
                tokens.append(self.scan_number())

            # 識別碼或關鍵字
            elif char.isalpha() or char == '_':
                tokens.append(self.scan_identifier())

            else:
                self.advance()
                raise LexerError(f"Unexpected character '{char}'", start_line, start_col)

        tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return tokens

    def scan_string(self) -> Token:
        start_line = self.line
        start_col = self.column
        self.advance() # 跳過開頭的雙引號 `"`
        
        string_val = []
        while self.peek() != '"' and self.peek() != '\0':
            # 支援基本逸出字元
            if self.peek() == '\\':
                self.advance()
                escaped = self.advance()
                if escaped == 'n':
                    string_val.append('\n')
                elif escaped == 't':
                    string_val.append('\t')
                elif escaped == '\\':
                    string_val.append('\\')
                elif escaped == '"':
                    string_val.append('"')
                else:
                    string_val.append('\\')
                    string_val.append(escaped)
            else:
                string_val.append(self.advance())

        if self.peek() == '\0':
            raise LexerError("Unterminated string literal", start_line, start_col)
            
        self.advance() # 跳過結尾的雙引號 `"`
        return Token(TokenType.STRING, "".join(string_val), start_line, start_col)

    def scan_number(self) -> Token:
        start_line = self.line
        start_col = self.column
        
        num_str = []
        while self.peek().isdigit():
            num_str.append(self.advance())
            
        # 處理浮點數
        if self.peek() == '.' and self.peek(1).isdigit():
            num_str.append(self.advance()) # 壓入 '.'
            while self.peek().isdigit():
                num_str.append(self.advance())
                
        return Token(TokenType.NUMBER, "".join(num_str), start_line, start_col)

    def scan_identifier(self) -> Token:
        start_line = self.line
        start_col = self.column
        
        ident_str = []
        while self.peek().isalnum() or self.peek() == '_':
            ident_str.append(self.advance())
            
        value = "".join(ident_str)
        # 判斷是否為關鍵字
        token_type = self.KEYWORDS.get(value, TokenType.IDENTIFIER)
        return Token(token_type, value, start_line, start_col)
