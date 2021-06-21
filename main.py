from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import common

import datetime
from time import sleep


class Scheduler():
    """
    Wrapper class for automated gym time scheduler
    """

    def __init__(self):
        """
        Store credentials in text file in same directory as program
        Format of text file:
            Username
            Password

        """

        self.credentials = open('credentials.txt', 'r')
        self.username = self.credentials.readline()
        self.password = self.credentials.readline()
        self.credentials.close()

        options = webdriver.ChromeOptions()
        options.binary_location = r'D:\Program Files\Google\Chrome\Application\chrome.exe'

        self.driver = webdriver.Chrome(r'.\chromedriver.exe', options=options)
        self.driver.maximize_window() # some of the webpage elements change between full screen and not

        self.date = datetime.date.today() + datetime.timedelta(days=3) # can only register a maximum of 3 days in advance

        self.timeslot = 22  # corresponds to 3pm

        self.xpaths = {"reserve_workout": "//a[contains(text(),'Reserve Your Workout Time')]",
                       "date_picker": "//*[@id=\"primary-view\"]/div/div[1]/div/div[3]/input"}

    def login(self):
        self.driver.get("https://fitnessworld.mosomyclub.com/login.aspx#")
        self.driver.find_element_by_id("username").send_keys(self.username)
        self.driver.find_element_by_id("password").send_keys(self.password)
        self.driver.find_element_by_id("moso-login-button").click()
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, self.xpaths["reserve_workout"])))

    def find_appointment(self):
        self.driver.find_element_by_xpath(self.xpaths["reserve_workout"]).click()
        WebDriverWait(driver=self.driver, timeout=10).until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                                            ".btn-primary")))
        for i in range(3):
            "Even with the wait, sometimes get a stale reference error, this is a stopgap fix while I research" \
            "the reason that it's occuring"
            try:
                self.driver.find_element_by_css_selector(
                    ".btn-primary").click() # .btn-primary refers to the 'Select Location' button

                self.driver.find_element_by_link_text(
                    "Victoria Fitness World").click()
                break
            except common.exceptions.NoSuchElementException as e:
                print(e)
                continue
            except common.exceptions.StaleElementReferenceException as e:
                print(e)
                continue
        else:
            raise Exception
        self.driver.find_element_by_xpath(self.xpaths["date_picker"]).click()

        if self.date.day <= 3: # if 3 days in the future is in a different month, we need to increment the calendar
            self.driver.find_element_by_css_selector("ui-icon-circle-triangle-e").click()
        for i in range(2):
            # same deal, stale reference issues, but they are only periodic
            try:
                self.driver.find_element_by_link_text(str(self.date.day)).click()
                WebDriverWait(driver=self.driver, timeout=10).until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                                                    f".selected-date "
                                                                                                    f".single-event"
                                                                                                    f":nth-child({self.timeslot}) "
                                                                                                    f".event-name")))
                sleep(3) # need this sleep because the website elements load before they are interactable
                self.driver.find_element_by_css_selector(f".selected-date .single-event:nth-child({self.timeslot})").click()
                break
            except common.exceptions.NoSuchElementException as e:
                print(e)
                continue
        else:
            raise Exception



    def book_appointment(self):
        WebDriverWait(driver=self.driver, timeout=10).until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                                            ".book-this-btn")))
        sleep(3)
        self.driver.find_element_by_css_selector(".book-this-btn").click()
        WebDriverWait(driver=self.driver, timeout=10).until(EC.presence_of_element_located((By.CSS_SELECTOR,"appttime")))
        self.driver.find_element_by_id("appttime").click()
        self.driver.find_element_by_css_selector("btn-primary").click()

def main():
    scheduler = Scheduler()
    scheduler.login()
    scheduler.find_appointment()
    scheduler.book_appointment()


if __name__ == ("__main__"):
    main()
