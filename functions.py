import os
import json
import whisper_timestamped
import ffmpeg
import detoxify
import multiprocessing

worker_model = None

def read_config(file_path):
    try:
        with open(file_path, 'r') as f:
            config_data = json.load(f)
        return config_data
    except FileNotFoundError:
        config_data = config_menu()
        return config_data
    
def write_config(file_path, content):
    try:
        with open(file_path, 'w') as outfile:
            json.dump(content, outfile, indent=4, sort_keys=True)
    except FileNotFoundError:
        print("Config not found")
        pass
        
        
def size_finder(size_input:str, config_dict:dict):
    if size_input.lower().strip() == "3":
            config_dict.update([("model_size", "small")])
            write_config("./config.json", config_dict)
            loop_check = 2
            return loop_check



    elif size_input.lower().strip() == "1":
            config_dict.update([("model_size", "tiny")])
            write_config("./config.json", config_dict)
            loop_check = 1
            return loop_check            
        
    elif size_input.lower().strip() == "2":
            config_dict.update([("model_size", "base")])
            write_config("./config.json", config_dict)
            loop_check = 1
            return loop_check

    elif size_input.lower().strip() == "4":
            config_dict.update([("model_size", "medium")])
            write_config("./config.json", config_dict)
            loop_check = 5
            return loop_check

    elif size_input.lower().strip() == "5":
            config_dict.update([("model_size", "large")])
            write_config("./config.json", config_dict)
            loop_check = 10
            return loop_check

    elif size_input.lower().strip() == "6":
            config_dict.update([("model_size", "turbo")])
            write_config("./config.json", config_dict)
            loop_check = 6
            return loop_check

    else:
          print("Please select a valid number")
          loop_check = "F"
          return loop_check
    
def category_finder(input:str, config_dict:dict, float:float):
    if input.lower().strip() == "t":
            config_dict.update([("t", float)])
            write_config("./config.json", config_dict)
            pass


    elif input.lower().strip() == "st":
            config_dict.update([("st", float)])
            write_config("./config.json", config_dict)
            pass
        
    elif input.lower().strip() == "th":
            config_dict.update([("th", float)])
            write_config("./config.json", config_dict)
            pass

    elif input.lower().strip() == "o":
            config_dict.update([("o", float)])
            write_config("./config.json", config_dict)


    elif input.lower().strip() == "id":
            config_dict.update([("id", float)])
            write_config("./config.json", config_dict)


    elif input.lower().strip() == "i":
            config_dict.update([("i", float)])
            write_config("./config.json", config_dict)


    else:
          print("Please select a valid category")
          pass

def severity_tweaker(input: str, config_dict):
      split_list = input.split("-")
      category = split_list[0]
      new_value = split_list[1]
      float_value = float(new_value)
      if float_value > 1:
            print("Number too high, please enter a new one")
      elif float_value < 0:
            print("Number too low, please enter a new one")
      category_finder(config_dict=config_dict, input=category, float=float_value)

