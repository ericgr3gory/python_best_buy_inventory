import psutil
import subprocess
import logging
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
        print(f"Error running command: {' '.join(command)}")
        print(f"Return code: {err.returncode}")
        print(f"Error output: {err.stderr}")
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

def find_openvpn_processes():
    openvpn_processes = []
    for proc in psutil.process_iter(attrs=["pid", "name", "cmdline"]):
        try:
            cmdline = proc.info.get("cmdline", [])
            # Check if any argument in the command line contains "openvpn"
            if any("openvpn" in arg for arg in cmdline):
                openvpn_processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return openvpn_processes


def stop_openvpn():
    processes = find_openvpn_processes()
    if processes:
        for proc in processes:
            conf = (proc['cmdline'])
            config_path = Path(conf[9])
            instance_name = config_path.stem
            ov_config = f"openvpn@{instance_name}.service"
            command = ["sudo", "systemctl", "stop", ov_config]
            
            
def vpnstart():
    stop_openvpn()
    configs = openvpn_conf_files()
    start_openvpn(configs)
    

    
    
    
if __name__ == '__main__':
    vpnstart()