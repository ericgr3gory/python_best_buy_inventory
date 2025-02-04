import subprocess
import logging
import os
import glob

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
    
def ls_directory():
    files = glob.glob("/etc/openvpn/*.conf")
    print(files)
    
    
if __name__ == '__main__':
   ls_directory()