import psutil
import subprocess
import logging
import glob
import random
from pathlib import Path
import requests
from time import sleep

logging.basicConfig(
    level=logging.INFO,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s [%(levelname)s] %(message)s',  # Log message format
    datefmt='%Y-%m-%d %H:%M:%S',  # Date format
    handlers=[
        logging.StreamHandler(),  # Output logs to the console
        logging.FileHandler("script.log", mode='w')  # Output logs to a file (overwrites each run)
    ]
)


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
        logging.info(f"Error running command: {' '.join(command)}")
        logging.info(f"Return code: {err.returncode}")
        logging.info(f"Error output: {err.stderr}")
        return None
    
def openvpn_conf_files():
    file_pattern = "/etc/openvpn/*.conf"
    config_file_list = glob.glob(file_pattern)
    logging.info('retrieving config files')
    return remove_file_extension(config_file_list)

def remove_file_extension(files):
    file_extension_removed = []
    for f in files:
        p = Path(f)
        file_extension_removed.append(p.stem)
    return file_extension_removed
    
def pick_random_openvpn_config(config_file_list):
    logging.info('picking random config file')
    return random.choice(config_file_list)
    
def get_public_ip():
    try:
        public_ip = requests.get('https://api.ipify.org').text
        logging.info(public_ip)
    except requests.RequestException as e:
        public_ip = None
        logging.info("Error:", e)
        logging.info(public_ip)
    return public_ip

def start_openvpn(openvpn_config_list):
    ov_config = pick_random_openvpn_config(openvpn_config_list)
    ov_config = f"openvpn@{ov_config}.service"
    command = ["sudo", "systemctl", "start", ov_config]
    logging.info('connecting to vpn')
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
            run_command(command)
            logging.info('disconneting form vpn')
            
def vpn():
    stop_openvpn()
    configs = openvpn_conf_files()
    start_openvpn(configs)
    public_ip = get_public_ip()
    while public_ip == "172.233.141.177" or public_ip == None:
        public_ip = get_public_ip()
        sleep(2)
        
    logging.info(f'vpn connected to {public_ip}')
    
def main():
    vpn()
    
    
if __name__ == '__main__':
    vpn()