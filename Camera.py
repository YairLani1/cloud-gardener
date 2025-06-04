import cv2
import os
from datetime import datetime
import json
import Script_Executer


def What_flash(current_time,Working_plan_File_path):
    with open(Working_plan_File_path, 'r') as file:
            Script = json.load(file)
    current_time = datetime.strptime(current_time, "%H:%M")
    
    Day_start_time, Day_end_time = Script["Day"].split("-")
    Day_start_time = datetime.strptime(Day_start_time, "%H:%M")
    Day_end_time = datetime.strptime(Day_end_time, "%H:%M")
    if Day_start_time <= current_time <= Day_end_time or (Day_start_time>Day_end_time and (Day_start_time <= current_time or current_time <= Day_end_time)):
        return [key+value for key, value in Script["Day_Flash"].items()]
    
    Night_start_time, Night_end_time = Script["Night"].split("-")
    Night_start_time = datetime.strptime(Night_start_time, "%H:%M")
    Night_end_time = datetime.strptime(Night_end_time, "%H:%M")
    if Night_start_time <= current_time <= Night_end_time or (Night_start_time>Night_end_time and (Night_start_time <= current_time or current_time <= Night_end_time)):
        return [key+value for key, value in Script["Night_Flash"].items()]




def take_picture(current_date, current_time, camera_index,Pics_Data_Folder_path):
    if (camera_index == 0):
        camera_folder_name = 'cameraA'
    else:
        camera_folder_name = 'cameraB'

    cap = cv2.VideoCapture(camera_index)
    print(f"cap = cv2.VideoCapture({camera_index})")
    if not cap.isOpened():
        print(f"Error: Unable to open the camera {camera_index}.")
        return
    ret, frame = cap.read()
    print(f"camera {camera_index} ret")
    # Always release the camera
    cap.release()
    print(f"camera {camera_index} release")
    if ret:
        folder_path = os.path.join(Pics_Data_Folder_path, camera_folder_name)
        # Check if the folder exists; if not, create it
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        filename = f"{folder_path}/{current_date}|{current_time}.jpg"
        # Save the image
        cv2.imwrite(filename, frame)


def main(Newest_Data, Changeable_Consts):
    # Initialize the camera
    Working_plan_File_path = Changeable_Consts[1]
    Pics_Data_Folder_path = Changeable_Consts[3]
    current_date, current_time = Newest_Data[0], Newest_Data[1]
    Original_light = ["light=" + Newest_Data[5]]
    Flash = What_flash(current_time, Working_plan_File_path)
    if Flash:
        Script_Executer.Command_exeuter(Flash, Changeable_Consts)
        take_picture(current_date, current_time, 0,Pics_Data_Folder_path)
        take_picture(current_date, current_time, 2,Pics_Data_Folder_path)
        Script_Executer.Command_exeuter(Original_light, Changeable_Consts)
    else:
        take_picture(current_date, current_time, 0,Pics_Data_Folder_path)
        take_picture(current_date, current_time, 2,Pics_Data_Folder_path)