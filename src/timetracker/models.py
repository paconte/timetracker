# Coppyright (c) 2020 Francisco Javier Revilla Linares to present.
# All rights reserved.
import datetime
import enum
import logging
import os

from timetracker.ctes import (
    SQLITE_DB_FILE,
    TEST_SQLITE_DB_FILE,
    TABLE_NAME_USER,
    TABLE_NAME_USER_ACTION,
    TABLE_NAME_SETTING,
    TABLE_NAME_TIMESHEET,
    COMPANY_NAME,
    COMPANY_SHORT_NAME,
    COMPANY_LANGUAGE,
    COMPANY_TZ,
    COMPANY_LEADER_NAME,
    COMPANY_LEADER_EMAIL,
    COMPANY_LEADER_PASSWORD,
    COMPANY_COLOR,
    COMPANY_COUNTRY,
    COMPANY_CURRENCY,
    COMPANY_USER_EMAIL,
    COMPANY_USER_PASSWORD,
    COMPANY_PROJECT
)

from sqlalchemy import create_engine
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Enum
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.declarative import declarative_base


logger = logging.getLogger(__name__)

Base = declarative_base()
#engine = create_engine(f"sqlite:////{SQLITE_DB_FILE}", echo=False)
#engine = create_engine('sqlite:////home/pi/timetracker/src/timetracker/sqlite3.db', echo=False)
engine = create_engine('sqlite:////home/pi/timetracker/src/sqlite3.db', echo=False)


_SessionFactory = sessionmaker(bind=engine)
#Session = sessionmaker()
#Session.configure(bind=engine)
#session = Session()

# models

class Setting(Base):
    __tablename__ = TABLE_NAME_SETTING

    name = Column(String(50), primary_key=True)
    value = Column(String(1024))
    k2 = Column(Boolean, default=False, nullable=False)
    k2_id = Column(Integer, nullable=True)


class UserActionEnum(enum.Enum):
    login = 1
    logout = 2
    error = 3


class User(Base):
    __tablename__ = TABLE_NAME_USER

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    template = Column(Integer, unique=True, nullable=False)
    k2_name =  Column(String(50), nullable=False)
    k2_id = Column(Integer, unique=True, nullable=True)
    k2_password = Column(String(50), nullable=True)
    k2_email = Column(String(50), nullable=True)


class UserAction(Base):
    __tablename__ = TABLE_NAME_USER_ACTION

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    action = Column(Enum(UserActionEnum), nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)

    user = relationship('User', foreign_keys='UserAction.user_id')

    def __prepr__(self):
        return "<UserAction(%s, %s)>" % (self.action, self.user.name)


class Timesheet(Base):
    __tablename__ = TABLE_NAME_TIMESHEET

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    #begin = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    begin = Column(DateTime, default=datetime.datetime.now(), nullable=False)
    end = Column(DateTime, default=None, nullable=True)
    k2_id = Column(Integer, unique=True, nullable=True)

    user = relationship('User', foreign_keys='Timesheet.user_id')


def _single_commit(instance, session):
    session.add(instance)
    session.commit()
    session.close()


def _single_commit_unclosed(instance, session):
    session.add(instance)
    session.commit()


def _get_last_user_action(user, session):
    return session.query(
        UserAction).filter_by(
            user_id=user.id).order_by(
                UserAction.created_at.desc()).first()


def _get_last_timesheet(user, session):
    return session.query(
        Timesheet).filter_by(
            user_id=user.id).order_by(
                Timesheet.begin.desc()).first()


def session_factory():
    return _SessionFactory()


def delete_file(filename):
    # if db exsist delete it
    if os.path.isfile(filename):
        logger.info("Delete database {}".format(filename))
        os.remove(filename)


def create_database(filename):
    logger.info("Delete database file.")
    delete_file(filename)
    logger.info("Create the database and tables")
    Base.metadata.create_all(engine)
    logger.info("Initialize database")
    init_database()


