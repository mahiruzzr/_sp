#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>
#include <fcntl.h>

#define MAX_LINE 1024
#define MAX_ARGS 64

typedef struct {
    char *args[MAX_ARGS];
    char *input_file;
    char *output_file;
    int background;
} Command;

void parse_command(char *line, Command *cmd) {
    memset(cmd, 0, sizeof(Command));

    char *tokens[MAX_ARGS];
    int argc = 0;
    char *token = strtok(line, " \t\n");

    while (token && argc < MAX_ARGS - 1) {
        tokens[argc++] = token;
        token = strtok(NULL, " \t\n");
    }
    tokens[argc] = NULL;

    for (int i = 0; i < argc; i++) {
        if (strcmp(tokens[i], "<") == 0 && i + 1 < argc) {
            cmd->input_file = tokens[i + 1];
            tokens[i] = NULL;
        } else if (strcmp(tokens[i], ">") == 0 && i + 1 < argc) {
            cmd->output_file = tokens[i + 1];
            tokens[i] = NULL;
        } else if (strcmp(tokens[i], "&") == 0) {
            cmd->background = 1;
            tokens[i] = NULL;
        }
    }

    int j = 0;
    for (int i = 0; i < argc; i++) {
        if (tokens[i] != NULL)
            cmd->args[j++] = tokens[i];
    }
    cmd->args[j] = NULL;
}

void execute_command(Command *cmd) {
    pid_t pid = fork();

    if (pid < 0) {
        perror("fork failed");
        return;
    }

    if (pid == 0) {
        if (cmd->input_file) {
            int fd = open(cmd->input_file, O_RDONLY);
            if (fd < 0) { perror("open input"); _exit(1); }
            dup2(fd, STDIN_FILENO);
            close(fd);
        }

        if (cmd->output_file) {
            int fd = open(cmd->output_file, O_WRONLY | O_CREAT | O_TRUNC, 0644);
            if (fd < 0) { perror("open output"); _exit(1); }
            dup2(fd, STDOUT_FILENO);
            close(fd);
        }

        execvp(cmd->args[0], cmd->args);
        perror("execvp failed");
        _exit(127);
    }

    if (!cmd->background)
        waitpid(pid, NULL, 0);
    else
        printf("[Background] PID: %d\n", pid);
}

int main() {
    char line[MAX_LINE];
    Command cmd;

    printf("=== Mini Shell ===\n");
    printf("Supports: < input redirect, > output redirect, & background, exit to quit\n\n");

    while (1) {
        printf("shell> ");
        fflush(stdout);

        if (fgets(line, sizeof(line), stdin) == NULL)
            break;

        if (line[0] == '\n')
            continue;

        parse_command(line, &cmd);

        if (cmd.args[0] == NULL)
            continue;

        if (strcmp(cmd.args[0], "exit") == 0)
            break;

        execute_command(&cmd);
    }

    printf("Goodbye!\n");
    return 0;
}
