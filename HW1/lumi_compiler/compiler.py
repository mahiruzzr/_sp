from ast_nodes import (
    ASTNode, ProgramNode, BlockNode, AssignNode, WhileNode,
    FuncDefNode, IfNode, BinOpNode, LiteralNode, VarNode, CallNode, PrintNode
)

class Program:
    def __init__(self):
        self.main_code = []
        self.functions = {}  # name -> { "params": [...], "code": [...] }

    def __repr__(self):
        return f"Program(main_code={self.main_code}, functions={self.functions})"

class Compiler:
    def __init__(self):
        self.program = Program()
        self.code = []
        self.label_counter = 0

    def new_label(self, prefix: str) -> str:
        self.label_counter += 1
        return f"{prefix}_{self.label_counter}"

    def emit(self, op: str, *args):
        self.code.append((op, *args))

    def emit_label(self, name: str):
        self.code.append(("LABEL", name))

    def compile(self, ast: ProgramNode) -> Program:
        # 編譯主程式
        for stmt in ast.statements:
            self.compile_node(stmt)
            # 如果主程式中的陳述句是純表達式，編譯後需將結果彈出以保持堆疊乾淨
            is_expr_stmt = not isinstance(stmt, (AssignNode, WhileNode, FuncDefNode, PrintNode))
            if is_expr_stmt:
                self.emit("POP")

        self.program.main_code = self.resolve_labels(self.code)
        return self.program

    def compile_node(self, node: ASTNode):
        if isinstance(node, LiteralNode):
            self.emit("PUSH_CONST", node.value)

        elif isinstance(node, VarNode):
            self.emit("LOAD_VAR", node.name)

        elif isinstance(node, AssignNode):
            self.compile_node(node.expr)
            self.emit("STORE_VAR", node.name)

        elif isinstance(node, PrintNode):
            self.compile_node(node.expr)
            self.emit("PRINT")

        elif isinstance(node, BlockNode):
            # 編譯區塊內的所有陳述句
            for stmt in node.statements:
                self.compile_node(stmt)
                is_expr_stmt = not isinstance(stmt, (AssignNode, WhileNode, FuncDefNode, PrintNode))
                if is_expr_stmt:
                    self.emit("POP")
            
            # 如果有最後的返回值表達式，編譯之
            if node.last_expr is not None:
                self.compile_node(node.last_expr)

        elif isinstance(node, IfNode):
            else_label = self.new_label("else")
            end_label = self.new_label("end")

            # 編譯條件
            self.compile_node(node.condition)
            self.emit("JUMP_IF_FALSE", else_label)

            # 編譯 then 分支
            self.compile_node(node.then_branch)
            # 若 then 區塊無返回值，則壓入 None 保持堆疊平衡
            if node.then_branch.last_expr is None:
                self.emit("PUSH_CONST", None)
            self.emit("JUMP", end_label)

            # 編譯 else 分支
            self.emit_label(else_label)
            self.compile_node(node.else_branch)
            if node.else_branch.last_expr is None:
                self.emit("PUSH_CONST", None)

            self.emit_label(end_label)

        elif isinstance(node, WhileNode):
            start_label = self.new_label("while_start")
            end_label = self.new_label("while_end")

            self.emit_label(start_label)
            self.compile_node(node.condition)
            self.emit("JUMP_IF_FALSE", end_label)

            # 編譯迴圈主體
            self.compile_node(node.body)
            # 迴圈體若有返回值則丟棄
            if node.body.last_expr is not None:
                self.emit("POP")

            self.emit("JUMP", start_label)
            self.emit_label(end_label)

        elif isinstance(node, FuncDefNode):
            # 保存當前的程式碼緩衝區
            old_code = self.code
            self.code = []

            # 編譯函數體
            self.compile_node(node.body)
            # 若函數體無最後表達式，預設返回 None
            if node.body.last_expr is None:
                self.emit("PUSH_CONST", None)
            self.emit("RET")

            # 解析函數內部的標籤
            fn_code = self.resolve_labels(self.code)
            self.program.functions[node.name] = {
                "params": node.params,
                "code": fn_code
            }

            # 恢復原本的程式碼緩衝區
            self.code = old_code

        elif isinstance(node, CallNode):
            # 依序編譯參數，將它們壓入堆疊
            for arg in node.args:
                self.compile_node(arg)
            self.emit("CALL", node.callee, len(node.args))

        elif isinstance(node, BinOpNode):
            # 處理短路邏輯
            if node.operator == "&&":
                false_label = self.new_label("and_false")
                end_label = self.new_label("and_end")

                self.compile_node(node.left)
                self.emit("JUMP_IF_FALSE", false_label)
                self.compile_node(node.right)
                self.emit("JUMP", end_label)

                self.emit_label(false_label)
                self.emit("PUSH_CONST", False)
                self.emit_label(end_label)

            elif node.operator == "||":
                true_label = self.new_label("or_true")
                end_label = self.new_label("or_end")

                self.compile_node(node.left)
                self.emit("JUMP_IF_TRUE", true_label)
                self.compile_node(node.right)
                self.emit("JUMP", end_label)

                self.emit_label(true_label)
                self.emit("PUSH_CONST", True)
                self.emit_label(end_label)

            else:
                # 一般二元運算
                self.compile_node(node.left)
                self.compile_node(node.right)
                
                op_map = {
                    "+": "ADD",
                    "-": "SUB",
                    "*": "MUL",
                    "/": "DIV",
                    "==": "EQ",
                    "!=": "NE",
                    "<": "LT",
                    "<=": "LE",
                    ">": "GT",
                    ">=": "GE",
                }
                self.emit(op_map[node.operator])

    def resolve_labels(self, raw_code: list) -> list:
        # 第一階段：記錄標籤的位置，並過濾掉 LABEL 指令
        labels = {}
        resolved_code = []
        for inst in raw_code:
            if inst[0] == "LABEL":
                labels[inst[1]] = len(resolved_code)
            else:
                resolved_code.append(inst)

        # 第二階段：將跳轉指令中的標籤名稱替換為絕對偏移量 (PC 位址)
        final_code = []
        for inst in resolved_code:
            op = inst[0]
            if op in ("JUMP", "JUMP_IF_FALSE", "JUMP_IF_TRUE"):
                label_name = inst[1]
                final_code.append((op, labels[label_name]))
            else:
                final_code.append(inst)

        return final_code
