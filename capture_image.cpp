#include <opencv2/opencv.hpp>
#include <iostream>

int main() {
    // Open the default camera (0 for the first USB camera).
    cv::VideoCapture cap(0);
    if (!cap.isOpened()) {
        std::cerr << "Error: Unable to access the USB camera!" << std::endl;
        return -1;
    }

    // Set the resolution (optional, adjust based on your camera's capability).
    cap.set(cv::CAP_PROP_FRAME_WIDTH, 640);
    cap.set(cv::CAP_PROP_FRAME_HEIGHT, 480);

    // Create a Mat object to hold the captured frame.
    cv::Mat frame;

    std::cout << "Press any key to capture a frame..." << std::endl;

    // Wait for a key press to capture a frame.
    while (true) {
        cap >> frame; // Capture a frame.
        if (frame.empty()) {
            std::cerr << "Error: Unable to capture frame!" << std::endl;
            break;
        }

        // Display the captured frame.
        cv::imshow("Camera", frame);

        // Break the loop if any key is pressed.
        if (cv::waitKey(1) >= 0) {
            break;
        }
    }

    // Save the captured frame to a file.
    std::string filename = "captured_frame.jpg";
    if (cv::imwrite(filename, frame)) {
        std::cout << "Frame saved successfully to " << filename << std::endl;
    } else {
        std::cerr << "Error: Unable to save the frame!" << std::endl;
    }

    // Release the camera and destroy OpenCV windows.
    cap.release();
    cv::destroyAllWindows();

    return 0;
}
