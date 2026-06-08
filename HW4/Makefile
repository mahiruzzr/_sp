CC = gcc
CFLAGS = -Wall -Wextra -g

TARGETS = process_io_demo demo_fd demo_fork demo_exec demo_redirect mini_shell

all: $(TARGETS)

process_io_demo: process_io_demo.c
	$(CC) $(CFLAGS) -o $@ $^

demo_fd: demo_fd.c
	$(CC) $(CFLAGS) -o $@ $^

demo_fork: demo_fork.c
	$(CC) $(CFLAGS) -o $@ $^

demo_exec: demo_exec.c
	$(CC) $(CFLAGS) -o $@ $^

demo_redirect: demo_redirect.c
	$(CC) $(CFLAGS) -o $@ $^

mini_shell: mini_shell.c
	$(CC) $(CFLAGS) -o $@ $^

clean:
	rm -f $(TARGETS) *.txt

test: all
	@echo "=== test process_io_demo ==="
	echo "Hello World" > input.txt
	./process_io_demo input.txt output.txt wc -w
	cat output.txt
	@echo ""
	@echo "=== test demo_fd ==="
	./demo_fd
	@echo ""
	@echo "=== test demo_fork ==="
	./demo_fork
	@echo ""
	@echo "=== test demo_exec ==="
	./demo_exec
	@echo ""
	@echo "=== test demo_redirect ==="
	./demo_redirect
	@echo ""
	@echo "=== test mini_shell (manual) ==="
	@echo "Run: ./mini_shell"

.PHONY: all clean test
