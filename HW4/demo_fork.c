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
        printf("[Child] PID: %d, Parent PID: %d, fork returned: %d\n",
               getpid(), getppid(), pid);
        sleep(1);
        printf("[Child] exiting\n");
        exit(42);
    } else {
        printf("[Parent] PID: %d, Child PID: %d, fork returned: %d\n",
               getpid(), pid, pid);

        int status;
        waitpid(pid, &status, 0);

        if (WIFEXITED(status))
            printf("[Parent] Child exited with code: %d\n", WEXITSTATUS(status));
    }

    printf("[%d] Both parent and child reach here\n", getpid());
    return 0;
}
