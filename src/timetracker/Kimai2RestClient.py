# Coppyright (c) 2020 Francisco Javier Revilla Linares to present.
# All rights reserved.
import requests


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

    def create_activity(self, name, project, color, visible=True):
        params = {
            "name": name,
            "project": project,
            "color": color,
            "visible": visible,
        }
        return self.post_action('activities', params)

    def create_team(self, name, leader_id):
        params = {
            "name": name,
            "teamlead": leader_id,
            "users": []
        }
        return self.post_action('teams', params)

    def create_timesheet(self, user, begin, end, project, activity):
        params = {
            "user": user,
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
