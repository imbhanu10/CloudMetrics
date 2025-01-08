#!/usr/bin/env python3

# Import modules
try:
    import os
    import pwd
    import socket
    import platform
    from datetime import datetime, date
except ModuleNotFoundError as err:
    print(f"Cloudmetrics: Error: {err}. \nUse 'pip install' to install the module.")

# Log a report whenever the main program is executed
class WriteToAccessLog:
    def __init__(self):
        # Collect system information
        self.system_type = platform.system()
        self.user = pwd.getpwuid(os.geteuid())[0]  # Get effective user ID
        self.nodename = socket.gethostname()
        self.date = date.today()
        self.time = datetime.now().strftime("%H:%M:%S")

    def log(self):
        log_dir = "logs"
        log_file = os.path.join(log_dir, "access.log")
        
        # Ensure the logs directory exists
        if not os.path.isdir(log_dir):
            os.mkdir(log_dir)
        
        # Write access log entry
        with open(log_file, "a") as file:
            file.write(f"Cloudmetrics: {self.date} {self.time} {self.system_type} {self.nodename} {self.user}\n")
