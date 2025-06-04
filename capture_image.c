#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/videodev2.h>
#include <sys/mman.h>
#include <string.h>

int capture_image(int camera_index, int res_width, int res_height) {
    char device[20];
    snprintf(device, sizeof(device), "/dev/video%d", camera_index);

    // Open the video device
    int fd = open(device, O_RDWR);
    if (fd == -1) {
        perror("Error: Unable to open video device");
        return -1;
    }

    // Query capabilities
    struct v4l2_capability cap;
    if (ioctl(fd, VIDIOC_QUERYCAP, &cap) < 0) {
        perror("Error: Unable to query capabilities");
        close(fd);
        return -1;
    }

    // Set the format
    struct v4l2_format fmt;
    memset(&fmt, 0, sizeof(fmt));
    fmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    fmt.fmt.pix.width = res_width;  // Set resolution width
    fmt.fmt.pix.height = res_height; // Set resolution height
    fmt.fmt.pix.pixelformat = V4L2_PIX_FMT_MJPEG;  // Set format to MJPEG
    fmt.fmt.pix.field = V4L2_FIELD_INTERLACED;

    if (ioctl(fd, VIDIOC_S_FMT, &fmt) < 0) {
        perror("Error: Unable to set format");
        close(fd);
        return -1;
    }

    // Request buffers
    struct v4l2_requestbuffers reqbuf;
    memset(&reqbuf, 0, sizeof(reqbuf));
    reqbuf.count = 1;
    reqbuf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    reqbuf.memory = V4L2_MEMORY_MMAP;

    if (ioctl(fd, VIDIOC_REQBUFS, &reqbuf) < 0) {
        perror("Error: Unable to request buffers");
        close(fd);
        return -1;
    }

    // Query the buffer
    struct v4l2_buffer buffer;
    memset(&buffer, 0, sizeof(buffer));
    buffer.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    buffer.memory = V4L2_MEMORY_MMAP;
    buffer.index = 0;

    if (ioctl(fd, VIDIOC_QUERYBUF, &buffer) < 0) {
        perror("Error: Unable to query buffer");
        close(fd);
        return -1;
    }

    // Map the buffer
    void *buffer_start = mmap(NULL, buffer.length, PROT_READ | PROT_WRITE, MAP_SHARED, fd, buffer.m.offset);
    if (buffer_start == MAP_FAILED) {
        perror("Error: Unable to map buffer");
        close(fd);
        return -1;
    }

    // Queue the buffer
    if (ioctl(fd, VIDIOC_QBUF, &buffer) < 0) {
        perror("Error: Unable to queue buffer");
        munmap(buffer_start, buffer.length);
        close(fd);
        return -1;
    }

    // Start capturing
    int type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    if (ioctl(fd, VIDIOC_STREAMON, &type) < 0) {
        perror("Error: Unable to start capturing");
        munmap(buffer_start, buffer.length);
        close(fd);
        return -1;
    }

    // Dequeue the buffer
    if (ioctl(fd, VIDIOC_DQBUF, &buffer) < 0) {
        perror("Error: Unable to dequeue buffer");
        munmap(buffer_start, buffer.length);
        close(fd);
        return -1;
    }

    // Write image data to stdout
    fwrite(buffer_start, buffer.length, 1, stdout);

    // Clean up
    munmap(buffer_start, buffer.length);
    ioctl(fd, VIDIOC_STREAMOFF, &type);
    close(fd);

    return 0;
}

int main(int argc, char *argv[]) {
    if (argc != 4) {
        fprintf(stderr, "Usage: %s <camera_index> <res_width> <res_height>\n", argv[0]);
        return -1;
    }

    int camera_index = atoi(argv[1]);
    int res_width = atoi(argv[2]);
    int res_height = atoi(argv[3]);

    int result = capture_image(camera_index, res_width, res_height);
    if (result == 0) {
        fprintf(stderr, "Image captured successfully.\n");
    } else {
        fprintf(stderr, "Failed to capture image.\n");
    }

    return result;
}
