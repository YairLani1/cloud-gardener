#fieldnames = ['Time', 'DHT(C+%)', 'Soil Temp(C)', 'Soil Electrical Conductivity(EC)', 'Light(R,G,B)', 'Pump(Sec)', 'Fan(RPM)']bjj
import json
import os
from datetime import datetime
import time
import schedule
import Extract_Data
import Camera_using_C
import Script_Executer
import Arduino_commands
import serial

Changeable_Consts=list()

Basic_working_plan={
  "Day": "06:00-22:00",
  "Day_Flash": {"light=": "70|70|70"},
  "Night": "22:01-05:59",
  "Night_Flash": {"light=": "0|50|0"},
  "conditionalScript": {},
  "dailySchedule":
  {
    "06:00": {"pump=": "0.5|0.5"},
    "14:00": {"pump=": "0.5|0.5"}
  }
}

def get_Data():
    start_Time = datetime.now()
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M")
    Newest_Data = Extract_Data.main(current_date, current_time,Changeable_Consts)
    minutes = int(current_time.split(":")[1])
    if minutes % 10 == 0: # Take a picture every 10 minutes
        Camera_using_C.main(Newest_Data,Changeable_Consts)
    Script_Executer.main(Newest_Data,Changeable_Consts)
    end_Time = datetime.now()
    print(str(end_Time-start_Time))
    
    
def create_folders():
    script_directory = os.getcwd()
    SER = serial.Serial('/dev/ttyUSB0')
    #script_parent_directory = os.path.dirname(script_directory)
    Working_plan_File_path = os.path.join(script_directory, "working_plan", "working_plan.json")
    Pics_Data_Folder_path = os.path.join(script_directory, "Pics&Data")
    Sensors_list = ['dht?', 's-temp?', 'ec?', 'light?', 'UV?', 'pump?', 'fan?', 'hydrofan?']

    os.makedirs(os.path.dirname(Pics_Data_Folder_path), exist_ok=True)
    # Ensure the directory exists
    os.makedirs(os.path.dirname(Working_plan_File_path), exist_ok=True)
    # Create the working_plan.json if it doesn't exist
    if not os.path.exists(Working_plan_File_path):
        with open(Working_plan_File_path, 'w') as file:
            json.dump(Basic_working_plan, file, indent=4)  # Optionally write an empty JSON object or other content

    Changeable_Consts.extend([SER, Working_plan_File_path, Sensors_list, Pics_Data_Folder_path])
    if not os.path.exists(Pics_Data_Folder_path):
        os.makedirs(Pics_Data_Folder_path)
        
        
def system_initialized():
    Time = datetime.now().strftime("%H:%M")
    print("system initialized at " + str(Time))
    create_folders()
    Arduino_commands.Reset(Changeable_Consts)
    Changeable_Consts[0].open()
    Script_Executer.recover_state(Changeable_Consts)

system_initialized()
schedule.every().minute.at(":00").do(get_Data)

while True:
        schedule.run_pending()
        time.sleep(1)