def config_menu():
        model_configured = False#These variables are used for the loops for each part of the config process
        path_configured = False
        worker_count_configured = False
        tox_levels_configured = False
        while model_configured == False:
        
                print("Config file not found at {file_path}, starting initialization process.")
                print("\n\nSelect one of the following model sizes:\n\n 1: 'tiny'(1G o/VRAM)\n\n 2: 'base'(1G o/VRAM)\n\n 3: 'small'(2G o/VRAM)\n\n 4: 'medium'(5G o/VRAM)\n\n 5: 'large'(10G o/VRAM)\n\n 6: 'Turbo'(6G o/VRAM) ")
                model_size = input("\nInput a number: ")
                try:
                       with open ("config.json", 'r') as file:
                                config_data = json.load(file)      
                except FileNotFoundError:
                                config_data = {
                        "file_path": "./",
                        "worker_counts": "1",
                        "model_size": "small",
                        "t": 0.5,
                        "ts": 0.5,
                        "o": 0.5,
                        "th": 0.5,
                        "i": 0.5,
                        "id": 0.5
                                }       #This config data is considered the preset
                model_loop = size_finder(model_size, config_data)
                if model_loop != "F": 
                        break
        
        while path_configured == False:
                print("\n\n Would you like to change filepaths from default?")
                file_change = input("\n y/N? ")
                if file_change.lower().strip() == "n":
                        path_configured = True
                        new_dir = "./"
                        break

                elif file_change.lower().strip() == "y":
                        new_dir = input("\nPlease paste your PATH here: ")
                        config_data.update([("file_path", new_dir)])
                        write_config("./config.json", config_data)
                        path_configured = True
                        break
                
                elif file_change.lower().strip() == "y":
                       path_configured = True
                       new_dir = "./"
                       break
                else: 
                       path_configured = True
                       new_dir = "./"
                       break
        while worker_count_configured == False:
              print("Choose how many workers you'd like to run.")
              worker_count_amnt = input("\nPlease type a number: ")
              int_worker_count = int(worker_count_amnt)
              vram_total = int_worker_count*model_loop
              string_vram = str(vram_total)
              print("\nWARNING, your current settings will use " + string_vram + "gigs of VRAM.\nAre you sure your system can handle this?")
              warning_check = input("Y/n... ")
              if warning_check.strip().lower() == "y":
                        worker_count_configured = True
                        config_data.update([("worker_counts", worker_count_amnt)])
                        write_config("./config.json", config_data)
                        pass
              elif warning_check.strip().lower() == "n":
                        model_configured = False
                        worker_count_configured = False

              elif warning_check.strip().lower() =="":
                        worker_count_configured = True
                        config_data.update([("worker_counts", worker_count_amnt)])
                        write_config("./config.json", config_data)
                        pass  

              else:
                        print("Please choose a valid option")
              print("Would you like to configue the sensitivity of the context model?")
              tox_config = input("y/N? ")
              if tox_config.lower().strip() == "n":
                    pass
              
              elif  tox_config.lower().strip() == "":
                        tox_levels_configured = True
                        pass
              elif tox_config.lower().strip() == "y":
                    while tox_levels_configured == False:
                        print("Set a value by typing the name of the category, e.g., for severe toxicity, st, then the new amount seperated with a dash -. The number cannot be larger than one, or smaller than zero.\n\nfor example, 'st-0.5'\nThe vaulues are:\n toxcicity(t)\n severe toxcicity(st)\n obscene(o)\n threats(th)\n insults(i)\n and identity(id)")
                        tweaked_severity = input("Awaiting input... ")
                        severity_tweaker(tweaked_severity, config_data)
                        print("Would you like to continue configuring toxicity levels?")
                        user_input = input("\nY/n... ")
                        if user_input.lower().strip() == "y":
                              pass
                        elif user_input.lower().strip() == "n":
                              tox_levels_configured = True
                              pass
                        else:
                              pass
                        
        print("Congratulations! You've configured Podangel, and now all that is left to do is add some files to the input folder, and run the program with pa run. Enjoy!")
        input_path = (f"{new_dir}" + "/Input")
        output_path = (f"{new_dir}" + "/Output")
        bridge_path = (f"{new_dir}" + "/.bridge")
        os.makedirs(input_path)
        os.makedirs(output_path)
        os.makedirs(bridge_path)
        return None
    
def run_program(config_dict):
    #setting up the variables that will be used in the actual program
    model_size = config_dict["model_size"]
    path = config_dict["file_path"]
    worker_counts = config_dict["worker_counts"]
    toxic = config_dict["t"]
    sev_toxic = config_dict["ts"]
    obscene = config_dict["o"]
    identity = config_dict["id"]
    insult = config_dict["i"]
    threat = config_dict["th"]

    input_path = f"{path}/Input"
    output_path = f"{path}/Output"
    in_file_list = []
    out_file_list = []
    
    for files in os.listdir(input_path):
        full_path = os.path.join(input_path, files)
        if os.path.isfile(full_path):
                in_file_list.append(files)
    print(in_file_list)
    
    for files in os.listdir(output_path):
        full_path = os.path.join(output_path, files)
        if os.path.isfile(full_path):
                out_file_list.append(files)
    
    working_list = []

    int_worker_counts = int(worker_counts)
    
    number = 0

    working_list = [f for f in in_file_list if f not in out_file_list]
    
    if not working_list:
           print("No files to update")
           return None   
    

    with multiprocessing.Pool(processes=int_worker_counts, initializer=worker_initializer, initargs=(model_size,),) as pool:
           results = pool.starmap(
                  process_file, [(file, input_path) for file in working_list]
           )
           print(results)
           return results


def process_file(filename, input_path):
       global worker_model
       file_path = f"{input_path}/{filename}"
       transcribed_file = whisper_timestamped.transcribe(worker_model, file_path)
       return transcribed_file

def worker_initializer(model_size):
    global worker_model
    worker_model = whisper_timestamped.load_model(model_size)