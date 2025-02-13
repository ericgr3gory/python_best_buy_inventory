import psutil
import subprocess
import logging
import glob
import random
from pathlib import Path
import requests
from time import sleep
from dotenv import load_dotenv

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
        logging.info("Error:", e)
        
    return public_ip

def start_openvpn(openvpn_config_list):
    ov_config = pick_random_openvpn_config(openvpn_config_list)
    ov_config = f"openvpn@{ov_config}.service"
    command = ["sudo", "systemctl", "start", ov_config]
    logging.info(f'connecting to vpn {ov_config}')
    run_command(command)
    return command


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


'''def stop_openvpn():
    processes = find_openvpn_processes()
    if processes:
        for proc in processes:
            conf = (proc['cmdline'])
            config_path = Path(conf[9])
            instance_name = config_path.stem
            ov_config = f"openvpn@{instance_name}.service"
            command = ["sudo", "systemctl", "stop", ov_config]
            run_command(command)
            logging.info('disconneting form vpn')'''
            
def vpn():
    stop_openvpn()
    current_ip = get_public_ip()
    logging.info(f'current ip {current_ip}')
    configs = openvpn_conf_files()
    start_openvpn(configs)
    vpn_public_ip = get_public_ip()
    logging.info(f'new ip is {vpn_public_ip} and old ip {current_ip}')
    while vpn_public_ip == current_ip or vpn_public_ip == None:
        sleep(8)
        vpn_public_ip = get_public_ip()
        logging.info(f'new ip is {vpn_public_ip} and old ip {current_ip}')
        
        
        
    logging.info(f'vpn connected to {vpn_public_ip}')
    
def main():
    vpn()
    
    
if __name__ == '__main__':
    main()