# Coppyright (c) 2020 Francisco Javier Revilla Linares to present.
# All rights reserved.
import logging

from Kimai2Controller import Kimai2Controller
from Kimai2RestClient import Kimai2API
from ctes import KIMAI2_URL
from ctes import KIMAI2_USER
from ctes import KIMAI2_PASSWORD
from utils import get_logging_dict_config


# variables
logger = logging.getLogger(__name__)
logging.config.dictConfig(get_logging_dict_config())


base_url = KIMAI2_URL
user0 = KIMAI2_USER
passwd = KIMAI2_PASSWORD

""" Script for synchronizing raspberry data with Kimai2.
This script is designed to be run regularly via cron job.
"""
if __name__ == "__main__":
    logger.info("Kimai2 syncronization starts.")
    api = Kimai2API(user0, passwd, base_url)
    k2c = Kimai2Controller(api)
    k2c.create_team_leader()
    k2c.create_team()
    k2c.create_customer()
    k2c.create_project()
    k2c.create_users()
    k2c.create_timesheets()
    logger.info("Kimai2 syncronization finished.")
