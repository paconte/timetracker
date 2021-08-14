# Coppyright (c) 2020 Francisco Javier Revilla Linares to present.
# All rights reserved.
import logging

from timetracker.Kimai2Controller import Kimai2Controller
from timetracker.Kimai2RestClient import Kimai2API
from timetracker.ctes import KIMAI2_URL, KIMAI2_USER, KIMAI2_PASSWORD
from timetracker.utils import get_logging_dict_config


# variables
logging.config.dictConfig(get_logging_dict_config())
logger = logging.getLogger('k2sync')

base_url = KIMAI2_URL
user0 = KIMAI2_USER
passwd = KIMAI2_PASSWORD

""" Script for synchronizing raspberry data with Kimai2.
This script is designed to be run regularly via cron job.
"""
if __name__ == "__main__":
    logger.info("############################")
    logger.info("Kimai2 syncronization starts.")

    api = Kimai2API(user0, passwd, base_url)
    k2c = Kimai2Controller(api)

    k2c.create_customer()
    k2c.create_project()
    k2c.create_activity()
    k2c.create_users()
    k2c.create_team_leader()
    k2c.create_team()
    k2c.create_timesheets()

    logger.info("Kimai2 syncronization finished.")
    logger.info("############################")
