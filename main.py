# main.py
import time
from monitor import list_processes
from detector import detect_suspicious
from logger import log_event
from utils import kill_process

system_processes = [
    "System Idle Process",
    "System",
    "Registry",
    "svchost.exe"
]

system_pids = [0, 4]  # critical Windows PIDs

# Optional: for colored terminal output
try:
    from colorama import Fore, Style, init
    init()
except ImportError:
    # fallback if colorama is not installed
    class Fore:
        RED = ''
        YELLOW = ''
        GREEN = ''
    class Style:
        RESET_ALL = ''

while True:
    # ✅ This prints once per iteration, not for every process
    print("Monitoring processes...")

    
    processes = list_processes()
    for p in processes:
        if p['pid'] == 0 or p['pid'] == 4:
          continue

        if p['name'] in ["System Idle Process", "System", "Registry", "svchost.exe"]:
            continue

        if p['name'] is None:
            continue 

        if p['pid'] in system_pids or p['name'] in system_processes:
           continue
        result = detect_suspicious(p)
        if result:
            message = f"{p['name']} (PID {p['pid']}) -> {', '.join(result)}"
            print(f"\n⚠️ ALERT DETECTED")
            print(f"Process: {p['name']}")
            print(f"PID: {p['pid']}")
            print(f"Reason: {', '.join(result)}")
            log_event(message)
            # killed = kill_process(p['pid']) 
            # # if killed: 
            # # print("Process terminated")

            #if any("high CPU" in r for r in result):
                #killed = kill_process(p['pid'])
                #if killed:
                 #print(Fore.RED + f"Process {p['name']} terminated!" + Style.RESET_ALL)
    time.sleep(3)
     




                      