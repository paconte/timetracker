# Coppyright (c) 2020 Francisco Javier Revilla Linares to present.
# All rights reserved.
import logging


# Raspbian file constants
PROD_PATH = '/home/pi/timetracker'
DEVEL_PATH = '/home/paconte/devel/timetracker'
PROJECT_PATH = PROD_PATH
LOGGING_CONFIG = PROJECT_PATH + '/src/logging.yml'
SQLITE_DB_FILE = PROJECT_PATH + '/src/sqlite3.db'
SQLITE_EXPORT_FILE = 'horarios.csv'
TEST_SQLITE_DB_FILE = 'test' + SQLITE_DB_FILE
TEST_SQLITE_EXPORT_FILE = 'test' + SQLITE_EXPORT_FILE

# Python logging constants
LOGGING_DEFAULT_LEVEL = logging.INFO

# Database constants
TABLE_NAME_SETTING = 'setting'
TABLE_NAME_USER_ACTION = 'user_action'
TABLE_NAME_USER = 'user'
TABLE_NAME_TIMESHEET = 'timesheet'
COLUMN_USERNAME_MAX_LENGTH = 50
COLUMN_USERNAME_MIN_LENGTH = 4

# Raspbian WiFi configuration constants
WIFI_CONFIG_HEADER = 'ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\nupdate_config=1\ncountry=ES\n\n'
WIFI_CONFIG_NO_PASSWD = 'network={{\n    ssid="{ssid}"\n    key_mgmt=NONE\n}}'
WIFI_CONFIG = 'network={{\n    ssid="{ssid}"\n    psk="{password}"\n    key_mgmt=WPA-PSK\n}}'
WIFI_TMP_CONFIG_FILE = PROJECT_PATH + '/wifi_config.txt'
WIFI_CONFIG_FILE = '/etc/wpa_supplicant/wpa_supplicant.conf'
WIFI_C_CODE = PROJECT_PATH + '/src/wifi.c'
WIFI_EXEC_FILE = PROJECT_PATH + '/src/wifi'
WIFI_SCRIPT = PROJECT_PATH + '/src/update_wifi.sh'

# Other ...
SEND_DATA_SUBJECT = '"Control horario de empleados"'
SEND_DATA_RECEIVER = 'paconte@gmail.com'
R_INVALID_EMAIL = 2

R_ERROR = 1

# Customers custom variables
COMPANY_NAME = "Restaurante Pizzeria la Palette"
COMPANY_SHORT_NAME = "palette"
COMPANY_TZ = "Europe/Madrid"
COMPANY_CURRENCY = "EUR"
COMPANY_COUNTRY = "ES"
COMPANY_LANGUAGE = "es"
COMPANY_COLOR = "#d2d6de"
COMPANY_LEADER_PREFIX = "admin_"
COMPANY_EMAIL_EXTENSION = ".com"
COMPANY_LEADER_NAME = COMPANY_LEADER_PREFIX + COMPANY_SHORT_NAME
COMPANY_LEADER_EMAIL = COMPANY_LEADER_NAME + "@" + COMPANY_SHORT_NAME + COMPANY_EMAIL_EXTENSION
COMPANY_LEADER_PASSWORD = "lapaletaapi"
COMPANY_USER_PASSWORD = "lapaletaapi"
COMPANY_USER_EMAIL = "@" + COMPANY_SHORT_NAME + COMPANY_EMAIL_EXTENSION

#kimai2 variables
KIMAI2_URL = "http://192.168.1.45:8001/api/" # this is an example
KIMAI2_USER = "admin"
KIMAI2_PASSWORD = "adminadmin"

# SSH constants
SERVER_URL = ''
SSH_PORT = 22
SSH_USER = ''
SSH_PASSWORD = ''
