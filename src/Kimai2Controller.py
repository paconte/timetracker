# Coppyright (c) 2020 Francisco Javier Revilla Linares to present.
# All rights reserved.
''' Controller with all the interactions method with Kimai2

The purpouse of this file is to syncronize the local data with a remote Kimai2 application.

A cronjob or diffrent cronjobs should regularly check for the following:
1) If there are new local users synchronize with Kimai2
2) If there are new local timesheets synchronize with Kimai2
3) This is not implemented and might not be needed; If there are
 deleted users synchronize with Kimai2

Additionally, when the app is installed for the first time, an activity, a project and
a team leader must be created in Kimai2.
'''
import logging
import Kimai2RestClient
import models

from ctes import COMPANY_LEADER_PREFIX
from ctes import COMPANY_EMAIL_EXTENSION
from ctes import COMPANY_TZ
from ctes import COMPANY_LANGUAGE
from ctes import COMPANY_COUNTRY
from ctes import COMPANY_COLOR
from ctes import COMPANY_CURRENCY
from ctes import KIMAI2_URL
from ctes import COMPANY_LEADER_PASSWORD

from utils import local_date_to_utc
from utils import date_to_kimai_date


logger = logging.getLogger(__name__)


class Kimai2Controller:

    def __init__(self, api):
        self.api = api

    def create_team_leader(self):
        create_team_leader(self.api)

    def create_team(self):
        create_team(self.api)

    def create_customer(self):
        create_customer(self.api)

    def create_project(self):
        create_project(self.api)

    def create_users(self):
        create_users(self.api)

    def create_timesheets(self):
        create_timesheets()


def create_team_leader(api):
    # check if is already created
    leader_id = models.get_leader(models.session_factory()).k2_id
    if leader_id is not None:
        return

    # collect info
    username = models.get_leader(models.session_factory()).value
    email = models.get_leader_email(models.session_factory()).value
    lang = models.get_language(models.session_factory()).value
    tz = models.get_timezone(models.session_factory()).value
    password = models.get_leader_password(models.session_factory()).value

    try:
        # create team leader in Kimai2
        resp = api.create_team_leader(username, email, lang, tz, password)
        if resp.status_code != 200:
            logger.error("Failed to create team leader in Kimai2: %s", username)
            logger.error("Status: {}, Values: {}, {}, {}, {}".format(
                str(resp.status_code), username, email, lang, tz))
            logger.error(resp.json())
            return
        # update local database
        obj = resp.json()
        models.set_leader(obj['username'], models.session_factory(), obj['id'])
        logger.info("Team leader created: {}, {}".format(obj['id'], obj['username']))
    except Exception:
        logging.exception("Failed to create a team leader in Kimai2: %s", username)


def create_team(api):
    # check if is already created
    team = models.get_team(models.session_factory()).k2_id
    if team is not None:
        return

    # check 2
    leader_id = models.get_leader(models.session_factory()).k2_id
    name = models.get_company_short(models.session_factory()).value
    if leader_id is None:
        logging.error("Failed to create a team in Kimai2: %s. There is no team leader.", name)
        return

    try:
        # create team in Kima2
        resp = api.create_team(name, leader_id)
        if resp.status_code != 200:
            logger.error("Failed to create a team in Kima2: %s", name)
            logger.error("Status: {}, Values: {}, {}".format(str(resp.status_code), name, leader_id))
            logger.error(resp.json())
            return
        # update local database
        obj = resp.json()
        models.set_team(name, models.session_factory(), leader_id)
        logger.info("Team created: {}, {}".format(obj['id'], obj['name']))
    except Exception:
        logging.exception("Failed to create a team in Kimai2: %s", name)


def create_customer(api):
    # check if is already created
    customer = models.get_customer(models.session_factory())
    if customer is not None and customer.k2_id is not None:
        return

    # collect info
    name = models.get_company_short(models.session_factory()).value
    country = models.get_country(models.session_factory()).value
    tz = models.get_timezone(models.session_factory()).value
    currency = models.get_currency(models.session_factory()).value
    color = models.get_color(models.session_factory()).value

    try:
        # create customer in Kimai2
        resp = api.create_customer(name, country, currency, tz, color)
        if resp.status_code != 200:
            logger.error("Failed to create customer in Kimai2: %s", name)
            logger.error("Status: {}, Values: {}, {}, {}, {}".format(
                str(resp.status_code), name, country, tz, color))
            logger.error(resp.json())
            return
        # update local database
        obj = resp.json()
        models.set_customer(obj['name'], models.session_factory(), obj['id'])
        logger.info("Customer created: {}, {}".format(obj['id'], obj['name']))
    except Exception:
        logging.exception("Failed to create customer in Kimai2: %s", name)


