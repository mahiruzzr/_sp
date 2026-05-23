# Lumi 程式語言設計與編譯器/虛擬機實作計劃

本計劃旨在設計一個全新、現代且輕量級的程式語言 **Lumi**，並以 **Python** 實作其完整的編譯器與 Stack-based 虛擬機（VM）。

Lumi 是一個強型態、動態綁定的表達式導向（Expression-oriented）語言。其語法融合了 Rust 的簡潔塊表達式與 Python 的動態特性，不需分號結尾，並使用大括號 `{}` 來界定範疇。

---

## 語言設計規範 (Language Specification)

### 1. 語法範例 (Program Example)

以下是一個在 Lumi 中計算斐波那契數列與累加和的範例：

```lumi
# 變數宣告與賦值
x = 10

# 條件判斷（If-Else 是一個表達式）
y = if x > 5 {
    x * 2
} else {
    5
}

# 函數定義與遞迴
def fib(n) {
    if n <= 1 {
        n
    } else {
        fib(n - 1) + fib(n - 2)
    }
}

# 迴圈與累加
sum = 0
i = 1
while i <= 10 {
    sum = sum + i
    i = i + 1
}

# 輸出結果
print("y is:")
print(y)
print("fib(10) is:")
print(fib(10))
print("sum of 1 to 10 is:")
print(sum)
```

### 2. EBNF 語法定義 (Grammar in EBNF)

```ebnf
program    = { statement } ;
statement  = var_decl | assignment | while_stmt | fn_decl | expr_stmt ;

var_decl   = identifier "=" expr ;
assignment = identifier "=" expr ;
while_stmt = "while" expr block ;
fn_decl    = "def" identifier "(" [ param_list ] ")" block ;
block      = "{" { statement } [ expr ] "}" ;

param_list = identifier { "," identifier } ;
expr_stmt  = expr ;

expr       = if_expr | logic_or ;
if_expr    = "if" expr block "else" ( block | if_expr ) ;

logic_or   = logic_and { "||" logic_and } ;
logic_and  = equality { "&&" equality } ;
equality   = comparison { ( "==" | "!=" ) comparison } ;
comparison = term { ( "<" | "<=" | ">" | ">=" ) term } ;
term       = factor { ( "+" | "-" ) factor } ;
factor     = primary { ( "*" | "/" ) primary } ;
primary    = call | literal | identifier | "(" expr ")" ;

call       = identifier "(" [ arg_list ] ")" ;
arg_list   = expr { "," expr } ;
literal    = number | string | "true" | "false" ;
number     = [ "-" ] digit { digit } [ "." digit { digit } ] ;
string     = '"' { character } '"' ;
```

---

## 系統架構設計 (System Architecture)

Lumi 的工具鏈分為四個核心模組：
1. **Lexer (掃描器)**：將原始碼字串解析成標記流 (Token Stream)。
2. **Parser (剖析器)**：使用遞迴下降法 (Recursive Descent) 解析標記流並建立抽象語法樹 (AST)。
3. **Compiler (編譯器)**：遍歷 AST，將其編譯為適用於 Stack VM 的自訂字節碼 (Bytecode)。
4. **VM (虛擬機)**：一個基於堆疊 (Stack-based) 的虛擬機，具有獨立的 Call Stack 與運算堆疊，負責執行字節碼。

### 虛擬機指令集 (Instruction Set)

| 指令 | 說明 |
| :--- | :--- |
| `PUSH_CONST <value>` | 將常數壓入運算堆疊 |
| `LOAD_VAR <name>` | 從當前 Scope 載入變數值壓入堆疊 |
| `STORE_VAR <name>` | 將堆疊頂端值寫入當前 Scope 的變數 |
| `ADD` / `SUB` / `MUL` / `DIV` | 彈出堆疊頂端兩個值進行算術運算，並將結果壓回 |
| `EQ` / `NE` / `LT` / `LE` / `GT` / `GE` | 彈出堆疊頂端兩個值進行比較，並將布林結果壓回 |
| `JUMP <addr>` | 無條件跳轉到指定位址 |
| `JUMP_IF_FALSE <addr>`| 若堆疊頂端為 False 則跳轉到指定位址 |
| `CALL <name> <arg_count>` | 呼叫函數，將返回位址與環境壓入 Call Stack |
| `RET` | 函數返回，恢復呼叫前狀態 |
| `PRINT` | 彈出堆疊頂端值並印出 |

---

## Proposed Changes

我們將在一個新的子目錄中建立該專案。建議的專案結構如下：

### [NEW] Lumi 專案目錄 (於 scratch/lumi_compiler/ 下)

#### [NEW] [lexer.py](file:///C:/Users/zhangzhengrong/.gemini/antigravity/scratch/lumi_compiler/lexer.py)
實作 Token 定義與 Lexer 類別，負責將原始碼轉為 Token 列表，並能精確報錯（包含行號與列號）。

#### [NEW] [ast_nodes.py](file:///C:/Users/zhangzhengrong/.gemini/antigravity/scratch/lumi_compiler/ast_nodes.py)
定義所有 AST 節點類別，例如 `BinOpNode`, `NumNode`, `VarNode`, `IfNode`, `WhileNode`, `FuncDefNode`, `CallNode` 等。

#### [NEW] [parser_impl.py](file:///C:/Users/zhangzhengrong/.gemini/antigravity/scratch/lumi_compiler/parser_impl.py)
實作遞迴下降剖析器，將 Token 轉換為 AST 樹。

#### [NEW] [compiler.py](file:///C:/Users/zhangzhengrong/.gemini/antigravity/scratch/lumi_compiler/compiler.py)
實作 Bytecode 編譯器，將 AST 轉為一個線性指令列表 (Bytecode Program)，包含符號表管理與標記位址跳轉計算。

#### [NEW] [vm.py](file:///C:/Users/zhangzhengrong/.gemini/antigravity/scratch/lumi_compiler/vm.py)
實作 Stack-based 虛擬機，具有一個指令指標 `pc`、資料堆疊 `data_stack` 和調用棧 `call_stack`。

#### [NEW] [main.py](file:///C:/Users/zhangzhengrong/.gemini/antigravity/scratch/lumi_compiler/main.py)
專案的主入口點。支援以下模式：
* `python main.py run <file.lumi>` - 編譯並執行程式。
* `python main.py debug <file.lumi>` - 列印 Token、AST、編譯後的字節碼以及虛擬機執行過程的堆疊變化。

---

## Verification Plan

### 自動化測試
我們將在 `tests/` 目錄中編寫單元測試與整合測試：
1. **單元測試 (`tests/test_parser.py`)**：驗證 AST 結構是否符合語法預期。
2. **單元測試 (`tests/test_compiler.py`)**：驗證產生的 Bytecode 序列是否正確。
3. **整合測試 (`tests/test_integration.py`)**：準備多個 `.lumi` 檔案（例如斐波那契數列、階乘、迴圈累加），執行後比對標準輸出。

### 手動驗證
1. 執行 `python main.py debug examples/demo.lumi` 觀察整個編譯與 VM 執行追蹤。
2. 故意引入語法錯誤與語義錯誤，確認 Lexer、Parser 與 Compiler 的錯誤處理機制能印出清晰的錯誤訊息。
