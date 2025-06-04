import json
from datetime import datetime
import time

Current_status = []

MAX_COMMEND_ATTEMPS = 3
MAX_COMMEND_TIMEOUT = 3



# Function to check conditions and apply actions
def apply_conditions(sensor_value, condition):
    for comparison, actions in condition.items():
        for threshold, command_dict in actions.items():
            if comparison == "greaterThan" and sensor_value > float(threshold):
                return command_dict
            elif comparison == "lessThan" and sensor_value < float(threshold):
                return command_dict
    return None



def validate_command(command_variables,Changeable_Consts):
    if command_variables is None:
        return False
    answer = False
    for Sensor_name in Changeable_Consts[2]:
        if command_variables[0] == Sensor_name[:-1]: # remove the '?'
            answer = True
            break
    if not answer:
        print(f"Error: The command name {command_variables[0]} is not in the known command options")
        return False
    if len(command_variables) == 1:
        return True
    if command_variables[0] in ['fan','UV','hydrofan']:
        if len(command_variables) != 2 or\
                command_variables[1] > 1 or\
                command_variables[1] < 0: # power is 0-1
                    answer = False
    if command_variables[0] in ['light']:
        if len(command_variables) != 4:
            answer = False
        else:
            for value in command_variables[1:]:
                if value > 255 or value < 0: # power is 0-255
                    answer = False
    if command_variables[0] in ['pump']:
        if len(command_variables) != 3 or\
                command_variables[2] < 0 or\
                command_variables[2] > 1: # power is 0-1
            answer = False
    if command_variables[0] in ['ec']:
        if len(command_variables) != 2:
            answer = False
    if command_variables[0] in ['s-temp']:
        if len(command_variables) != 2 or\
                command_variables[1] == -127:  # -127 is the value for not connected soil-temp sensor
                answer = False
    if command_variables[0] in ['dht']:
        if len(command_variables) != 3 or\
        not isinstance(command_variables[1], float) or\
        not isinstance(command_variables[2], float):  # not connected dht returns Nan|Nan
                answer = False
    if not answer:
        print(f"Error: The command {str(command_variables)} args doest fit the valid values")
    return answer



def break_msg_to_variables(command):
    try:
        command_Name, command_Values = command.split("=")
    except:
        try:
            command_Name, command_Values = command.split(":")
        except:
            try:
                command_Name, command_Values = command.split("?")
                if not command_Values:
                    return [command_Name]
                return None
            except:
                return None
    try:
        valuesList = [float(f"{float(item):.2f}") for item in command_Values.split("|")]
    except:
        return None
    return [command_Name]+valuesList

def response_validation(command_variables,response,Changeable_Consts):
    response_variables = break_msg_to_variables(response)
    if response_variables is None:
        return False
    if len(command_variables) == 1:
        return validate_command(response_variables,Changeable_Consts)
    return validate_command(response_variables,Changeable_Consts) and response_variables == command_variables
        

def Command_exeuter (Commands_list, Changeable_Consts):
    SER = Changeable_Consts[0]
    print("The command list is: " + str(Commands_list))
    responses = []
    for command in Commands_list:
        response = ''
        print("Trying command: "+command)
        sent_time = datetime.now()
        Num_attempts = 0
        command_variables = break_msg_to_variables(command)
        if not validate_command(command_variables,Changeable_Consts):
            print(f"Error: the command {command} is not defined correctly, skipping to the next one")
            continue
        while not response_validation(command_variables, response,Changeable_Consts):
            Num_attempts += 1
            if Num_attempts > MAX_COMMEND_ATTEMPS:
                print("Error: tried to do " + command + " for " + str(MAX_COMMEND_ATTEMPS) +
                      " times but didn't succeed. Moving on to do next command")
                break
            SER.flushInput()
            time.sleep(0.2)
            # Send the command
            bytes_written = SER.write(command.encode())
            # Check if the command was sent successfully
            if bytes_written != len(command):
                print(f"Sent command: {command} Failed")
                print("Error: Not all bytes were written to the serial port.")
                continue #
            start_time = time.time()  # Record the start time
            while (not response) and ((time.time() - start_time) < MAX_COMMEND_TIMEOUT):
                if SER.in_waiting > 0:  # Check if data is available in the buffer
                    response = SER.readline().decode().strip()
                    if not response_validation(command_variables, response,Changeable_Consts):
                        print("Error: Arduino is doing problems, sent the commend " + command +
                              " and got the response " + response)
                        response = ''
                        break
                else:
                    time.sleep(0.1)  # Small delay to avoid busy-waiting
        print("Arduino took " + str(datetime.now()-sent_time) + " seconds to response")
        responses.append(response)
    print("The responses list is: " + str(responses))
    return responses
    