def create_project(api):
    # check if is already created
    project = models.get_project(models.session_factory())
    if project is not None and project.k2_id is not None:
        return

    # check
    leader = models.get_leader(models.session_factory())
    name = models.get_company_short(models.session_factory()).value
    if leader is None or leader.k2_id is None:
        logging.exception("Failed to create a project in Kimai2: %s. There is no customer.", name)
        return

    # collect info
    customer = models.get_customer(models.session_factory()).k2_id
    color = models.get_color(models.session_factory()).value

    try:
        # create project in Kimai2
        resp = api.create_project(name, customer, color)
        if resp.status_code != 200:
            logger.error("Failed to create project in Kimai2: %s", name)
            logger.error("Status: {}, Values: {}, {}, {}".format(
                str(resp.status_code), name, customer, color))
            logger.error(resp.json())
            return
        # update local database
        obj = resp.json()
        models.set_project(obj['name'], models.session_factory(), obj['id'])
        logger.info("Project created: {}, {}".format(obj['id'], obj['name']))
    except Exception:
        logging.exception("Failed to create project in Kimai2: %s", name)


def create_users(api):
    # check and collect info
    tz = models.get_timezone(models.session_factory()).value
    lang = models.get_language(models.session_factory()).value

    if tz is None:
        logger.error("Failed to create user in kimai2, no timezone defined.")
        return
    elif lang is None:
        logger.error("Failed to create user in kimai2, no language defined.")
        return

    # collect not created users
    session = models.session_factory()
    users = models.get_new_kimai2_users(session)
    # create users
    for user in users:
        try:
            resp = api.create_user(user.k2_name, user.k2_email, lang, tz, user.k2_password)
            if resp.status_code != 200:
                # wrong hhtp response, log error
                logger.error("Failed to create user in Kimai2")
                logger.error("Status: {}, Values: {}, {}, {}, {} {}".format(
                    str(resp.status_code),
                    user.k2_name, user.k2_email, lang, tz, user.k2_password))
                logger.error(resp.json())

            else:
                # right http response, update local database
                obj = resp.json()
                models.set_user_kimai2_id(user, obj['id'], session)
                logger.info("User created: {}, {}".format(obj['id'], obj['username']))
        except Exception:
            logging.exception("Failed to create user {}".format(user.name))

    session.close()


def create_timesheets():
    # checks
    project = models.get_project(models.session_factory()).k2_id
    tz = models.get_timezone(models.session_factory()).value
    password = models.get_user_password(models.session_factory()).value
    url = KIMAI2_URL
    if project is None:
        logger.error("Failed to create timesheet in kimai2, no project id.")
        return
    if tz is None:
        logger.error("Failed to create timesheet in kimai2, no timezone defined.")
        return
    if password is None:
        logger.error("Failed to create timesheet in kimai2, no user password defined.")
        return

    # fetch all timesheets to be uploaded
    session = models.session_factory()
    timesheets = models.get_new_kimai2_timesheets(session)

    # create timesheets
    for ts in timesheets:
        utc_begin = local_date_to_utc(ts.begin, tz)
        utc_end = local_date_to_utc(ts.end, tz)
        kimai2_begin = date_to_kimai_date(utc_begin)
        kimai2_end = date_to_kimai_date(utc_end)

        # api manager
        ##user_k2_id = models.get_user_by_id(ts.user_id).k2_id
        if ts.user.k2_id is None:
            logger.error("Failed to create timesheet in kimai2, user does not exists in kimai2.")
            return
        api = Kimai2RestClient.Kimai2API(ts.user.k2_name, ts.user.k2_password, url)

        try:
            logging.info("")
            resp = api.create_timesheet(kimai2_begin, kimai2_end, project, 1)
            if resp.status_code != 200:
                # wrong hhtp response, log error
                logger.error("Failed to create timesheet in Kimai2")
                logger.error("Status: {}, Values: {}, {}, {}, {}".format(
                    str(resp.status_code),
                    ts.user.k2_name, ts.user.k2_password, ts.begin, ts.end))
                logger.error(resp.json())
            else:
                # right http response, update local database
                obj = resp.json()
                models.set_timesheet_kimai_id(ts, obj['id'], session)
                logger.info("Timesheet created: {}, {}".format(kimai2_begin, kimai2_end, project, 1))
        except Exception:
            logging.exception("Failed to create timesheet")

    session.close()
