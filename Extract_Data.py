#fieldnames = 'Date','Time', 'DHT:(Celsius|HumidityPercent)','Soil Temp(C)','Soil Electrical Conductivity(VoltsValue)',
#                         'Light(R|G|B)', 'Pump(Duration|Power)', 'Fan(Power)'
import os
import csv
import Script_Executer


Fieldnames = ['Date','Time', 'DHT:(Celsius|percent)',
                          'Soil Temp(C)',
                         'Soil Electrical Conductivity(VoltsValue)',
                         'Light(R|G|B)','UV(Power)', 'Pump(Duration|Power)', 'Fan(Power)','HydroFan(Power)']


    
def sensors(current_date, current_time,Changeable_Consts):
    SER = Changeable_Consts[0]
    Sensors_list = Changeable_Consts[2]
    Pics_Data_Folder_path = Changeable_Consts[3]
    sensors_status=Script_Executer.Command_exeuter(Sensors_list,Changeable_Consts)
    new_row = [current_date, current_time]
    for value in sensors_status:
        if value:
            new_row.append(value.split(":")[1])
        else:
            new_row.append(value)
    file_path = f"{Pics_Data_Folder_path}/{current_date}.csv"
    if not os.path.exists(file_path):
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=Fieldnames)
            writer.writeheader()
    with open(file_path, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(new_row)
    print("The new row is: "+ str(new_row))
    return (new_row) 

def main(current_date,current_time,Changeable_Consts):
    return sensors(current_date, current_time,Changeable_Consts)
    
    
    
    








