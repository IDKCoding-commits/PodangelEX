import whisper_timestamped
import json
import os 
import threading
import argparse
import functions
from functions import *
import ast

if __name__ == "__main__":
    try:
        config_dict = read_config("./config.json")
    except FileNotFoundError:
        config_menu()
        config_dict = read_config("./config.json")

    main_loop = True

    while main_loop == True:
        print("\n\nWelcome to PodAngel CLI! \nIf you want to reconfigure, type (1)\nYou can run the app with (2)")
        main_input = input("\n Input: ")
        normalized_input = main_input.lower().strip()

            #Config Menu
        if normalized_input == "1":
                config_menu()


        elif normalized_input == "2":
                run_program(config_dict=config_dict)
                print("Run menu reached")


        elif normalized_input == "exit":
                main_loop = False
                quit()