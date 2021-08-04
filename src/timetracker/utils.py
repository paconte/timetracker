# Coppyright (c) 2020 Francisco Javier Revilla Linares to present.
# All rights reserved.
import subprocess
import paramiko
import datetime
import re
import os
import pathlib
import logging
import logging.config
import yaml
import pytz
import string
import random

from scp import SCPClient

from timetracker.ctes import (
    LOGGING_CONFIG,
    LOGGING_DEFAULT_LEVEL,
    SQLITE_DB_FILE,
    SQLITE_EXPORT_FILE,
    SERVER_URL,
    SSH_PORT,
    SSH_USER,
    SSH_PASSWORD,
    TABLE_NAME_USER_ACTION,
    TABLE_NAME_SETTING,
    SEND_DATA_SUBJECT,
    R_ERROR,
    R_INVALID_EMAIL,
    WIFI_C_CODE,
    WIFI_EXEC_FILE
)

from timetracker.models import (
    session_factory, UserAction, truncate_user_actions, get_uuid, get_company, get_company_short
)


logger = logging.getLogger(__name__)

def get_logging_dict_config():
    if os.path.exists(LOGGING_CONFIG):
        with open(LOGGING_CONFIG, 'rt') as f:
            config = yaml.safe_load(f.read())
    return config


def setup_logging():
    if os.path.exists(LOGGING_CONFIG):
        config = get_logging_dict_config()
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=LOGGING_DEFAULT_LEVEL)


def delete_file(filename):
    if os.path.isfile(filename):
        os.remove(filename)
        logger.info('File %s deleted', filename)


def _export_database_logs(filename):
    #sqlite3 -headers -csv ./sqlite3.db "query;"
    sql_str = 'SELECT (SELECT value FROM {setting} WHERE name = "uuid"), (SELECT value FROM {setting} WHERE name = "company"), created_at, action, user FROM {user_action};'
    sql = sql_str.format(setting=TABLE_NAME_SETTING, user_action=TABLE_NAME_USER_ACTION)
    sql = 'SELECT u.name, t.begin, t.end FROM timesheet t INNER JOIN user u ON t.user_id=u.id;'
    with open(filename, 'w') as fp:
        subprocess.run(['sqlite3', '-header', '-csv', '-separator', ';', SQLITE_DB_FILE, sql], stdout=fp)

    #sql = 'SELECT (SELECT value FROM setting WHERE name = "uuid"),
    #  (SELECT value FROM setting WHERE name = "company"), created_at, action, user FROM user_action;'


def _create_ssh_client():
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(SERVER_URL, SSH_PORT, SSH_USER, SSH_PASSWORD)
    return client


def upload_database():
    # find out filename to export
    uuid = get_uuid(session_factory()).value
    filename = uuid + "_" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "_" + SQLITE_EXPORT_FILE

    # export file
    _export_database_logs(filename)

    # upload file
    ssh = _create_ssh_client()
    scp = SCPClient(ssh.get_transport())
    scp.put(filename, filename)
    scp.close()

    # delete local exported file
    delete_file(SQLITE_EXPORT_FILE)

    # delete uploaded data from database
    session = session_factory()
    truncate_user_actions(session)


def send_data(email):
    try:
        # check email address
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return R_INVALID_EMAIL

        company = get_company(session_factory).value
        filename = company + "_" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "_" + SQLITE_EXPORT_FILE

        # export file
        _export_database_logs(filename)

        # send data
        subprocess.run(['mpack', '-s', SEND_DATA_SUBJECT, SQLITE_EXPORT_FILE, email])

        # delete local exported file
        delete_file(SQLITE_EXPORT_FILE)

        return 0

    except Exception:
        return R_ERROR


def export_data_to_usb():
    logger.info('Export data to the USB starts.')
    try:
        usb_path = "/media/pi/"

        # check usb has been mounted
        if not os.path.exists(usb_path):
            logger.error('The USB is not mounted.')
            return 2

        # check there is a directory to write
        dirs = os.listdir(usb_path)
        if len(dirs) != 1:
            logger.error('The USB has an unexpected directory structure.')
            return 3

        # export file into usb
        destination = usb_path + dirs[0] + "/registro_horario/"
        pathlib.Path(destination).mkdir(parents=True, exist_ok=True)
        company = get_company_short(session_factory()).value
        filename = company + "_" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "_" + SQLITE_EXPORT_FILE
        _export_database_logs(destination + filename)

        logger.info('Export data to the USB finished. Data exported to the USB.')
        return 0

    except Exception:
        logger.exception('Errors while exporting database data to the USB.')
        return R_ERROR


def create_wifi_executable():
    logger.info('Creating WiFi executable file')
    # create c executable file
    subprocess.run(['cc', WIFI_C_CODE, '-o', WIFI_EXEC_FILE])
    logger.info('WiFi executable file created')


def update_wifi_configuration(ssid, passwd):
    # set up new configuration
    logger.info('Update raspberry-pi WiFi configuration file')
    if 0 == len(passwd):
        os.system('sudo {0} {1}'.format(WIFI_EXEC_FILE, ssid))
    else:
        os.system('sudo {0} {1} {2}'.format(WIFI_EXEC_FILE, ssid, passwd))

    # load new configuration
    logger.info('Load new WiFi settings')
    os.system('wpa_cli -i wlan0 reconfigure')
    logger.info('WiFi settings updated')


def local_date_to_utc(date, timezone):
    local = pytz.timezone(timezone)
    local_dt = local.localize(date, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)
    return utc_dt


def date_to_kimai_date(date):
    return date.strftime ("%Y-%m-%dT%H:%M:%S")


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result = ''.join(random.choice(letters) for i in range(length))
    return result