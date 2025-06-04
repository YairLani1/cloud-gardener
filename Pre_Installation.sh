#!/bin/bash

# Step 1: Update and install Python
echo "Checking for Python installation..."
sudo apt install -y python3 python3-pip

# Step 2: Clone the GitHub repository (optional, if not already cloned)
# echo "Cloning the repository..."
# git clone <your-github-repo-url>
# cd <your-repo-folder>

# Step 3: Run the C requirements installation script
echo "Running C_requirements.sh..."
chmod +x C_requirements.sh  # Ensure the script is executable
./C_requirements.sh         # Execute the C_requirements.sh script

# Step 4: Install required Python libraries
echo "Installing Python libraries..."
pip3 install -r requirements.txt
chmod +x Tamaguchi.sh
# Step 5: Inform user of successful setup
echo "Pre-installation complete. You can now run your program."
