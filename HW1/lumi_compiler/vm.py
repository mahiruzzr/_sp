from compiler import Program

class Frame:
    def __init__(self, locals_dict: dict, return_pc: int, return_code: list, prev_frame: 'Frame'):
        self.locals = locals_dict
        self.return_pc = return_pc
        self.return_code = return_code
        self.prev_frame = prev_frame

class VM:
    def __init__(self, program: Program):
        self.program = program
        self.globals = {}
        self.data_stack = []
        self.frame = None
        self.code = program.main_code
        self.pc = 0

    def load_var(self, name: str):
        # 1. 查找區域變數
        if self.frame is not None:
            if name in self.frame.locals:
                return self.frame.locals[name]
        # 2. 查找全域變數
        if name in self.globals:
            return self.globals[name]
        raise RuntimeError(f"Runtime Error: name '{name}' is not defined")

    def store_var(self, name: str, val):
        if self.frame is not None:
            self.frame.locals[name] = val
        else:
            self.globals[name] = val

    def call_function(self, name: str, arg_count: int):
        if name not in self.program.functions:
            raise RuntimeError(f"Runtime Error: function '{name}' is not defined")
            
        fn = self.program.functions[name]
        params = fn["params"]
        
        if len(params) != arg_count:
            raise RuntimeError(f"Runtime Error: function '{name}' expects {len(params)} arguments, got {arg_count}")

        # 從數據棧彈出參數。由於計算順序是從左到右，最右邊的參數在棧頂。
        args = []
        for _ in range(arg_count):
            args.append(self.data_stack.pop())
        args.reverse()

        # 建立新的 Stack Frame
        locals_dict = {param: val for param, val in zip(params, args)}
        
        # 創建並切換 Call Frame，PC 重置為 0，載入函數字節碼
        new_frame = Frame(
            locals_dict=locals_dict,
            return_pc=self.pc,
            return_code=self.code,
            prev_frame=self.frame
        )
        self.frame = new_frame
        self.code = fn["code"]
        self.pc = 0

    def run(self, debug=False):
        if debug:
            print("\n=== VM EXECUTION START ===")
            
        while self.pc < len(self.code):
            inst = self.code[self.pc]
            op = inst[0]
            
            if debug:
                # 打印調用層級的縮排，方便觀察遞迴
                indent = ""
                curr = self.frame
                while curr:
                    indent += "  "
                    curr = curr.prev_frame
                print(f"{indent}PC={self.pc:<3} Inst={str(inst):<30} Stack={repr(self.data_stack)}")

            self.pc += 1  # 推進 PC

            if op == "PUSH_CONST":
                self.data_stack.append(inst[1])

            elif op == "LOAD_VAR":
                name = inst[1]
                self.data_stack.append(self.load_var(name))

            elif op == "STORE_VAR":
                name = inst[1]
                val = self.data_stack.pop()
                self.store_var(name, val)

            elif op == "ADD":
                b = self.data_stack.pop()
                a = self.data_stack.pop()
                self.data_stack.append(a + b)

            elif op == "SUB":
                b = self.data_stack.pop()
                a = self.data_stack.pop()
                self.data_stack.append(a - b)

            elif op == "MUL":
                b = self.data_stack.pop()
                a = self.data_stack.pop()
                self.data_stack.append(a * b)

            elif op == "DIV":
                b = self.data_stack.pop()
                a = self.data_stack.pop()
                if b == 0:
                    raise RuntimeError("Runtime Error: Division by zero")
                self.data_stack.append(a / b)

            elif op == "EQ":
                b = self.data_stack.pop()
                a = self.data_stack.pop()
                self.data_stack.append(a == b)

            elif op == "NE":
                b = self.data_stack.pop()
                a = self.data_stack.pop()
                self.data_stack.append(a != b)

            elif op == "LT":
                b = self.data_stack.pop()
                a = self.data_stack.pop()
                self.data_stack.append(a < b)

            elif op == "LE":
                b = self.data_stack.pop()
                a = self.data_stack.pop()
                self.data_stack.append(a <= b)

            elif op == "GT":
                b = self.data_stack.pop()
                a = self.data_stack.pop()
                self.data_stack.append(a > b)

            elif op == "GE":
                b = self.data_stack.pop()
                a = self.data_stack.pop()
                self.data_stack.append(a >= b)

            elif op == "JUMP":
                self.pc = inst[1]

            elif op == "JUMP_IF_FALSE":
                val = self.data_stack.pop()
                if not val:
                    self.pc = inst[1]

            elif op == "JUMP_IF_TRUE":
                val = self.data_stack.pop()
                if val:
                    self.pc = inst[1]

            elif op == "POP":
                self.data_stack.pop()

            elif op == "PRINT":
                val = self.data_stack.pop()
                print(val)

            elif op == "CALL":
                name = inst[1]
                arg_count = inst[2]
                self.call_function(name, arg_count)

            elif op == "RET":
                if self.frame is None:
                    raise RuntimeError("Runtime Error: Cannot return from global scope")
                # 恢復調用者的狀態。返回值已經在運算棧頂端，不需要彈出。
                self.pc = self.frame.return_pc
                self.code = self.frame.return_code
                self.frame = self.frame.prev_frame

            else:
                raise RuntimeError(f"Runtime Error: Unknown VM instruction '{op}'")

        if debug:
            print("=== VM EXECUTION END ===\n")
