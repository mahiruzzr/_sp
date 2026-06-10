# 課程：系統程式 -- 習題總匯

| 欄位 | 內容 |
|------|------|
| 學期 | 114 學年下學期 |
| 學生 | 張政榮 |
| 學號末兩碼 | 46 |
| 教師 | [陳鍾誠](https://www.nqu.edu.tw/educsie/index.php?act=blog&code=list&ids=4) |
| 學校科系 | [金門大學資訊工程系](https://www.nqu.edu.tw/educsie/index.php) |
| 課程教材 | [ccc114b/cpu2os](https://github.com/ccc114b/cpu2os) |
| 作業存放 | [mahiruzzr/_sp](https://github.com/mahiruzzr/_sp) |

---

## 📋 習題概覽

| 習題 | 主題 | 語言 | 使用 AI | 原始 Issue |
|------|------|------|---------|------------|
| **習題一** | p0 編譯器（迷你 C） | C | Antigravity | #1 |
| **習題二** | lumi 編譯器（Python） | Python | Antigravity | #2 |
| **習題三** | 課程倉儲與筆記 | Markdown | Antigravity | #3 |
| **習題四** | 系統程式 Agent 筆記 | Markdown | Antigravity | #4 |
| **習題五** | 多執行緒程式設計 | C++ | [Gemini](https://gemini.google.com/share/a28abe69c2) | #5 |
| **習題六** | Unix 行程與檔案操作 | C | Antigravity | #6 |

> AI 工具：主要使用 **Antigravity**，少部分使用 **OpenCode**。

---

## 🔗 習題連結

| 習題 | 完整檔案 |
|------|---------|
| **習題一 — p0 編譯器** | [`HW/`](https://github.com/mahiruzzr/_sp/tree/ba13b9b715f36a9b9d0ff63f95c6b7e59a69af7d/HW)（`p0.c` + README） |
| **習題二 — lumi 編譯器** | [`HW1/lumi_compiler/`](https://github.com/mahiruzzr/_sp/tree/1b7b34dce5c89fdfc20a901b434dc697fa7e6e5a/HW1/lumi_compiler)（6 個 Python 模組） |
| **習題三 — 課程倉儲** | [`_sp`](https://github.com/mahiruzzr/_sp.git)（Repo 根目錄 + README） |
| **習題四 — Agent 筆記** | [`HW2/`](https://github.com/mahiruzzr/_sp/tree/67200492d95e54da96c7f6b06a882bdecca0a7d0/HW2)（`system_programming_agent_book.MD`） |
| **習題五 — 多執行緒** | [`HW3/`](https://github.com/mahiruzzr/_sp/tree/9ae128b2d2242c59924317f2366c63de3040d70d/HW3)（`1.cpp` ~ `3.cpp` + README） |
| **習題六 — 行程與檔案** | [`HW4/`](https://github.com/mahiruzzr/_sp/tree/c9fb2872536b4a59710b4013d042907a7220b066/HW4)（6 個 C 程式 + Makefile + README） |

---

## 🖥️ 各習題說明

### 習題一 — p0 編譯器（C 語言）

- **資料夾**：[`HW/`](https://github.com/mahiruzzr/_sp/tree/ba13b9b715f36a9b9d0ff63f95c6b7e59a69af7d/HW)
- **語言**：C
- **檔案**：`p0.c`（單一檔案編譯器）
- **架構**：
  - 詞法分析（Lexer）→ 語法解析（Parser）→ 四元式中間碼（IR）→ 虛擬機（VM）
  - 遞迴下降剖析，邊解析邊 emit 四元式
- **支援語法**：變數賦值、四則運算、比較運算、`if` 條件、`while` 迴圈、函數定義與呼叫、遞迴
- **編譯執行**：`gcc -o p0 p0.c && ./p0 <source_file>`

### 習題二 — lumi 編譯器（Python）

- **資料夾**：[`HW1/lumi_compiler/`](https://github.com/mahiruzzr/_sp/tree/1b7b34dce5c89fdfc20a901b434dc697fa7e6e5a/HW1/lumi_compiler)
- **語言**：Python
- **模組架構**：

| 檔案 | 功能 |
|------|------|
| `main.py` | 主程式入口 |
| `lexer.py` | 詞法分析器 |
| `parser_impl.py` | 遞迴下降語法解析器 |
| `ast_nodes.py` | AST 節點定義 |
| `compiler.py` | 編譯器（AST → 中間碼） |
| `vm.py` | 虛擬機執行 |

- **範例程式**：`examples/` 目錄

### 習題三 — 課程倉儲與筆記

- **連結**：[`mahiruzzr/_sp`](https://github.com/mahiruzzr/_sp.git)
- **內容**：GitHub 倉儲建立、課程 README 與習題目錄結構

### 習題四 — 系統程式 Agent 筆記

- **資料夾**：[`HW2/`](https://github.com/mahiruzzr/_sp/tree/67200492d95e54da96c7f6b06a882bdecca0a7d0/HW2)
- **檔案**：`system_programming_agent_book.MD`
- **內容**：系統程式主題的 Agent 筆記 / 教材整理

### 習題五 — 多執行緒並行程式設計

- **資料夾**：[`HW3/`](https://github.com/mahiruzzr/_sp/tree/9ae128b2d2242c59924317f2366c63de3040d70d/HW3)
- **AI 工具**：Gemini → [對話紀錄](https://gemini.google.com/share/a28abe69c2)
- **語言**：C++
- **核心概念**：Thread、Race Condition、Mutex、Deadlock
- **範例程式**：

| # | 主題 | 說明 |
|---|------|------|
| `1.cpp` | 銀行存提款 | Mutex 保護共享餘額，展示 Race Condition 與鎖定 |
| `2.cpp` | 生產者-消費者 | 條件變數 + Mutex 實現緩衝區同步 |
| `3.cpp` | 哲學家用餐 | 多鎖死結預防與資源分級 |

### 習題六 — Unix 行程與檔案操作

- **資料夾**：[`HW4/`](https://github.com/mahiruzzr/_sp/tree/c9fb2872536b4a59710b4013d042907a7220b066/HW4)
- **語言**：C
- **核心系統呼叫**：`fork`, `execvp`, `open`, `close`, `read`, `write`, `dup2`, `waitpid`
- **範例程式**：

| # | 檔案 | 主題 | 難度 |
|---|------|------|------|
| 1 | `demo_fd.c` | 基本檔案操作與 FD 分配規則 | ★☆☆ |
| 2 | `demo_fork.c` | 行程建立與 waitpid 回收 | ★☆☆ |
| 3 | `demo_exec.c` | fork + execvp 執行程式 | ★★☆ |
| 4 | `demo_redirect.c` | dup2 I/O 重導向（三種用法） | ★★☆ |
| 5 | `process_io_demo.c` | fork + dup2 + exec 完整流程 | ★★★ |
| 6 | `mini_shell.c` | 簡易 Shell（支援 `< > & exit`） | ★★★ |

- **編譯**：`make && make test`

---

## 📝 補充說明

- 各習題資料夾內皆有獨立的 `README.md` 詳細說明
- 所有程式皆可編譯執行，並附有測試範例

---

*最後更新：2026 年 6 月*
