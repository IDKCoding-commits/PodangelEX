import whisper_timestamped
import json
import os 
import threading
import argparse
import functions
from functions import *
import ast

config_dict = read_config("./config.json")
print(type(config_dict))

print("\n\nWelcome to PodAngel CLI! \nIf you want to change some settings, use: 'PA config'\nbesides that, you can run the script with 'PA run'")
main_input = input("\n Input: ")
normalized_input = main_input.lower().strip()
print(normalized_input)

#Config Menu
if normalized_input == "pa config":
    config_menu()


elif normalized_input == "pa run":
    json.dump
    print("Run menu reached")


elif normalized_input == "exit":
    quit()