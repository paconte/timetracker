# Coppyright (c) 2020 Francisco Javier Revilla Linares to present.
# All rights reserved.
import requests
import datetime

from time import sleep
from requests.auth import HTTPBasicAuth
from utils import local_date_to_utc
from utils import date_to_kimai_date


class Kimai2API:

    def __init__(self, user, passwd, base_url):
        self.base_url = base_url
        self.user = user
        self.passwd = passwd
        self.headers = {
            "X-AUTH-USER": self.user,
            "X-AUTH-TOKEN": self.passwd
        }

    def get_action(self, action, id=None):
        self.url = self.base_url + action
        if id is not None:
            self.url += '/{:d}'.format(id)
        resp = requests.get(self.url, headers=self.headers)
        return resp

    def post_action(self, action, params):
        self.url = self.base_url + action
        resp = requests.post(self.url, headers=self.headers, json=params)
        return resp

    def patch_action(self, action, params):
        self.url = self.base_url + action
        resp = requests.patch(self.url, headers=self.headers, json=params)
        return resp

    def delete_action(self, action, params):
        self.url = self.base_url + action
        resp = requests.delete(self.url, headers=self.headers, json=params)
        return resp

    def get_activities(self):
        return self.get_action('activities')

    def get_activity(self, id):
        return self.get_action('activities', id)

    def get_customers(self):
        return self.get_action('customers')

    def get_customer(self, id):
        return self.get_action('customers', id)

    def get_projects(self):
        return self.get_action('projects')

    def get_project(self, id):
        return self.get_action('projects', id)

    def get_teams(self):
        return self.get_action('teams')

    def get_team(self, id):
        return self.get_action('teams', id)

    def get_timesheets(self):
        return self.get_action('timesheets')

    def get_timesheet(self, id):
        return self.get_action('timesheets', id)

    def get_users(self):
        return self.get_action('users')

    def create_customer(self, name, country, currency, tz, color):
        params = {
            "name": name,
            "country": country,
            "currency": currency,
            "timezone": tz,
            "color": color,
            "visible": True
        }
        return self.post_action('customers', params)

    def create_project(self, name, customer_id, color):
        params = {
            "name": name,
            "customer": customer_id,
            #"color": color,
            "visible": True
        }
        return self.post_action('projects', params)

    def create_team(self, name, leader_id):
        params = {
            "name": name,
            "teamlead": leader_id,
            "users": []
        }
        return self.post_action('teams', params)

    def create_timesheet(self, begin, end, project, activity):
        params = {
            "begin": str(begin),
            "end": str(end),
            "project": project,
            "activity": activity
        }
        return self.post_action('timesheets', params)

    def create_user(self, username, email, lang, tz, passwd):
        params = {
            "username": username,
            "email": email,
            "language": lang,
            "timezone": tz,
            "plainPassword": passwd,
            "enabled": True
        }
        return self.post_action('users', params)

    def create_team_leader(self, username, email, lang, tz, passwd):
        params = {
            "username": username,
            "email": email,
            "language": lang,
            "timezone": tz,
            "plainPassword": passwd,
            "roles": ["ROLE_TEAMLEAD"],
            "enabled": True
            }
        return self.post_action('users', params)

    def delete_user(self, id):
        params = {
            "id": id
        }
        return self.delete_action('users', params)

    def delete_team(self, id):
        params = {
            "id": id
        }
        return self.delete_action('teams', params)

    def delete_customer(self, id):
        params = {
            "id": id
        }
        return self.delete_action('customers', params)

    def delete_project(self, id):
        params = {
            "id": id
        }
        return self.delete_action('projects', params)


if __name__ == "__main__":

    # variables
    base_url = 'http://192.168.1.45:8001/api/'
    user0 = 'admin'
    user1 = 'Isaac'
    user2 = 'Paco'
    passwd = 'adminadmin'

    # init
    api = Kimai2API(user0, passwd, base_url)

    # calls
    '''
    sleep(1)
    resp = api.get_timesheets()
    print('timesheets', resp)
    for t in resp:
        print('timesheet', t)

    sleep(1)
    resp = api.get_timesheet(1)
    print("timesheet", resp)



    begin = datetime.datetime(2020, 1, 1, 9, 0)
    end = datetime.datetime(2020, 1, 1, 10, 0)
    begin_dt = date_to_kimai_date(local_date_to_utc(begin, "Europe/Madrid"))
    end_dt = date_to_kimai_date(local_date_to_utc(end, "Europe/Madrid"))
    resp = api.post_timesheets("2019-04-20T14:00:00", "2019-04-20T15:00:00", 1, 1)
    #print(begin, end, begin_dt, end_dt)
    print("POST - timesheets", resp)
    if resp.status_code == 200:
        print(resp.json())


    utc_dt = local_date_to_utc(datetime.datetime.now(), "Europe/Madrid")
    kimai_dt = date_to_kimai_date(utc_dt)
    print(utc_dt.strftime ("%Y-%m-%d %H:%M:%S"))
    print(kimai_dt)
    print(datetime.datetime.now())

    ## test create user
    resp = api.create_user("paconte", "paconte@gmail.com", "es", "Europe/Madrid", "pako666")
    print(resp)
    print(resp.json())
   '''

    resp = api.get_customers()
    print(resp)
    print(resp.json())
    resp = api.get_activities()
    print(resp)
    print(resp.json())
