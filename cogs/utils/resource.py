import psutil, os
from datetime import datetime

# check system's resource
def states(task:str, site:str):
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory()[2]
    time = datetime.now().strftime("%c")
    re = str(os.system(f'ping -c 1 {site}'))
    ping = re[re.find('time=')+len('time='):re.rfind('ms')]
    print(
            "Checking for " + task +
            " | Usage: CPU: " + str(cpu) +
            "% / RAM: " + str(memory) +
            "% / Site Ping: " + str(ping) +
            "ms | Time: " + str(time)
        )

def states_(task:str):
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory()[2]
    time = datetime.now().strftime("%c")
    print(
        "Checking for " + task +
        " | Usage: CPU: " + str(cpu) +
        "% / RAM: " + str(memory) +
        "% | Time: " + str(time)
    )