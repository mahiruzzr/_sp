import sys
import os
from lexer import Lexer, LexerError
from parser_impl import Parser, ParserError
from compiler import Compiler
from vm import VM

def print_help():
    print("Lumi 語言工具鏈 CLI")
    print("使用方式:")
    print("  python main.py run <filename.lumi>    - 編譯並執行 Lumi 程式")
    print("  python main.py debug <filename.lumi>  - 以除錯模式運行，列印 Tokens, AST, Bytecode 與執行過程")

def main():
    if len(sys.argv) < 3:
        print_help()
        sys.exit(1)

    command = sys.argv[1]
    filename = sys.argv[2]

    if not os.path.exists(filename):
        print(f"錯誤：找不到檔案 '{filename}'")
        sys.exit(1)

    with open(filename, "r", encoding="utf-8") as f:
        source_code = f.read()

    if command not in ("run", "debug"):
        print_help()
        sys.exit(1)

    try:
        if command == "debug":
            print("--- 原始程式碼 ---")
            print(source_code)
            print("-" * 20)

        # 1. 詞法分析 (Lexer)
        lexer = Lexer(source_code)
        tokens = lexer.scan_tokens()

        if command == "debug":
            print("\n--- 掃描產生的 Tokens ---")
            for token in tokens:
                print(token)
            print("-" * 20)

        # 2. 語法分析 (Parser)
        parser = Parser(tokens)
        ast = parser.parse()

        if command == "debug":
            print("\n--- 剖析產生的 AST 結構 ---")
            print(ast)
            print("-" * 20)

        # 3. 代碼生成 (Compiler)
        compiler = Compiler()
        program = compiler.compile(ast)

        if command == "debug":
            print("\n--- 編譯產生的字節碼 ---")
            print("【全域函數定義】")
            for fn_name, fn_info in program.functions.items():
                print(f"Function '{fn_name}' (params: {fn_info['params']}):")
                for pc, inst in enumerate(fn_info['code']):
                    print(f"  {pc:<3} {inst}")
            print("\n【主程式代碼】")
            for pc, inst in enumerate(program.main_code):
                print(f"  {pc:<3} {inst}")
            print("-" * 20)

        # 4. 虛擬機執行 (VM)
        vm = VM(program)
        vm.run(debug=(command == "debug"))

    except LexerError as e:
        print(f"\n詞法錯誤：{e}")
        sys.exit(1)
    except ParserError as e:
        print(f"\n語法錯誤：{e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"\n執行期錯誤：{e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n系統未預期錯誤：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