def check_for_conditional_commands(Newest_Data,Script):
    # Parse the Newest_Data for sensor values
    [date, Time, air_temp_humidity, soil_temp, soil_conductivity, light_rgb, uv, pump_status, fan_power,
     hydrofan] = Newest_Data

    if air_temp_humidity:
        air_temp, air_humidity = map(float, air_temp_humidity.split('|'))
    if soil_conductivity:
        soil_conductivity_value = float(soil_conductivity)
    if pump_status:
        pump_duration, pump_power = pump_status.split('|')
        pump_duration = float(pump_duration)
        pump_power = float(pump_power)
    if fan_power:
        fan_power = float(fan_power)
    # Generate a list of commands based on the conditional script
    conditional_commands = {}
    Schedule_commands = []
    # Determine which conditional script to use based on time
    current_time = datetime.strptime(Time, "%H:%M")
    for period in Script["conditionalScript"]:
        starting_time, ending_time = period.split("-")
        starting_time = datetime.strptime(starting_time, "%H:%M")
        ending_time = datetime.strptime(ending_time, "%H:%M")
        if starting_time <= current_time <= ending_time or (
                starting_time > ending_time and (starting_time <= current_time or current_time <= ending_time)):
            conditional_script = Script["conditionalScript"][period]

            # Check air temperature
            if air_temp_humidity:
                air_temp_action = apply_conditions(air_temp, conditional_script["Air temperature"])
                if air_temp_action:
                    conditional_commands.update(air_temp_action)

                # Check air humidity
                air_humidity_action = apply_conditions(air_humidity, conditional_script["Air humidity"])
                if air_humidity_action:
                    conditional_commands.update(air_humidity_action)
            # conditional_commands contains only one command for each fan\pump\light\hidrofan so if
            # two diffrent conditions apply to the same motor action only one will be executed
            # Check soil conductivity
            if soil_conductivity:
                soil_conductivity_action = apply_conditions(soil_conductivity_value,
                                                            conditional_script["soil Conductivity"])
                if soil_conductivity_action:
                    conditional_commands.update(soil_conductivity_action)

    return [key + value for key, value in conditional_commands.items()]

# Main function to process Newest_Data
def main(Newest_Data, Changeable_Consts):
    # Load the JSON configuration file
    Working_plan_File_path = Changeable_Consts[1]
    with open(Working_plan_File_path, 'r') as file:
        Script = json.load(file)

    Conditional_commands_list = check_for_conditional_commands(Newest_Data,Script)
    Schedule_commands_list =[]
    # Check daily schedule
    Time = Newest_Data[1]
    daily_schedule = Script["dailySchedule"]
    if Time in daily_schedule:
    # add filter to commands that are already applied - no need to reactivate something to the same value
        Schedule_commands_list = [key+value for key, value in daily_schedule[Time].items()]

    if Schedule_commands_list:
        Command_exeuter(Schedule_commands_list,Changeable_Consts)
        print("sending the Schedule_commands_list: "+str(Schedule_commands_list))
    if Conditional_commands_list:
        print("sending the Conditional_commands_list: "+str(Conditional_commands_list))
        Command_exeuter(Conditional_commands_list,Changeable_Consts)


def recover_state(Changeable_Consts):
    Working_plan_File_path = Changeable_Consts[1]
    Commands_dict = {}
    current_time = datetime.now().strftime("%H:%M")
    current_date = datetime.now().strftime("%Y-%m-%d")
    with open(Working_plan_File_path, 'r') as file:
        Script = json.load(file)
    daily_schedule = Script["dailySchedule"]
    for Time in daily_schedule:
        if datetime.strptime(current_time, "%H:%M") >= datetime.strptime(Time, "%H:%M"):
            for command, value in daily_schedule[Time].items():
                Commands_dict[command] = value
        #else: break only if the script is not chronologically organized

    if not Commands_dict: # if all the Times have not accure yet - do the last one of the previous day
        Commands_dict = daily_schedule[Time]
    Commands_list = [key+value for key, value in Commands_dict.items() if not key.startswith("pump")]
    Command_exeuter(Commands_list,Changeable_Consts)




