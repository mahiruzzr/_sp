#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <string.h>

#define BUFFER_SIZE 4096

void error_exit(const char *msg) {
    write(STDERR_FILENO, msg, strlen(msg));
    write(STDERR_FILENO, "\n", 1);
    exit(EXIT_FAILURE);
}

int main(int argc, char *argv[]) {
    if (argc < 4) {
        const char *usage = "Usage: process_io_demo <input_file> <output_file> <cmd> [args...]";
        write(STDERR_FILENO, usage, strlen(usage));
        write(STDERR_FILENO, "\n", 1);
        exit(EXIT_FAILURE);
    }

    const char *input_file  = argv[1];
    const char *output_file = argv[2];
    char **cmd_argv = argv + 3;

    int fd_in  = open(input_file, O_RDONLY);
    if (fd_in < 0) error_exit("Failed to open input file");

    int fd_out = open(output_file, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd_out < 0) {
        close(fd_in);
        error_exit("Failed to open output file");
    }

    pid_t pid = fork();
    if (pid < 0) {
        close(fd_in);
        close(fd_out);
        error_exit("fork failed");
    }

    if (pid == 0) {
        if (dup2(fd_in, STDIN_FILENO) < 0)
            error_exit("dup2 stdin failed");
        if (dup2(fd_out, STDOUT_FILENO) < 0)
            error_exit("dup2 stdout failed");

        close(fd_in);
        close(fd_out);

        execvp(cmd_argv[0], cmd_argv);
        error_exit("execvp failed");
    } else {
        close(fd_in);
        close(fd_out);

        int status;
        waitpid(pid, &status, 0);

        if (WIFEXITED(status)) {
            char buf[64];
            int n = snprintf(buf, sizeof(buf),
                             "Child exited with status %d\n",
                             WEXITSTATUS(status));
            write(STDOUT_FILENO, buf, n);
        }
    }

    return 0;
}