def init_database():
    logger.info("DB => Initialize the database.")
    set_company(COMPANY_NAME, session_factory())
    set_country(COMPANY_COUNTRY, session_factory())
    set_currency(COMPANY_CURRENCY, session_factory())
    set_color(COMPANY_COLOR, session_factory())
    set_company_short(COMPANY_SHORT_NAME, session_factory())
    set_language(COMPANY_LANGUAGE, session_factory())
    set_timezone(COMPANY_TZ, session_factory())
    set_team(COMPANY_SHORT_NAME, session_factory())
    set_project(COMPANY_PROJECT, session_factory())
    set_customer(COMPANY_SHORT_NAME, session_factory())
    set_leader_email(COMPANY_LEADER_EMAIL, session_factory())
    set_leader(COMPANY_LEADER_NAME, session_factory())
    set_leader_password(COMPANY_LEADER_PASSWORD, session_factory())
    set_user_password(COMPANY_USER_PASSWORD, session_factory())
    set_user_email(COMPANY_USER_EMAIL, session_factory())
    set_uuid(session_factory())
    logger.info("DB => Database initialized.")


def add_user(name, template, session):
    short_name = get_company_short(session_factory()).value
    email = get_user_email(session_factory()).value
    k2_name = "{}_{}".format(name, short_name)
    k2_email = "{}{}".format(name, email)
    k2_password = get_user_password(session_factory()).value

    if short_name is None:
        logger.error("Failed to create user, no company short name defined.")
        return
    if k2_email is None:
        logger.error("Failed to create user, no kimai2 email defined.")
        return
    if k2_password is None:
        logger.error("Failed to create user, no kimai2 password defined.")
        return

    user = User(
        name=name,
        template=template,
        k2_name=k2_name,
        k2_id=None,
        k2_email=k2_email,
        k2_password=k2_password
    )
    _single_commit(user, session)


def set_user_kimai2_id(user, kimai2_id, session):
    user.k2_id = kimai2_id
    _single_commit_unclosed(user, session)


def get_user_by_template(template, session):
    result = session.query(User).filter_by(template=template).one()
    session.close()
    return result


def get_user_by_name(name, session):
    result = session.query(User).filter_by(name=name).one_or_none()
    session.close()
    return result


def get_user_by_id(id, session):
    result = session.query(User).get(id)
    session.close()
    return result


def exists_user(username, session):
    result = session.query(User).filter_by(name=username).first()
    session.close()
    if None == result:
        return False
    else:
        return True


def delete_user(username, session):
    session.query(User).filter_by(name=username).delete()
    session.commit()
    session.close()


def truncate_user_actions(session):
    stm1 = 'DELETE FROM '+ TABLE_NAME_USER_ACTION
    #stm2 = 'VACUUM'
    session.execute(stm1)
    #session.execute(stm2)
    session.commit()
    session.close()


def add_login(user, session):
    last_action = _get_last_user_action(user, session)

    if last_action is None or last_action.action == UserActionEnum.logout:
        # allow login after logout or no action
        login_action = UserAction(
            action=UserActionEnum.login,
            user=user)
        _single_commit(login_action, session)
        result = True
    else:
        # do not allow consecutives logins
        result = False

    return result


def add_logout(user, session):
    last_action = _get_last_user_action(user, session)

    if last_action is None:
        # do not allow logout without login
        result = 1
    elif last_action.action == UserActionEnum.logout:
        # do not allow consecutives logouts
        result = 2
    else:
        # allow logout after login
        logout_action = UserAction(
            action=UserActionEnum.logout,
            user=user)
        _single_commit(logout_action, session)
        result = 0

    return result


def add_login2(user, session):
    result = False # do not allow consecutives logins
    last_action = _get_last_timesheet(user, session)
    # allow login after logout or no action
    if last_action is None or last_action.end is not None:
        timesheet = Timesheet(user=user)
        _single_commit(timesheet, session)
        result = True

    return result


def add_logout2(user, session):
    result = 3 # unknown error
    last_action = _get_last_timesheet(user, session)
    if last_action is None:
        # do not allow logout without login
        result = 1
    elif last_action.end is not None:
        # do not allow consecutives logouts
        result = 2
    elif last_action.end is None:
        # allow logout after login
        last_action.end = datetime.datetime.now()
        datetime.datetime.utcnow
        _single_commit(last_action, session)
        result = 0

    return result


