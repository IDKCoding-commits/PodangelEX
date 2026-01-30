import os
import json

def read_config(file_path):
    try:
        with open(file_path, 'r') as f:
            config_data = json.load(f)
        return config_data
    except:
        FileNotFoundError
        config_menu()
    
def write_config(file_path, content):
    try:
        with open(file_path, 'w') as outfile:
            json.dump(content, outfile, indent=4, sort_keys=True)
    except:
        FileNotFoundError
        print("Config not found")
        pass
        
        
def size_finder(size_input, config_dict):
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
    
def catagory_finder(input, config_dict, interger):
    if input.lower().strip() == "t":
            config_dict.update([("t", interger)])
            write_config("./config.json", config_dict)
            pass


    elif input.lower().strip() == "st":
            config_dict.update([("st", interger)])
            write_config("./config.json", config_dict)
            pass
        
    elif input.lower().strip() == "th":
            config_dict.update([("th", interger)])
            write_config("./config.json", config_dict)
            pass

    elif input.lower().strip() == "o":
            config_dict.update([("o", interger)])
            write_config("./config.json", config_dict)


    elif input.lower().strip() == "id":
            config_dict.update([("id", interger)])
            write_config("./config.json", config_dict)


    elif input.lower().strip() == "i":
            config_dict.update([("i", interger)])
            write_config("./config.json", config_dict)


    else:
          print("Please select a valid category")
          pass

def severity_tweaker(input: str, config_dict):
      split_list = input.split("-")
      category = split_list[1]
      new_value = split_list[2]
      int_value = int(new_value)
      if int_value > 1:
            print("Number too high, please enter a new one")
      elif int_value < 0:
            print("Number too low, please enter a new one")
      catagory_finder(config_dict=config_dict, input=category, interger=int_value)

def config_menu():
        model_configured = False
        path_configured = False
        iteration_configured = False
        tox_levels_configured = False
        while model_configured == False:
        
                print("Config file not found at {file_path}, starting initialization process.")
                print("\n\nSelect one of the following model sizes:\n\n 1: 'tiny'(1G o/VRAM)\n\n 2: 'base'(1G o/VRAM)\n\n 3: 'small'(2G o/VRAM)\n\n 4: 'medium'(5G o/VRAM)\n\n 5: 'large'(10G o/VRAM)\n\n 6: 'Turbo'(6G o/VRAM) ")
                model_size = input("\nInput a number: ")
                content = {
        "file_path": "./",
        "iterations": "1",
        "model_size": "small",
        "iterations": "null",
        "t": 0.5,
        "ts": 0.5,
        "o": 0.5,
        "th": 0.5,
        "i": 0.5,
        "id": 0.5
                }
                model_loop = size_finder(model_size, content)
                if model_loop != "F":
                        break
        
        while path_configured == False:
                print("\n\n Would you like to change filepaths from default?")
                file_change = input("\n Y/N? ")
                if file_change.lower().strip() == "n":
                        path_configured = True
                        break

                if file_change.lower().strip() == "y":
                        new_dir = input("\nPlease paste your PATH here: ")
                        config_data.update([("file_path", new_dir)])
                        write_config("./config.json", config_data)
                        path_configured = True
                        break
        while iteration_configured == False:
              print("Choose how many iterations you'd like to run.")
              iteration_amnt = input("\nPlease type a number: ")
              int_iteration = int(iteration_amnt)
              vram_total = int_iteration*model_loop
              string_vram = str(vram_total)
              print("\nWARNING, your current settings will use " + string_vram + "gigs of VRAM.\nAre you sure your system can handle this?")
              warning_check = input("Y/n... ")
              if warning_check.strip().lower() == "y":
                        iteration_configured = True
                        pass
              elif warning_check.strip().lower() == "n":
                        model_configured = False
                        iteration_configured = False
              else:
                        print("Please choose a valid option")
              print("Would you like to configue the sensitivity of the context model?")
              tox_config = input("Y/n?")
              if tox_config.lower().strip() == "n":
                    pass
              elif tox_config.lower().strip() == "y":
                    while tox_levels_configured == False:
                        print("Set a value by typing the name of the category, e.g., for severe toxicity, st, then the new amount seperated with a dash -. The number cannot be larger than one, or smaller than zero.\n\nfor example, 'st-0.5'\nThe vaulues are:\n toxcicity(t)\n severe toxcicity(st)\n obscene(o)\n threats(th)\n insults(i)\n and identity(id)")
                        tweaked_severity = input("Awaiting input... ")
                        severity_tweaker(tweaked_severity, config_data)
                        print("Would you like to continue configuring toxicity levels?")
                        user_input = input("\nY/n...")
                        if user_input.lower().strip() == "y":
                              pass
                        elif user_input.lower().strip == "n":
                              tox_levels_configured = True
                        else:
                              pass
                        pass
                        print("Congratulations! You've configured Podangel, and now all that is left to do is run it with pa run. Enjoy!")
        return None
    