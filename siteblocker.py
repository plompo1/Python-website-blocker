import os
import time
from typing import Optional
import psutil
import win32gui
import win32process

check = 2
opens = 0
files = {
    "browser": "Name of browser: ",
    "blocked": "Name of site to block (no url): ",
    "opens": None
}

def init_config() -> tuple[str, str]:
    for filename, prompt in files.items():
        if not os.path.exists(filename) and prompt:
            with open(filename, "w") as f:
                f.write(input(prompt))

    with open("blocked", "r") as f:
        block = f.read().strip()
    with open("browser", "r") as f:
        browser = f.read().strip()

    global openssave
    if os.path.exists("opens"):
        with open("opens", "r") as f:
            openssave = int(f.read().strip())
    else:
        openssave = 0

    return browser, block

def save_opens() -> None:
    with open("opens", "w") as f:
        f.write(str(openssave))

browser, block = init_config()
print(f"\nMonitoring browser: {browser}")
print(f"Blocking site: {block}\n")

def is_blocked_site(hwnd: int) -> Optional[str]:
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        proc = psutil.Process(pid)
        
        if browser not in proc.name().lower():
            return None

        title = win32gui.GetWindowText(hwnd).lower()
        if block in title:
            return block
    except Exception:
        pass
    return None

def close_browser() -> None:
    for proc in psutil.process_iter(['name']):
        if browser in proc.info['name'].lower():
            try:
                proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

def main() -> None:
    global opens, openssave
    
    try:
        while True:
            try:
                hwnd = win32gui.GetForegroundWindow()
                if is_blocked_site(hwnd):
                	close_browser()
                    opens += 1
                    openssave += 1
                    save_opens()
                    
                    time.sleep(1)

                    #print(f"You have now tried opening {block} {opens} time(s) while this has been open now, and {openssave} in total.")
            except Exception as e:
                print(f"An error occurred: {e}")
                
            time.sleep(check)
    except KeyboardInterrupt:
        print("\nStopping site blocker...")

if __name__ == "__main__":

    main()

