import psutil
import subprocess
import logging
import glob
import random
from pathlib import Path
import requests
from time import sleep
import re

logging.basicConfig(
    level=logging.INFO,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s [%(levelname)s] %(message)s',  # Log message format
    datefmt='%Y-%m-%d %H:%M:%S',  # Date format
    handlers=[
        logging.StreamHandler(),  # Output logs to the console
        logging.FileHandler("/home/ericgr3gory/.local/logs/best_buy_scrape.log", mode='a')
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
        
    except requests.RequestException as e:
        public_ip = None
        logging.info("Error: %s", e)
        
    return public_ip

def start_openvpn(openvpn_config):
    config = f"openvpn@{openvpn_config}.service"
    command = ["sudo", "systemctl", "start", config]
    logging.info(f'connecting to vpn {config}')
    run_command(command)
    


def stop_openvpn():
    processes = find_openvpn_processes()
    if processes:
        for proc in processes:
            cmd = proc.get("cmdline", [])
            # Look for an argument that ends with ".conf"
            conf_file = next((arg for arg in cmd if arg.endswith(".conf")), None)
            if not conf_file:
                logging.warning("No config file found in process cmdline: %s", cmd)
                continue  # Skip this process if no config file was found
            config_path = Path(conf_file)
            instance_name = config_path.stem
            ov_config = f"openvpn@{instance_name}.service"
            command = ["sudo", "systemctl", "stop", ov_config]
            run_command(command)
            logging.info('disconnecting from vpn')


def find_openvpn_processes():
    openvpn_processes = []
    for proc in psutil.process_iter(attrs=["pid", "name", "cmdline"]):
        try:
            cmdline = proc.info.get("cmdline") or []
            # Check if any argument in the command line contains "openvpn"
            if any("openvpn" in arg for arg in cmdline):
                openvpn_processes.append(proc.info)
                logging.info(f'vpn running{proc.info}')
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return openvpn_processes

def check_connection():
    pattern = re.compile(r"Initialization Sequence Completed")
    with open("/var/log/openvpn.log", "r") as f:
        for line in f:
            if pattern.search(line):
                logging.info(f'{line}')
                return True
    return False
            
'''
def check_connection_dep(public_ip):
    
    vpn_public_ip = get_public_ip()  
    max_attempts = 3
    attempts_waiting_on_connection = 0
    
    while vpn_public_ip == public_ip or vpn_public_ip == None:
        attempts_waiting_on_connection = attempts_waiting_on_connection + 1
        if attempts_waiting_on_connection > max_attempts:
            logging.info('vpn connection failed starting a new connection')
            vpn()
        else:
            sleep(8)
            vpn_public_ip = get_public_ip()
            logging.info(f'vpn ip is {vpn_public_ip} and public ip was {public_ip}')
    
    return True
'''    
            
def vpn():
    stop_openvpn()
    current_ip = get_public_ip()
    logging.info(f'current ip {current_ip}')
    configs = openvpn_conf_files()
    random_config = pick_random_openvpn_config(configs)
    start_openvpn(random_config)
    sleep(15)
    
    if check_connection():
        logging.info(f'VPN Connection established at {get_public_ip()}')
        return True
    else:
        logging.info('VPN failed to start')
        return False
           
def main():
    while not vpn():
        sleep(10)
    
if __name__ == '__main__':
    main()