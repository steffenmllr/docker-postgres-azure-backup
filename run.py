#!/usr/bin/python3
import os
import sys
import subprocess
import datetime
from azure.storage.file import FileService
import requests, json
import time
start = time.time()

PGHOST = os.getenv("PGHOST")
PGPORT = os.getenv("PGPORT")
PGUSER = os.getenv("PGUSER")
PGPASSWORD = os.getenv("PGPASSWORD")
PGDATABASE = os.getenv("PGDATABASE")

AZURE_KEEP_BACKUPS = int(os.getenv("AZURE_KEEP_BACKUPS", 100))
AZURE_ACCOUNT_NAME = os.getenv("AZURE_ACCOUNT_NAME")
AZURE_ACCOUNT_KEY = os.getenv("AZURE_ACCOUNT_KEY")
AZURE_SHARE_NAME = os.getenv("AZURE_SHARE_NAME")
AZURE_BACKUP_FOLDER = os.getenv("AZURE_BACKUP_FOLDER", "backups")
AZURE_ENDPOINT_SUFFIX = os.getenv("AZURE_ENDPOINT_SUFFIX", "core.cloudapi.de")

SLACK_URL = os.getenv("SLACK_URL")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", '#server')

FILENAME = os.getenv("FILENAME", datetime.datetime.strftime(
    datetime.datetime.now(),  "%d-%m-%Y_%H-%M-%S_" + PGDATABASE))

# AZURE HELPER
def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def upload_callback(current, total):
    print('({}, {})'.format(sizeof_fmt(current), TOTAL_BACKUP_SIZE))

# Stack Helper
def slack_message(success=True, duration=0, deleted=[]):
    if SLACK_URL:
        payload = json.dumps({
            "channel": SLACK_CHANNEL,
            "username": "Mllrsohn Backup Bot - MBB",
            "text": "*[Backup::%s] %s Backup (backup)*" % ("success" if success else "failure", PGDATABASE),
            "icon_emoji": ":floppy_disk:",
            "attachments": [
                {
                    "fallback": "BACKUP STATUS",
                    "color": "good" if success else "danger",
                    "fields": [
                        {
                            "title": "Hostname",
                            "value": PGHOST,
                            "short": "false"
                        },
                        {
                            "title": "Database",
                            "value": PGDATABASE,
                            "short": "false"
                        },
                        {
                            "title": "Created Backup",
                            "value": FILENAME,
                            "short": "false"
                        },
                        {
                            "title": "Deleted Backups",
                            "value": ", ".join(deleted) if len(deleted) > 0 else "0",
                            "short": "false"
                        },
                        {
                            "title": "Duration",
                            "value": datetime.time(0, 0, duration).strftime("%M:%S"),
                            "short": "false"
                        }
                    ]
                }
            ]
        })
        headers = {'Content-Type': 'application/json'}
        requests.post(SLACK_URL, data=payload, headers=headers, timeout=5)

# PG DUMP
try:
    COMMANDS = ['pg_dump', '-F', 'c', '-b', '-v', '-f', './%s' % FILENAME]
    print("Running: '%s'" % (' '.join(COMMANDS)))
    exit_code = subprocess.call(COMMANDS)
    if exit_code is 1:
        raise Exception('Could not Backup, please check logs')

    # AZURE CONNECTION
    file_service = FileService(endpoint_suffix=AZURE_ENDPOINT_SUFFIX,
                               account_name=AZURE_ACCOUNT_NAME, account_key=AZURE_ACCOUNT_KEY)

    # Check if AZURE_BACKUP_FOLDER exists, if not create it
    if not file_service.exists(AZURE_SHARE_NAME, AZURE_BACKUP_FOLDER):
        file_service.create_directory(AZURE_SHARE_NAME, AZURE_BACKUP_FOLDER)

    # Upload
    print("uploading to: '%s/%s/%s'" % (AZURE_SHARE_NAME, AZURE_BACKUP_FOLDER, FILENAME))
    file_service.create_file_from_path(AZURE_SHARE_NAME, AZURE_BACKUP_FOLDER, FILENAME, FILENAME, progress_callback=upload_callback)



    # Cleaning Backup Files
    backup_files = file_service.list_directories_and_files(AZURE_SHARE_NAME, AZURE_BACKUP_FOLDER)
    filenames = []
    for file in backup_files:
        filenames.append(file.name)

    files_to_delete = []
    if len(filenames) >= AZURE_KEEP_BACKUPS:
        files_to_delete = filenames[:(len(filenames) - AZURE_KEEP_BACKUPS)]
        for file in files_to_delete:
            file_service.delete_file(AZURE_SHARE_NAME, AZURE_BACKUP_FOLDER, file)
    end = time.time()
    duration = int(end - start)
    slack_message(success=True, duration=duration, deleted=files_to_delete)
except:
    end = time.time()
    duration = int(end - start)
    slack_message(success=False, duration=duration, deleted=[])

