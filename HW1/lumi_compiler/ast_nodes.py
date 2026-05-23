class ASTNode:
    def __repr__(self):
        return f"{self.__class__.__name__}()"

class ProgramNode(ASTNode):
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f"ProgramNode(statements={repr(self.statements)})"

class BlockNode(ASTNode):
    def __init__(self, statements, last_expr=None):
        self.statements = statements
        self.last_expr = last_expr  # 用於支援表達式區塊 (如 if-else 的區塊返回值)

    def __repr__(self):
        return f"BlockNode(statements={repr(self.statements)}, last_expr={repr(self.last_expr)})"

class AssignNode(ASTNode):
    def __init__(self, name: str, expr: ASTNode):
        self.name = name
        self.expr = expr

    def __repr__(self):
        return f"AssignNode(name={repr(self.name)}, expr={repr(self.expr)})"

class WhileNode(ASTNode):
    def __init__(self, condition: ASTNode, body: BlockNode):
        self.condition = condition
        self.body = body

    def __repr__(self):
        return f"WhileNode(condition={repr(self.condition)}, body={repr(self.body)})"

class FuncDefNode(ASTNode):
    def __init__(self, name: str, params: list[str], body: BlockNode):
        self.name = name
        self.params = params
        self.body = body

    def __repr__(self):
        return f"FuncDefNode(name={repr(self.name)}, params={repr(self.params)}, body={repr(self.body)})"

class IfNode(ASTNode):
    def __init__(self, condition: ASTNode, then_branch: BlockNode, else_branch: BlockNode):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def __repr__(self):
        return f"IfNode(condition={repr(self.condition)}, then={repr(self.then_branch)}, else={repr(self.else_branch)})"

class BinOpNode(ASTNode):
    def __init__(self, left: ASTNode, operator: str, right: ASTNode):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f"BinOpNode(left={repr(self.left)}, op={repr(self.operator)}, right={repr(self.right)})"

class LiteralNode(ASTNode):
    def __init__(self, value):
        self.value = value  # 可以是 int, float, str, bool, None

    def __repr__(self):
        return f"LiteralNode(value={repr(self.value)})"

class VarNode(ASTNode):
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"VarNode(name={repr(self.name)})"

class CallNode(ASTNode):
    def __init__(self, callee: str, args: list[ASTNode]):
        self.callee = callee
        self.args = args

    def __repr__(self):
        return f"CallNode(callee={repr(self.callee)}, args={repr(self.args)})"

class PrintNode(ASTNode):
    def __init__(self, expr: ASTNode):
        self.expr = expr

    def __repr__(self):
        return f"PrintNode(expr={repr(self.expr)})"
