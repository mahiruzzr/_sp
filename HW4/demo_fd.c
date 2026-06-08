#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>

int main() {
    const char *filename = "test.txt";
    const char *msg = "Hello, File Descriptor!\n";

    int fd = open(filename, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) {
        perror("open write failed");
        exit(1);
    }
    printf("Opened FD: %d\n", fd);

    ssize_t written = write(fd, msg, strlen(msg));
    printf("Written %zd bytes\n", written);
    close(fd);

    fd = open(filename, O_RDONLY);
    if (fd < 0) {
        perror("open read failed");
        exit(1);
    }
    printf("Opened FD: %d\n", fd);

    char buf[256] = {0};
    ssize_t bytes = read(fd, buf, sizeof(buf) - 1);
    printf("Read %zd bytes: %s", bytes, buf);
    close(fd);

    printf("\n=== FD Allocation Rule ===\n");
    close(STDOUT_FILENO);
    int new_fd = open("fd_demo.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
    printf("After close(stdout), open() got FD: %d\n", new_fd);
    close(new_fd);

    return 0;
}
