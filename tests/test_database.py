# Coppyright (c) 2020 Francisco Javier Revilla Linares to present.
# All rights reserved.
import unittest
import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import timetracker.models as models
from timetracker.ctes import TEST_SQLITE_DB_FILE


class TestDatabase(unittest.TestCase):
    engine = create_engine('sqlite:///' + TEST_SQLITE_DB_FILE, echo=False)
    #engine = create_engine('sqlite:///:memory:')
    Session = sessionmaker(bind=engine)
    session = Session()

    @classmethod
    def setUpDownClass(cls):
        models.delete_file(TEST_SQLITE_DB_FILE)

    @classmethod
    def tearDownClass(cls):
        models.delete_file(TEST_SQLITE_DB_FILE)

    def setUp(self):
        models.Base.metadata.create_all(self.engine)

    def tearDown(self):
        models.Base.metadata.drop_all(self.engine)

    def test_setting_operation(self):
        company_name = "La Paleta"
        models.set_company(company_name, self.session)
        models.set_uuid(self.session)
        company = self.session.query(models.Setting).get("company")
        uuid_setting = self.session.query(models.Setting).get("uuid")
        uuid_real = uuid.UUID(uuid_setting.value)
        self.assertEqual(company.value, company_name)
        self.assertEqual(len(uuid_real.hex), 32)
        self.session.close()

    def test_init_database(self):
        setting = models.get_uuid(self.session)
        self.assertEqual(None, setting)
        models.init_database(self.session)
        setting = models.get_uuid(self.session)
        uuid_real = uuid.UUID(setting.value)
        self.assertEqual(len(uuid_real.hex), 32)

    def test_get_add_users(self):
        models.add_user("Alice", 0, self.session)
        models.add_user("Bob", 1, self.session)
        models.add_user("Peter", 2, self.session)

        user1 = models.get_user_by_template(0, self.session)
        user2 = models.get_user_by_template(1, self.session)
        user3 = models.get_user_by_template(2, self.session)

        self.assertEqual("Alice", user1.name)
        self.assertEqual("Bob", user2.name)
        self.assertEqual("Peter", user3.name)
        self.assertEqual(0, user1.template)
        self.assertEqual(1, user2.template)
        self.assertEqual(2, user3.template)

        users = self.session.query(models.User).all()
        self.assertEqual(3, len(users))

    def test_user_action_operations(self):

        models.add_user("Alice", 0, self.session)
        models.add_user("Bob", 1, self.session)
        models.add_user("Peter", 2, self.session)

        user1 = models.get_user_by_template(0, self.session)
        models.add_login(user1, self.session)

        user2 = models.get_user_by_template(1, self.session)
        models.add_login(user2, self.session)

        user2 = models.get_user_by_template(1, self.session)
        models.add_logout(user2, self.session)

        user3 = models.get_user_by_template(2, self.session)
        models.add_login(user3, self.session)
        user3 = models.get_user_by_template(2, self.session)
        models.add_logout(user3, self.session)

        user1 = models.get_user_by_template(0, self.session)
        models.add_logout(user1, self.session)

        actions = self.session.query(models.UserAction).all()
        self.assertEqual(len(actions), 6)

        models.truncate_user_actions(self.session)
        actions = self.session.query(models.UserAction).all()
        self.assertEqual(len(actions), 0)

        self.session.close()

    def test_user_consecutive_login(self):
        models.add_user("Alice", 0, self.session)

        # consecutives log in
        user1 = models.get_user_by_template(0, self.session)
        r = models.add_login(user1, self.session)
        self.assertEqual(True, r)
        actions = self.session.query(models.UserAction).all()
        self.assertEqual(len(actions), 1)

        user1 = models.get_user_by_template(0, self.session)
        r = models.add_login(user1, self.session)
        self.assertEqual(False, r)
        actions = self.session.query(models.UserAction).all()
        self.assertEqual(len(actions), 1)

    def test_user_consecutive_logout(self):
        models.add_user("Alice", 0, self.session)

        user1 = models.get_user_by_template(0, self.session)
        models.add_login(user1, self.session)

        user1 = models.get_user_by_template(0, self.session)
        r = models.add_logout(user1, self.session)
        self.assertEqual(0, r)
        actions = self.session.query(models.UserAction).all()
        self.assertEqual(2, len(actions))

        user1 = models.get_user_by_template(0, self.session)
        r = models.add_logout(user1, self.session)
        self.assertEqual(2, r)
        actions = self.session.query(models.UserAction).all()
        self.assertEqual(2, len(actions))

    def test_user_no_previous_login_by_logout(self):
        user1 = models.add_user("Alice", 0, self.session)

        user1 = models.get_user_by_template(0, self.session)
        r = models.add_logout(user1, self.session)
        self.assertEqual(1, r)
        actions = self.session.query(models.UserAction).all()
        self.assertEqual(0, len(actions))

