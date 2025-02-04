import subprocess
import logging
import os
import glob
import random
from pathlib import Path

def run_command(command):
    """
    Run a command using subprocess.run and return its output.
    If the command fails, print the error details.
    """
    try:
        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as err:
        logging.error(f"Error running command: {' '.join(command)}")
        logging.error(f"Return code: {err.returncode}")
        logging.error(f"Error output: {err.stderr}")
        return None
    
def openvpn_conf_files():
    file_pattern = "/etc/openvpn/*.conf"
    config_file_list = glob.glob(file_pattern)
    return remove_file_extension(config_file_list)

def remove_file_extension(files):
    file_extension_removed = []
    for f in files:
        p = Path(f)
        file_extension_removed.append(p.stem)
    return file_extension_removed
    
def pick_random_openvpn_config(config_file_list):
    return random.choice(config_file_list)    

def start_openvpn(openvpn_config_list):
    ov_config = pick_random_openvpn_config(openvpn_config_list)
    ov_config = f"openvpn@{ov_config}.service"
    command = ["sudo", "systemctl", "start", ov_config]
    run_command(command)
    return command

def openvpn_currently_running():
    command = ["systemctl", "list-units", "--type=service", "|",  "grep", "openvpn"]
    return run_command(command)

def stop_openvpn():
    #systemctl list-units --type=service | grep openvpn
    pass

    
    
    
if __name__ == '__main__':
    print(openvpn_currently_running())