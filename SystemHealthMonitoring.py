import logging
import time
import shutil
import subprocess

# Configure logging
logging.basicConfig(filename='system_health.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Thresholds
CPU_THRESHOLD = 80  
MEMORY_THRESHOLD = 80  
DISK_THRESHOLD = 80  

# Function to check CPU usage using top command
def check_cpu():
    try:
        output = subprocess.check_output("top -bn1 | grep 'Cpu(s)'", shell=True).decode()
        cpu_usage = float(output.split('%')[0].split()[-1])
        cpu_usage = 100 - cpu_usage  
        if cpu_usage > CPU_THRESHOLD:
            message = f"High CPU Usage detected: {cpu_usage:.2f}%"
            print(message)
            logging.warning(message)
    except Exception as e:
        logging.error(f"Failed to check CPU usage: {e}")

# Function to check Memory usage using free command
def check_memory():
    try:
        output = subprocess.check_output("free", shell=True).decode().splitlines()
        memory_line = output[1].split()
        total = int(memory_line[1])
        used = int(memory_line[2])
        memory_percent = (used / total) * 100
        if memory_percent > MEMORY_THRESHOLD:
            message = f"High Memory Usage detected: {memory_percent:.2f}%"
            print(message)
            logging.warning(message)
    except Exception as e:
        logging.error(f"Failed to check Memory usage: {e}")

# Function to check Disk usage
def check_disk():
    try:
        total, used, free = shutil.disk_usage('/')
        disk_percent = (used / total) * 100
        if disk_percent > DISK_THRESHOLD:
            message = f"High Disk Usage detected: {disk_percent:.2f}%"
            print(message)
            logging.warning(message)
    except Exception as e:
        logging.error(f"Failed to check Disk usage: {e}")

# Function to list running processes
def check_processes():
    try:
        output = subprocess.check_output("ps -eo pid,comm,pcpu --sort=-pcpu", shell=True).decode().splitlines()
        for line in output[1:10]:  
            parts = line.split()
            if len(parts) >= 3:
                pid, name, cpu_percent = parts[0], parts[1], float(parts[2])
                if cpu_percent > CPU_THRESHOLD:
                    message = f"Process {name} (PID: {pid}) is using high CPU: {cpu_percent}%"
                    print(message)
                    logging.warning(message)
    except Exception as e:
        logging.error(f"Failed to check running processes: {e}")

# Main function
def monitor_system():
    while True:
        check_cpu()
        check_memory()
        check_disk()
        check_processes()
        time.sleep(10) 

if __name__ == "__main__":
    monitor_system()
