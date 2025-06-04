#!/bin/bash

# Update the package list

# Install GCC and essential build tools
echo "Installing GCC and build-essential..."
sudo apt install -y gcc build-essential

# Install V4L2 (Video4Linux2) development headers
echo "Installing V4L2 development headers..."
sudo apt install -y libv4l-dev v4l-utils

# Install other general libraries (if not already installed)
echo "Installing other required libraries..."
sudo apt install -y libc-dev

# Compile the C program
echo "Compiling the C program..."
gcc -o capture_image capture_image.c -lv4l2

echo "Setup complete. The C program has been compiled as 'capture_image'."
