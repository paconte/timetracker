# Fingerprint timetracking with a raspberry-pi

## Background
Currently the European Union force to all the companies to keep a record of all employees working times. The application is compliant with the EU requirements.

## Description
This is a python application running on a raspberry-pi with a fingerprint reader. It records all employees clockin and clock out in timesheets that are automatically uploaded to a Kima2 application on the cloud. The project is originally designed for restaurants, 

## Technologies

### Software

- The application is mainly written in python3.
- Ansible is used for automatic deployment into a raspbian operating system.
- The application also contain some bash script
- A single C file for generating WiFi configurations.

### Hardware requirements
- Raspberry-pi 4. It has not been tested with other raspberry pies.
- Real Time Clock. The raspberry-pi has no hardware clock.
- Fingerprint reader. It should be compatible with ZhianTec (ZFM-20, ZFM-60, ZFM-70 and ZFM-100). Visit the driver website https://github.com/bastianraschke/pyfingerprint for more information.
- Touch screen. For this project I used the official raspberry-pi 7 inches touch screen.
- A custom hardcase. You can use a 3d printer for it.

## Installation (last edit 24.04.2020)

Install the latest raspberian OS into your raspberry-pi.

To continue with ansible installation you have to copy your ssh-key into the raspberry-pi. You can use the below command where the USERNAME value is your username at the raspberry pi and the IP-ADDRES value is the ip addres of the raspberry pi.


`ssh-copy-id <USERNAME>@<IP-ADDRESS>`


Install ansible in the local machine.

`sudo apt install ansible`

Edit the file ansible/inventory.yml and set the ip value of your raspberry and your local source code path:

```yaml
raspberry_pies:
  hosts:
    192.168.1.113 # set your raspberry ip here
  vars:
    src_project: /home/paconte/devel/timetracker # set your src path here
```

Set up the hardware clock in your raspberry OS, a couple of howtoes: [howto1](https://pimylifeup.com/raspberry-pi-rtc/), [howto2](https://thepihut.com/blogs/raspberry-pi-tutorials/17209332-adding-a-real-time-clock-to-your-raspberry-pi)

Edit the file src/ctes.py for your needs, but at least set the following variables:

```python
# Raspbian file constants
PROD_PATH = '/home/pi/timetracker'
DEVEL_PATH = '/home/paconte/devel/timetracker'
```

Edit the file src/ctes.py to set up your customers values:

```python
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
COMPANY_LEADER_PASSWORD = ""
COMPANY_USER_PASSWORD = ""
COMPANY_USER_EMAIL = "@" + COMPANY_SHORT_NAME + COMPANY_EMAIL_EXTENSION
```

Install Kimai2 on an external machine. (Currently only has been tested in a external server and not locally on the raspberry-pi).

Edit the file src/ctes.py and configure your kimai2 variables:
```python
#kimai2 variables
KIMAI2_URL = "http://192.168.1.107/api/" # this is an example
KIMAI2_USER = ""
KIMAI2_PASSWORD = ""
```

Run ansible set up your raspberry-pi:

`ansible-playbook -i inventory.yml playbook.yml`


## Logging

The syncronization with the kimai2 server is logger by default into: `/home/pi/timetracker/logs/k2sync.log`

The app logs are in `/var/log/syslog`. This need an improvement and the log file should be in `/home/pi/timetracker/logs` as well.


## Fingerprint reader and raspberry pi connection

I am using `DollaTek Blau Licht Optischer Fingerabdruckleser Sensormodul für Arduino Mega2560 UNO R3` (https://www.amazon.de/gp/product/B07PRMXXXN/ref=ppx_yo_dt_b_asin_title_o06_s00?ie=UTF8&psc=1).

### Cable configuration (it might be different for your fingerprint device)

The red cable is 3.3V

The white cable is TxD

The yellow cable is RxD

The black cable is GND
