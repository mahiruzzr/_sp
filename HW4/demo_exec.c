#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

int main() {
    pid_t pid = fork();

    if (pid < 0) {
        perror("fork failed");
        exit(1);
    }

    if (pid == 0) {
        printf("[Child] Before exec (PID: %d)\n", getpid());

        char *args[] = {"ls", "-la", NULL};
        execvp("ls", args);

        perror("execvp failed");
        _exit(127);
    }

    int status;
    waitpid(pid, &status, 0);

    if (WIFEXITED(status))
        printf("\n[Parent] Child exited with code: %d\n", WEXITSTATUS(status));

    return 0;
}