def add_setting(name, value, session):
    setting = session.query(Setting).get(name)
    if setting:
        setting.value = value
    else:
        setting = Setting(
            name=name,
            value=value
        )
    _single_commit(setting, session)


def add_kimai2_setting(key, value, k2_id, session):
    setting = session.query(Setting).get(key)
    k2 = False if k2_id is None else True
    if setting:
        setting.value = value
        setting.k2 = k2
        setting.k2_id = k2_id
    else:
        setting = Setting(name=key, value=value, k2=k2, k2_id=k2_id)
    _single_commit(setting, session)


def get_new_kimai2_users(session):
    result = session.query(User).filter(User.k2_id == None)
    return result


def get_new_kimai2_timesheets(session):
    result = session.query(Timesheet).options(joinedload('user')).\
        filter(Timesheet.k2_id == None).\
            filter(Timesheet.end != None).\
                filter(Timesheet.begin != None)
    return result


def set_timesheet_kimai_id(timesheet, kimai2_id, session):
    timesheet.k2_id = kimai2_id
    _single_commit_unclosed(timesheet, session)


def set_company(company_name, session):
    add_setting("company", company_name, session)


def get_company(session):
    result = session.query(Setting).get('company')
    session.close()
    return result


def set_uuid(session):
    import uuid
    value = uuid.uuid4()
    add_setting("uuid", str(value), session)


def get_uuid(session):
    result = session.query(Setting).get('uuid')
    session.close()
    return result


def get_company_short(session):
    result = session.query(Setting).get('company_short')
    session.close()
    return result


def set_company_short(name, session):
    add_setting("company_short", name, session)


def get_leader_email(session):
    result = session.query(Setting).get('leader_email')
    session.close()
    return result


def set_leader_email(email, session):
    add_setting("leader_email", email, session)


def get_leader_password(session):
    result = session.query(Setting).get('leader_password')
    session.close()
    return result


def set_leader_password(passwd, session):
    add_setting("leader_password", passwd, session)


def get_user_email(session):
    result = session.query(Setting).get('user_email')
    session.close()
    return result


def set_user_email(email, session):
    add_setting("user_email", email, session)


def get_user_password(session):
    result = session.query(Setting).get('user_password')
    session.close()
    return result


def set_user_password(passwd, session):
    add_setting("user_password", passwd, session)


def get_language(session):
    result = session.query(Setting).get('language')
    session.close()
    return result


def set_language(lang, session):
    add_setting("language", lang, session)


def get_timezone(session):
    result = session.query(Setting).get('timezone')
    session.close()
    return result


def set_timezone(tz, session):
    add_setting("timezone", tz, session)


def get_leader(session):
    result = session.query(Setting).get('leader')
    session.close()
    return result


def set_leader(name, session, k2_id=None):
    add_kimai2_setting('leader', name, k2_id, session)


def get_customer(session):
    result = session.query(Setting).get('customer')
    session.close()
    return result


def set_customer(name, session, k2_id=None):
    add_kimai2_setting('customer', name, k2_id, session)


def get_project(session):
    result = session.query(Setting).get('project')
    session.close()
    return result


def set_project(name, session, k2_id=None):
    add_kimai2_setting('project', name, k2_id, session)


def get_team(session):
    result = session.query(Setting).get('team')
    session.close()
    return result


def set_team(name, session, k2_id=None):
    add_kimai2_setting('team', name, k2_id, session)


def get_country(session):
    result = session.query(Setting).get('country')
    session.close()
    return result


def set_country(name, session):
    add_setting('country', name, session)


def get_currency(session):
    result = session.query(Setting).get('currency')
    session.close()
    return result


def set_currency(name, session):
    add_setting('currency', name, session)


def get_color(session):
    result = session.query(Setting).get('color')
    session.close()
    return result


def set_color(name, session):
    add_setting('color', name, session)
