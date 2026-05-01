import psutil

def kill_process(pid):
    try:
        p = psutil.Process(pid)

        p.terminate()   # try soft kill
        p.wait(timeout=2)

        return True

    except psutil.TimeoutExpired:
        # force kill if not terminated
        try:
            p.kill()
            return True
        except:
            return False

    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False