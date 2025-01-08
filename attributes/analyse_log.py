#!/usr/bin/env python3

import re
import os
from datetime import datetime

class Logs:
    def __init__(self, values):
        self.values = values
        self.logdate = datetime.now().strftime('%b %e')
        self.date = datetime.today().strftime('%Y-%m-%d')
        self.filepath = f'report-{self.date}.txt'

    def logSudo(self):
        sudo_log = '/var/log/sudo.log'
        if sudo_log not in self.values["log_files"] or not os.access(sudo_log, os.F_OK | os.R_OK):
            return False

        dirpath = 'logs/sudo'
        os.makedirs(dirpath, exist_ok=True)

        logfile_path = os.path.join(dirpath, self.filepath)
        pattern = rf'^{self.logdate}'

        with open(sudo_log) as sudo_file, open(logfile_path, 'w') as logfile:
            lines = sudo_file.readlines()
            for i in range(len(lines) - 1):  # Ensure no index error
                if re.search(pattern, lines[i]):
                    logfile.write(lines[i])
                    logfile.write(lines[i + 1])

        return True

    def logCron(self):
        cron_log = '/var/log/cron.log'
        if cron_log not in self.values["log_files"] or not os.access(cron_log, os.F_OK | os.R_OK):
            return False

        cron_dir = 'logs/cron'
        anacron_dir = 'logs/anacron'
        os.makedirs(cron_dir, exist_ok=True)
        os.makedirs(anacron_dir, exist_ok=True)

        cron_file_path = os.path.join(cron_dir, self.filepath)
        anacron_file_path = os.path.join(anacron_dir, self.filepath)

        cron_pattern = rf"^{self.logdate}.*CRON\[\d+\]"
        anacron_pattern = rf"^{self.logdate}.*anacron\[\d+\]"

        with open(cron_log) as cron_file:
            lines = cron_file.readlines()
            with open(cron_file_path, 'w') as cron_out:
                cron_out.writelines([line for line in lines if re.search(cron_pattern, line)])
            with open(anacron_file_path, 'w') as anacron_out:
                anacron_out.writelines([line for line in lines if re.search(anacron_pattern, line)])

        return True

    def logAuth(self):
        auth_log = '/var/log/auth.log'
        if auth_log not in self.values["log_files"] or not os.access(auth_log, os.F_OK | os.R_OK):
            return False

        dirpath = 'logs/auth'
        os.makedirs(dirpath, exist_ok=True)

        logfile_path = os.path.join(dirpath, self.filepath)
        auth_pattern = rf"^{self.logdate}.*(sshd|systemd-logind)\[\d+\]"

        with open(auth_log) as auth_file, open(logfile_path, 'w') as logfile:
            logfile.writelines([line for line in auth_file if re.search(auth_pattern, line)])

        return True
