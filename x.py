#import requests,time and os
import requests
import time
import os
from selenium import webdriver
from twilio.rest import Client
from urllib.parse import urljoin
from collections import defaultdict

#SMS alert is triggered using settings
COUNTRIES = ["US", "Sweden"]
THRESHOLDS = [12, 1]
URL = "https://arcg.is/0fHmTX"
URL_MOBILE = "https://arcg.is/1DPOWm0"

def sms_alert(message):
    #print(message)
    client = Client(os.environ.get("TWILIO_SID"), os.environ.get("TWILIO_TOKEN"))
    client.messages.create(body = message, from_ =os.environ.get("TWILIO_NUMBER"),to = os.environ.get("PHONE_NUMBER"))
    time.sleep(2)


def footer_message(ts):
    return "For more info: {}\n{}".format(URL_MOBILE, ts)


def test_alert():
    countries_confirmed, ts = scrape_confirmed_countries()
    message = "{} has {} cases.\n{}".format(list(countries_confirmed.keys())[0], list(countries_confirmed.values())[0],footer_message(ts))
    #print(message)
    sms_alert(message)


def confirmed_data(driver):
    confirmed_cases_results = driver.find_elements_by_xpath("//*[@id='ember32']")
    countries_confirmed = defaultdict(int)

    for confirmed in confirmed_cases_results:
        countries = confirmed.find_elements_by_class_name("external-html")

        for country in countries:
            country_attr = country.text.split(" ", 1)
            countries_confirmed[country_attr[1]] = int(country_attr[0].replace(",", ""))

    return countries_confirmed


def ts_data(driver):
    # Get last updated time
    last_updated_results = driver.find_element_by_xpath("//*[@id='ember46']/div")
    return last_updated_results.text


def scrape_confirmed_countries():  
    # Request Web Page
    driver = webdriver.Chrome()
    driver.get(URL)
    time.sleep(5)
    # Call Helper functions to scrape data
    countries_confirmed =confirmed_data(driver)
    ts = ts_data(driver)
    driver.quit()
    return countries_confirmed, ts


def get_alert_message(country, confirmed, ts):
    footer = footer_message(ts)
    return "Alert Triggered!\n{} has {} confirmed cases.\n{}".format(country, confirmed, footer)


def check_status():    
    countries_confirmed, ts = scrape_confirmed_countries()

    for country, threshold in zip(COUNTRIES, THRESHOLDS):

        if countries_confirmed[country] >= threshold:
            print("{} triggered an alert!".format(country))
            sms_alert(get_alert_message(country, countries_confirmed[country], ts))

        else:
            print("{} didn't trigger an alert.".format(country))


if __name__ == '__main__':
    check_status()
