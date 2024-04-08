import serial
import serial.tools.list_ports
import os
import json


def get_ports():
    read_ports = serial.tools.list_ports.comports()
    ports = []
    for port, desc, hwid in sorted(read_ports):
        # print(f"{port}: {desc} [{hwid}]")
        if 'arduino' in desc.lower() or '2341' in hwid:
            ports.append(port)
    return ports

def config_exist():
    file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.json')
    return os.path.exists(file_path)


def save_config(dic):
    file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.json')
    try:
        with open(file_path, 'w') as file:
            json.dump(dic, file)
        return "Configuration saved."
    except IOError:
        return "Configuration NOT SAVED. Can't write the file."

def load_config():
    file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.json')
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as file:
                dic = json.load(file)
            return dic
        except IOError:
            return "Can't open the config file."
    else:
        return "Config file do not exist."
