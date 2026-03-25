# p0 編譯器

一個以 C 語言實作的迷你編譯器，支援函數定義、遞迴、if 條件、while 迴圈，並內建虛擬機直接執行產生的中間碼。

---

## 目錄

- [架構概覽](#架構概覽)
- [支援語法](#支援語法)
- [建置與執行](#建置與執行)
- [中間碼（Quadruples）](#中間碼quadruples)
- [函數呼叫機制](#函數呼叫機制)
- [while 語法實作說明](#while-語法實作說明)
- [完整範例](#完整範例)

---

## 架構概覽

p0 分為四個模組，依序串接：

```
原始碼字串
    │
    ▼
┌─────────────┐
│  詞法分析    │  next_token() — 將字元流切成 Token
│   Lexer     │
└──────┬──────┘
       │ Token 流
       ▼
┌─────────────┐
│  語法解析    │  parse_program() / statement() / expression()
│   Parser    │  遞迴下降，邊解析邊 emit 四元式
└──────┬──────┘
       │ Quadruples（quads[]）
       ▼
┌─────────────┐
│  中間碼      │  quads[1000]  每條指令 4 個欄位
│  IR Store   │  op / arg1 / arg2 / result
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  虛擬機      │  vm()  直接解釋執行四元式
│     VM      │  呼叫堆疊 stack[sp]，支援遞迴
└─────────────┘
```

---

## 支援語法

### 變數賦值

```
x = 42;
y = x + 1;
```

### 算術運算

支援 `+`、`-`、`*`、`/`，以及括號改變優先序。

### 比較運算

支援 `==`、`<`、`>`，結果為 0 或 1。

### if 條件

```
if (x < 10) {
    y = y + 1;
}
```

### while 迴圈

```
while (i < 6) {
    sum = sum + i;
    i = i + 1;
}
```

### 函數定義與呼叫

```
func add(a, b) {
    return a + b;
}

result = add(3, 7);
```

支援遞迴呼叫與巢狀函數呼叫。

---

## 建置與執行

```bash
# 編譯
gcc -o p0 p0.c

# 執行
./p0 <source_file>
```

輸出分為兩段：編譯器產生的四元式清單，以及 VM 執行後的全域變數結果。

---

## 中間碼（Quadruples）

每條指令為一筆四欄記錄：`(op, arg1, arg2, result)`。

| 指令 | 說明 | 範例 |
|------|------|------|
| `IMM` | 載入立即數到暫存變數 | `IMM 5 - t1` |
| `STORE` | 將值寫入具名變數 | `STORE t1 - x` |
| `ADD` / `SUB` / `MUL` / `DIV` | 四則運算 | `ADD t1 t2 t3` |
| `CMP_EQ` / `CMP_LT` / `CMP_GT` | 比較，結果存為 0/1 | `CMP_LT i t4 t5` |
| `JMP_F` | 條件為假（0）時跳轉到指定 PC | `JMP_F t5 - 12` |
| `JMP` | 無條件跳轉到指定 PC | `JMP - - 4` |
| `FUNC_BEG` / `FUNC_END` | 函數邊界標記 | `FUNC_BEG fact - -` |
| `FORMAL` | 綁定形式參數 | `FORMAL n - -` |
| `PARAM` | 推入實際引數 | `PARAM t1 - -` |
| `CALL` | 呼叫函數 | `CALL fact 1 t6` |
| `RET_VAL` | 函數回傳值 | `RET_VAL result - -` |

暫存變數以 `t1`、`t2`… 自動命名，VM 輸出結果時會自動隱藏這些內部變數。

---

## 函數呼叫機制

p0 使用**呼叫堆疊**（`stack[]`）搭配四元式實作完整的函數呼叫與遞迴，整體流程分為四個階段。

### 階段一：PARAM — 推入引數

呼叫前，每個引數先求值，再用 `PARAM` 指令壓入 `param_stack`。  
`param_stack` 是獨立於任何 Frame 的全域陣列，確保遞迴時引數不會互相覆蓋。

```
PARAM t1 - -   ← 引數1 入棧
PARAM t2 - -   ← 引數2 入棧
```

### 階段二：CALL — 建立新 Frame

執行 `CALL` 時：

1. `sp++`，在 `stack[sp]` 開啟全新的 Frame
2. 記錄 `ret_pc`（返回後繼續執行的位址）
3. 記錄 `ret_var`（返回值要寫入的變數名稱）
4. 將 `param_stack` 頂端的 N 個值搬入新 Frame 的 `incoming_args[]`
5. 將 `pc` 設為目標函數的入口，開始執行

### 階段三：FORMAL — 綁定形式參數

進入函數本體後，每個 `FORMAL` 指令依序從 `incoming_args[]` 取值，寫入當前 Frame 的區域變數表，完成形參與實參的對應。

```
FORMAL a - -   ← a = incoming_args[0]
FORMAL b - -   ← b = incoming_args[1]
```

### 階段四：RET_VAL — 返回並銷毀 Frame

1. 讀取返回值 `ret_val`
2. 從當前 Frame 取出 `ret_pc` 與 `ret_var`
3. `sp--`，銷毀當前 Frame（區域變數隨之消失）
4. 在上一層 Frame 執行 `set_var(ret_var, ret_val)`，將結果寫回呼叫者
5. `pc = ret_pc`，繼續執行呼叫點後的下一條指令

### 遞迴支援

每次 `CALL` 都讓 `sp++` 建立獨立的 Frame，不同遞迴層的區域變數完全隔離。`RET_VAL` 依序 `sp--` 回捲，每一層都能正確恢復狀態，因此支援任意深度的遞迴（上限為 `stack[1000]`）。

---

## while 語法實作說明

### 修改清單

共修改三個地方，新增四行核心邏輯：

**1. 詞法分析（Lexer）**

在 `TokenType` 加入 `TK_WHILE`，並在 `next_token()` 辨識 `"while"` 關鍵字。

**2. 語法解析（Parser）**

`statement()` 新增 while 分支，使用 **Backpatching** 處理跳轉位址：

```c
} else if (cur_token.type == TK_WHILE) {
    next_token(); next_token();             // skip 'while' '('

    int loop_start = quad_count;            // ① 記住條件判斷的 PC（回跳目標）
    char cond[32]; expression(cond);
    next_token(); next_token();             // skip ')' '{'

    int jmp_out_idx = quad_count;
    emit("JMP_F", cond, "-", "?");         // ② 條件為假跳出，目標先佔位

    while (cur_token.type != TK_RBRACE) statement();
    next_token();                           // skip '}'

    char loop_start_str[16];
    sprintf(loop_start_str, "%d", loop_start);
    emit("JMP", "-", "-", loop_start_str); // ③ 無條件跳回條件判斷

    sprintf(quads[jmp_out_idx].result, "%d", quad_count); // ④ 回填跳出位置
}
```

**3. 虛擬機（VM）**

新增一行處理無條件跳轉：

```c
else if (strcmp(q.op, "JMP") == 0) { pc = atoi(q.result) - 1; }
```

### 產生的中間碼結構

以 `while (i < 6) { ... }` 為例：

```
004: CMP_LT     i          t3         t4        ← loop_start，每次迴圈從這裡開始
005: JMP_F      t4         -          13        ← 條件假則跳到 013（迴圈結束後）
006:   ...迴圈本體...
012: JMP        -          -          4         ← 無條件跳回 004
013: （下一條指令）
```

---

## 完整範例

### 範例一：while 累加

```
i = 1;
sum = 0;
while (i < 6) {
    sum = sum + i;
    i = i + 1;
}
```

執行結果：`sum = 15`

### 範例二：while + 函數（迭代階乘）

```
func factorial(n) {
    result = 1;
    i = 1;
    while (i < n + 1) {
        result = result * i;
        i = i + 1;
    }
    return result;
}

answer = factorial(5);
```

執行結果：`answer = 120`

### 範例三：遞迴函數

```
func fib(n) {
    if (n < 2) {
        return n;
    }
    a = fib(n - 1);
    b = fib(n - 2);
    return a + b;
}

result = fib(7);
```

執行結果：`result = 13`
