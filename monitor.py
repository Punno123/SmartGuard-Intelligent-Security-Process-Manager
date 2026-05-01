import psutil

def list_processes():
    process_list = []

    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try:
            pinfo = proc.info

            # ✅ Add thread count
            pinfo['threads'] = proc.num_threads()

            # ✅ (Optional but useful) process status
            pinfo['status'] = proc.status()

            process_list.append(pinfo)

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    return process_list