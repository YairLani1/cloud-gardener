import subprocess
from datetime import datetime
import json
import Script_Executer
import os

from PIL import Image
import io





def What_flash(current_time, Working_plan_File_path):
    with open(Working_plan_File_path, 'r') as file:
        Script = json.load(file)
    current_time = datetime.strptime(current_time, "%H:%M")

    Day_start_time, Day_end_time = Script["Day"].split("-")
    Day_start_time = datetime.strptime(Day_start_time, "%H:%M")
    Day_end_time = datetime.strptime(Day_end_time, "%H:%M")
    if Day_start_time <= current_time <= Day_end_time or (
            Day_start_time > Day_end_time and (Day_start_time <= current_time or current_time <= Day_end_time)):
        return [key + value for key, value in Script["Day_Flash"].items()]

    Night_start_time, Night_end_time = Script["Night"].split("-")
    Night_start_time = datetime.strptime(Night_start_time, "%H:%M")
    Night_end_time = datetime.strptime(Night_end_time, "%H:%M")
    if Night_start_time <= current_time <= Night_end_time or (
            Night_start_time > Night_end_time and (Night_start_time <= current_time or current_time <= Night_end_time)):
        return [key + value for key, value in Script["Night_Flash"].items()]


# Convert MJPEG binary data to an image and compress it
def save_compressed_image(image_data, quality, camera_index, current_date, current_time ,Pics_Data_Folder_path):
    if (camera_index == 0):
        camera_folder_name = 'cameraA'

    else:
        camera_folder_name = 'cameraB'
    folder_path = os.path.join(Pics_Data_Folder_path, camera_folder_name)
        # Check if the folder exists; if not, create i
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    filename = f"{folder_path}/{current_date}|{current_time}.jpeg"
    
    image = Image.open(io.BytesIO(image_data))  # Load the image from MJPEG data
    image.save(filename, format="JPEG", quality=quality)  # Save with lower quality


def take_picture(camera_index):
    if (camera_index == 0):
        #width = 2592
        #height = 1944
        width = 1920
        height = 1080
    else:
        width = 1920
        height = 1080

    exe_path = os.path.join(os.getcwd(),"capture_image")
    result = subprocess.run(
        [exe_path, str(camera_index),str(width),str(height)],
        stdout=subprocess.PIPE,  # Capture stdout for image data
        stderr=subprocess.PIPE  # Capture stderr for error messages
    )

    # Check for errors
    if result.returncode == 0:
        return result.stdout
        
    else:
        print(f"Error Camera {camera_index} :", result.stderr.decode())

#Start = datetime.now()
#x = take_picture(0)
#print(datetime.now()-Start)
#y = take_picture(2)
#print(datetime.now()-Start)
#with open(os.getcwd()+"/A.jpeg", "wb") as file:
#            file.write(x)
#save_compressed_image(x, 100, 0,'12-12-16','12:43',os.getcwd())
#print(datetime.now()-Start)
#with open(os.getcwd()+"/B.jpeg", "wb") as file:
#            file.write(y)
#save_compressed_image(y, 100, 2,'12-12-16','12:43',os.getcwd())
#print(datetime.now()-Start)

def main(Newest_Data, Changeable_Consts):
    Start = datetime.now()
    # Initialize the camera
    Working_plan_File_path = Changeable_Consts[1]
    Pics_Data_Folder_path = Changeable_Consts[3]
    current_date, current_time = Newest_Data[0], Newest_Data[1]
    Original_light = ["light=" + Newest_Data[5]]
    Flash = What_flash(current_time, Working_plan_File_path)
    if Flash:
        Script_Executer.Command_exeuter(Flash, Changeable_Consts)
        camera_A_Data = take_picture(0)
        camera_B_Data = take_picture(2)
        Script_Executer.Command_exeuter(Original_light, Changeable_Consts)
        save_compressed_image(camera_A_Data, 50, 0, current_date, current_time ,Pics_Data_Folder_path)
        save_compressed_image(camera_B_Data, 50, 2, current_date, current_time ,Pics_Data_Folder_path)
    else:
        camera_A_Data = take_picture(0)
        camera_B_Data = take_picture(2)
        save_compressed_image(camera_A_Data, 50, 0, current_date, current_time ,Pics_Data_Folder_path)
        save_compressed_image(camera_B_Data, 50, 2, current_date, current_time ,Pics_Data_Folder_path)
    print("pictures took "+str(datetime.now()-Start))
        
        
        