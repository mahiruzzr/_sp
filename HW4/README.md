# HW4 — Unix 行程與檔案操作 (Process & File I/O)

> 系統程式 習題 6 — 行程與檔案相關程式  
> 涵蓋系統呼叫：`fork`, `execvp`, `open`, `close`, `read`, `write`, `dup2`, `stdin(0)`, `stdout(1)`, `stderr(2)`

---

## 目錄

- [概述](#概述)
- [學習目標](#學習目標)
- [檔案說明](#檔案說明)
- [系統呼叫對照表](#系統呼叫對照表)
- [編譯與執行](#編譯與執行)
- [程式詳解](#程式詳解)
  - [1. demo_fd.c — 基本檔案操作](#1-demofdc--基本檔案操作)
  - [2. demo_fork.c — 行程建立](#2-demoforkc--行程建立)
  - [3. demo_exec.c — 執行程式](#3-demoexecc--執行程式)
  - [4. demo_redirect.c — I/O 重導向](#4-demoredirectc--io-重導向)
  - [5. process_io_demo.c — 完整流程導向](#5-processiodemoc--完整流程導向)
  - [6. mini_shell.c — 簡易 Shell](#6-minishellc--簡易-shell)
- [檔案描述子（File Descriptor）](#檔案描述子file-descriptor)
- [FD 分配規則](#fd-分配規則)
- [參考資料](#參考資料)

---

## 概述

本專案展示 Unix 系統程式中行程管理（Process）與檔案輸入輸出（File I/O）的核心系統呼叫。透過六個由淺入深的範例程式，逐步建立對以下觀念的理解：

- 檔案描述子（File Descriptor, FD）的運作方式
- 行程建立（`fork`）與資源回收（`waitpid`）
- 程式載入與執行（`execvp`）
- I/O 重導向的原理與實作（`dup2`）
- 將上述技術整合為一個簡易 Shell

---

## 學習目標

1. 理解檔案描述子是作業系統管理 I/O 資源的核心機制
2. 掌握 `open/close/read/write` 的基本使用與 FD 分配規則
3. 理解 `fork()` 建立行程的機制與父子行程的行為差異
4. 利用 `execvp()` 在子行程中執行外部程式
5. 使用 `dup2()` 實現標準輸入／輸出的重導向
6. 綜合運用上述技術實作一個微型 Shell

---

## 檔案說明

| 檔案 | 說明 | 難度 |
|------|------|------|
| `demo_fd.c` | 展示 open/close/read/write 基本用法與 FD 分配規則 | ★☆☆ |
| `demo_fork.c` | 展示 fork() 建立子行程、父子行程區分、waitpid 回收 | ★☆☆ |
| `demo_exec.c` | 展示 fork + execvp 經典組合，子行程執行 ls 指令 | ★★☆ |
| `demo_redirect.c` | 展示 dup2 三種用法：stdout、stdin、fork+exec+dup2 | ★★☆ |
| `process_io_demo.c` | 整合 fork + dup2 + execvp，從檔案讀入、寫出到檔案 | ★★★ |
| `mini_shell.c` | 實作支援 `<` `>` `&` `exit` 的簡易 Shell | ★★★ |
| `Makefile` | 編譯、測試、清理 | - |

---

## 系統呼叫對照表

| 系統呼叫 | 功能 | 關鍵概念 | 使用範例 |
|---------|------|---------|---------|
| `open()` | 開啟檔案 | 回傳 FD，最小可用原則 | `open("file", O_RDONLY)` |
| `close()` | 關閉檔案 | 釋放 FD | `close(fd)` |
| `read()` | 從 FD 讀取資料 | 回傳實際讀取 bytes | `read(fd, buf, size)` |
| `write()` | 寫入資料到 FD | 回傳實際寫入 bytes | `write(fd, data, len)` |
| `fork()` | 建立子行程 | 回傳值區分父子行程，Copy-on-Write | `pid_t pid = fork()` |
| `execvp()` | 執行程式 | 取代當前行程映像，結合 fork 使用 | `execvp("ls", args)` |
| `dup2()` | 複製檔案描述子 | 實現 I/O 重導向 | `dup2(fd, STDOUT_FILENO)` |
| `waitpid()` | 等待子行程結束 | 回收子行程資源，取得退出狀態 | `waitpid(pid, &status, 0)` |

---

## 編譯與執行

### 編譯全部

```bash
cd ~/.gemini/HW4
make
```

### 執行自動測試

```bash
make test
```

### 個別編譯與執行

```bash
# 1. 基本檔案操作
gcc -o demo_fd demo_fd.c && ./demo_fd

# 2. 行程建立
gcc -o demo_fork demo_fork.c && ./demo_fork

# 3. 執行程式
gcc -o demo_exec demo_exec.c && ./demo_exec

# 4. I/O 重導向
gcc -o demo_redirect demo_redirect.c && ./demo_redirect

# 5. 完整流程導向
echo "Hello World" > input.txt
gcc -o process_io_demo process_io_demo.c
./process_io_demo input.txt output.txt wc -w
cat output.txt          # 預期輸出: 2

# 6. 簡易 Shell
gcc -o mini_shell mini_shell.c && ./mini_shell
```

### 清理

```bash
make clean
```

---

## 程式詳解

### 1. demo_fd.c — 基本檔案操作

展示 `open` / `close` / `read` / `write` 的基本用法。

```c
int fd = open("test.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
write(fd, "Hello", 5);
close(fd);

fd = open("test.txt", O_RDONLY);
read(fd, buf, sizeof(buf));
close(fd);
```

**FD 分配規則展示：**

```c
close(STDOUT_FILENO);                        // 釋放 FD 1
int new_fd = open("fd_demo.txt", O_WRONLY);  // new_fd == 1（最小可用）
```

> 輸出範例：
> ```
> Opened FD: 3
> Written 24 bytes
> Opened FD: 3
> Read 24 bytes: Hello, File Descriptor!
> 
> === FD Allocation Rule ===
> After close(stdout), open() got FD: 1
> ```

---

### 2. demo_fork.c — 行程建立

展示 `fork()` 建立子行程、父子行程如何透過 `fork()` 回傳值區分、以及 `waitpid` 回收子行程。

```c
pid_t pid = fork();

if (pid == 0) {
    // 子行程：pid == 0
    printf("[Child] PID: %d\n", getpid());
    exit(42);
} else {
    // 父行程：pid == 子行程 ID
    int status;
    waitpid(pid, &status, 0);
    printf("[Parent] Child exited with: %d\n", WEXITSTATUS(status));
}
```

**關鍵觀念：**
- `fork()` 回傳值：父行程得到子行程 PID，子行程得到 0
- 父子行程擁有獨立的位址空間（寫時複製，Copy-on-Write）
- 使用 `waitpid()` 避免殭屍行程（Zombie Process）
- `WIFEXITED` / `WEXITSTATUS` 巨集解析退出狀態

> 輸出範例：
> ```
> [Parent] PID: 348739, Child PID: 348740, fork returned: 348740
> [Child] PID: 348740, Parent PID: 348739, fork returned: 0
> [Child] exiting
> [Parent] Child exited with code: 42
> ```

---

### 3. demo_exec.c — 執行程式

展示 `fork` + `execvp` 的經典組合：子行程執行 `ls -la`，父行程等待。

```c
pid_t pid = fork();

if (pid == 0) {
    char *args[] = {"ls", "-la", NULL};
    execvp("ls", args);        // 取代行程映像
    perror("execvp failed");   // 只有 execvp 失敗才會執行
    _exit(127);
}

waitpid(pid, &status, 0);     // 父行程等待
```

**關鍵觀念：**
- `execvp` 以 PATH 環境變數搜尋執行檔
- 新程式完全取代目前行程映像（程式碼、資料、堆疊全部替換）
- **成功不回傳，失敗回傳 -1**
- PID 保持不變
- 通常與 `fork` 搭配使用：子行程執行新程式，父行程繼續原程式

---

### 4. demo_redirect.c — I/O 重導向

展示 `dup2` 的三種用法。

**stdout 重導向（相當於 `>`）：**

```c
int fd = open("output.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
dup2(fd, STDOUT_FILENO);  // 複製 fd 到 FD 1
close(fd);
// 從此 printf() 的輸出都寫入檔案
```

**stdin 重導向（相當於 `<`）：**

```c
int fd = open("output.txt", O_RDONLY);
dup2(fd, STDIN_FILENO);   // 複製 fd 到 FD 0
close(fd);
// 從此 scanf() / fgets() 都從檔案讀取
```

**fork + exec + dup2 實作 `ls > ls_out.txt`：**

```c
if (fork() == 0) {
    int fd = open("ls_out.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
    dup2(fd, STDOUT_FILENO);
    close(fd);
    execlp("ls", "ls", "-la", NULL);  // ls 的輸出寫入檔案
}
```

---

### 5. process_io_demo.c — 完整流程導向

整合 `fork` + `dup2` + `execvp`，接受命令列參數：

```
Usage: process_io_demo <input_file> <output_file> <cmd> [args...]
```

**執行流程：**

```
┌──────────────────────────────────────────┐
│  1. open(input_file, O_RDONLY)   → fd_in │
│  2. open(output_file, O_WRONLY)  → fd_out│
│  3. fork()                               │
│       ├── child:                         │
│       │   dup2(fd_in,  stdin)            │
│       │   dup2(fd_out, stdout)           │
│       │   execvp(cmd, args)              │
│       └── parent:                        │
│           close(fd_in), close(fd_out)    │
│           waitpid() → print status       │
└──────────────────────────────────────────┘
```

**範例：**

```bash
echo "Hello World" > input.txt
./process_io_demo input.txt output.txt wc -w
cat output.txt   # → 2
```

---

### 6. mini_shell.c — 簡易 Shell

實作一個支援下列功能的簡易 Shell：

- 外部指令執行（`ls`, `cat`, `echo`, `wc` 等）
- 輸入重導向 `<`
- 輸出重導向 `>`
- 背景執行 `&`
- `exit` 離開

**執行範例：**

```
shell> ls
shell> ls > files.txt
shell> cat < files.txt
shell> sleep 10 &
[Background] PID: 12345
shell> exit
```

**實作架構：**

```
main loop:
  print("shell> ")
  fgets(line)                     ← 讀取命令列
  parse_command(line, &cmd)       ← 解析指令、<、>、&
  execute_command(&cmd)           ← fork + exec + redirect
```

**parse_command 解析邏輯：**

```
"ls -la > out.txt < in.txt &"
  → args[]       = {"ls", "-la", NULL}
  → output_file  = "out.txt"
  → input_file   = "in.txt"
  → background   = 1
```

---

## 檔案描述子（File Descriptor）

檔案描述子（FD）是非負整數，作業系統用它來識別行程正在存取的資源。

```
行程 FD 表
┌─────┬─────────────────┐
│ FD  │ 指向             │
├─────┼─────────────────┤
│ 0   │ stdin  (鍵盤)    │
│ 1   │ stdout (螢幕)    │
│ 2   │ stderr (螢幕)    │
│ 3+  │ 開啟的檔案或資源  │
└─────┴─────────────────┘
```

### 三種標準串流

| FD | 常數 | 預設裝置 | 用途 |
|----|------|---------|------|
| 0 | `STDIN_FILENO` | 鍵盤 | 標準輸入 |
| 1 | `STDOUT_FILENO` | 螢幕 | 標準輸出 |
| 2 | `STDERR_FILENO` | 螢幕 | 標準錯誤 |

---

## FD 分配規則

> `open()` 回傳的 FD = 目前最小的可用非負整數

這條規則使得 I/O 重導向成為可能：

```c
close(1);                             // 釋放 FD 1
int fd = open("output.txt", ...);     // fd = 1（覆蓋 stdout！）
// 此後所有 printf() 的輸出自動寫入 output.txt
```

這也是 Shell 中 `>` 和 `<` 運算子的底層實作原理。

---

## 參考資料

1. **UNIX System Calls** — `man 2 open`, `man 2 fork`, `man 2 execvp`, `man 2 dup2`
2. **The C Programming Language (K&R)** — Chapter 8: The UNIX System Interface
3. **Advanced Programming in the UNIX Environment (Stevens)** — Chapters 3, 8
4. **GAMES104 / Piccolo Engine** — BoomingTech Piccolo Engine codebase
5. **Reference Implementations**:
   - [123remus/_sp HW6](https://github.com/123remus/_sp/tree/14f98753d11d59d2aa29260b4deb8ee75db9204c/HW/HW6)
   - [how101081/_sp sp6](https://github.com/how101081/_sp/tree/df4973b75d58d8563c065cfeeee04d6ed1b6693a/homework/sp6)

---

## 授權

本專案僅供教育學習使用。
