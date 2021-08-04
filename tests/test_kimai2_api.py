import pytest

from timetracker.Kimai2RestClient import Kimai2API
from timetracker.ctes import KIMAI2_URL
from timetracker.utils import get_random_string


API = Kimai2API("admin", "foobar123", KIMAI2_URL)

def test_get_customers():
    resp = API.get_customers()
    assert resp.status_code == 200


def test_get_activities():
    resp = API.get_activities()
    assert resp.status_code == 200


def test_get_timesheets():
    resp = API.get_timesheets()
    timesheets = resp.json()

    assert resp.status_code == 200
    if len(timesheets) > 0:
        resp = API.get_timesheet(0)
        assert resp.status_code == 200


def test_create_user():
    username = "random_" + get_random_string(6)
    email = f"{username}@gmail.com"
    password = get_random_string(10)
    resp = API.create_user(username, email, "es", "Europe/Madrid", password)
    assert resp.status_code == 200


