#!/usr/bin/env python3

from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from datetime import datetime
from enum import Enum, auto
import json
import logging
import json
import pprint as pp
import time

# TODO: Use config file
from credentials import EMAIL, PASSWORD


class PackageStatus(Enum):
    IN_TRANSIT = auto()
    DELIVERED = auto()
    UNKNOWN = auto()


class Package:
    def __init__(self, identifier, sender, status, delivery_date, tracking_url):
        self.identifier = identifier
        self.sender = sender
        self.status = status
        self.delivery_date = delivery_date
        self.tracking_url = tracking_url


    def __repr__(self):
        return str(self.__dict__)

class Scraper:
    def __init__(self, headless=True, email=EMAIL, password=PASSWORD):
        self.logger = logging.getLogger('SwissPostPackages.Scraper')
        self.email = email
        self.password = password

        options = Options()
        options.headless = headless
        service = Service(executable_path=GeckoDriverManager().install())
        self.driver = webdriver.Firefox(options=options, service=service)
        self.driver.implicitly_wait(10)

        self.logged_in = False

    
    def login(self):
        if not self.logged_in:
            self._login()


    def _login(self):
        self.logger.info('Logging in')

        self.logger.debug('Loading "My Post" page')
        login_url = 'https://www.post.ch/fr/espace-clients'
        self.driver.get(login_url)

        self.logger.debug('Clicking on button to log in with Swiss ID')
        self.driver.find_element(By.ID, 'externalIDP').click()

        self.logger.debug('Typing in e-mail address and password')

        email_field = self.driver.find_element(By.ID, 'email')
        email_field.clear()
        email_field.send_keys(self.email)

        password_field = self.driver.find_element(By.ID, 'password')
        password_field.clear()
        password_field.send_keys(self.password)

        self.logger.debug('Triggering login')
        password_field.send_keys(Keys.RETURN)

        self.logger.debug('Waiting until logged in')
        try:
            self.wait_until_url_contains('https://service.post.ch/kvm/app/ui/')
        except:
            raise Error('Could not log in. Did you provide the correct credentials?')
        time.sleep(2) # Browser seems overwhelmed if we move on too quickly
        self.logger.debug('Logged in!')
        self.logged_in = True


    def fetch_packages_json(self):
        self.logger.info('Fetching packages')
        self.driver.get('view-source:https://service.post.ch/kvm/app/api/api/activities?page=0&limit=1000&lang=en')
        json_string = self.driver.find_element(By.TAG_NAME, 'pre').text
        result = json.loads(json_string)
        return result


    def wait_until_url_contains(self, partial_url):
        self.logger.debug('Waiting until URL contains %s', partial_url)
        return WebDriverWait(self.driver, 10).until(self.url_contains_function(partial_url))

    
    def url_contains_function(self, partial_url):
        def condition(driver):
            return partial_url in driver.current_url
        return condition


    def fetch_packages(self):
        self.login()
        packages = [self.to_package(data) for data in self.fetch_packages_json() if 'type' in data and data['type'] == 'PARCEL']
        return packages


    def to_package(self, data):
        package = Package(data['id'], 
                          data['summary'], 
                          self.to_status(data['statusType']), 
                          datetime.fromisoformat(data['date']) if 'date' in data else None, 
                          data['actions'][0]['url'])
        return package


    def to_status(self, status_type):
        if status_type == 'ON_GOING_DELIVERY':
            return PackageStatus.IN_TRANSIT
        elif status_type == 'DELIVERED':
            return PackageStatus.DELIVERED
        else:
            self.logger.warn('Unknown package status: %s' % status_type)
            return PackageStatus.UNKNOWN


class App:
    def __init__(self):
        self.logger = logging.getLogger('SwissPostPackages.App')
        self.scraper = Scraper()
        self.packages_list = None

    @property
    def packages(self):
        if self.packages_list is None:
            self.packages_list = self.scraper.fetch_packages()
        return self.packages_list



if __name__ == '__main__':
    logging.basicConfig()
    logger = logging.getLogger('SwissPostPackages')
    logger.setLevel(logging.DEBUG)

    app = App()
    packages = app.packages
    pp.pprint(packages)
