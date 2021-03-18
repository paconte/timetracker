# Coppyright (c) 2020 Francisco Javier Revilla Linares to present.
# All rights reserved.
import logging
import models

from pyfingerprint import PyFingerprint


logger = logging.getLogger(__name__)

class FingerprintController:

    f = None
    RESULT_ERROR = -1
    RESULT_TEMPLATE_ALREADY_EXISTS = -2
    RESULT_FINGER_DO_NOT_MATCH = -3
    RESULT_NO_MATCH = -4

    def __init__(self):
        try:
            self.f = PyFingerprint('/dev/ttyS0', 57600, 0xFFFFFFFF, 0x00000000)
            if self.f.verifyPassword() == False:
                raise ValueError('The given fingerprint sensor password is wrong!')
        except Exception as e:
            logger.exception('The fingerprint sensor could not be initialized!')

    def __del__(self):
        del self.f

    def exists_user(self, username):
        return models.exists_user(username, models.session_factory())

    def add_user_step1(self):
        try:
            print('Waiting for finger...')

            ## Wait that finger is read
            while self.f.readImage() == False:
                pass

            ## Converts read image to characteristics and stores it in charbuffer 1
            self.f.convertImage(0x01)

            ## Checks if finger is already enrolled
            result = self.f.searchTemplate()
            positionNumber = result[0]

            if positionNumber >= 0:
                logger.warn('Template already exists at position #{}', str(positionNumber))
                return self.RESULT_TEMPLATE_ALREADY_EXISTS

            return 0

        except Exception as e:
            logger.exception('Error while adding a user (step1).')
            return self.RESULT_ERROR

    def add_user_step2(self, username):
        try:
            print('Waiting for finger...')

            ## Wait that finger is read again
            while self.f.readImage() == False:
                pass

            ## Converts read image to characteristics and stores it in charbuffer 2
            self.f.convertImage(0x02)

            ## Compares the charbuffers
            if self.f.compareCharacteristics() == 0:
                return self.RESULT_FINGER_DO_NOT_MATCH

            ## Creates a template
            self.f.createTemplate()

            ## Saves template at new position number
            template_index = self.f.storeTemplate()
            logger.info('Finger enrolled successfully. New template position #{}', str(template_index))

            ## save user in DB
            models.add_user(username, template_index, models.session_factory())
            return 0

        except Exception as e:
            logger.exception('Error while adding a user (step2).')
            return self.RESULT_ERROR

    def delete_user(self, username):
        user = models.get_user_by_name(username, models.session_factory())
        if None == user:
            logger.info('User \"{}\" does not exists and can not be deleted.', username)
            return
        position = user.template
        models.delete_user(username, models.session_factory())
        self.f.deleteTemplate(position)
        logger.info('User \"{}\" with template position #{} deleted.', username, str(position))

    def search_user(self):
        try:
            logger.info('Waiting for finger...')

            ## Wait that finger is read
            while self.f.readImage() == False:
                pass

            ## Converts read image to characteristics and stores it in charbuffer 1
            self.f.convertImage(0x01)

            ## Searchs template
            result = self.f.searchTemplate()

            positionNumber = result[0]
            accuracyScore = result[1]

            if positionNumber == -1:
                logger.warn('No fingerprint match found')
                return self.RESULT_NO_MATCH
            else:
                logger.info('Found template at position #{} with accuracy score of {}', str(positionNumber), str(accuracyScore))
                return positionNumber

        except Exception as e:
            logger.exception('Error while searching for a fingerprint template.')
            return self.RESULT_ERROR

    def delete_database(self):
        self.f.deleteDatabase()