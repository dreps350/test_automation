import re
import time
import argparse

from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException


class CareersFilter:

    def __init__(self, driver):
        self.driver = driver
        self.url = "https://careers.veeam.com/"
        self.driver.get(self.url)

    def select_country(self, country):
        self._select_from_scroller("country", country)

    def select_language(self, language):
        lang_codes = {
            "not required": "ch-0",
            "english": "ch-7",
            "german": "ch-11",
            "russian": "ch-22",
        }
        self._select_from_checkbox("language", lang_codes[language.lower()])

    def _select_from_scroller(self, scroller_name, value):
        scroller_id = f"{scroller_name}-element"
        scroller_relative_xpath = f"//dd[@id='{scroller_id}']"
        item_relative_xpath = f"//span[@data-value='{value}']"

        self._select_item(scroller_id, scroller_relative_xpath + item_relative_xpath)

    def _select_from_checkbox(self, checkbox_name, value):
        checkbox_relative_xpath = f"//div[@id='{checkbox_name}']"
        item_relative_xpath = f"//label[@for='{value}']"
        apply_button_xpath = "//a[@class='selecter-fieldset-submit']"

        # object, that will be hidden when "Apply" button is clicked
        hidden_xpath = f"{checkbox_relative_xpath}/div[contains(@class, 'selecter-options scroller')]"

        self._select_item(checkbox_name, checkbox_relative_xpath + item_relative_xpath)

        # submit selection
        try:
            self.driver.find_element_by_xpath(checkbox_relative_xpath + apply_button_xpath).click()
            WebDriverWait(self.driver, 10).until(EC.invisibility_of_element((By.XPATH, hidden_xpath)))
        except NoSuchElementException as e:
            print(e)

    def _select_item(self, container_name, item_path):
        try:
            self.driver.find_element_by_id(container_name).click()
            self.driver.find_element_by_xpath(item_path).click()
        except NoSuchElementException as e:
            print(e)


def count_vacancies(driver, expected_vac_n=None):
    time.sleep(1)  # vacancies animation delay is not captured by WebDriverWait
    try:
        show_all_xpath = "//*[a='Show all jobs']/a"
        driver.find_element_by_xpath(show_all_xpath).click()
        # wait until page is updated
        WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.XPATH, "//*[a='Show all jobs']/a")))
    except NoSuchElementException as e:
        print("'Show all jobs' button was not found")
    except ElementNotInteractableException as e:
        print("'Show all jobs' button is not clickable")

    vacancies = driver.find_elements_by_xpath("//div[contains(@class, 'vacancies-blocks-col')]")
    counted_vac_n = len(vacancies)

    if expected_vac_n is None:
        jobs_header = driver.find_element_by_xpath("//div[contains(@class, 'row vacancies-blocks')]//h3").text
        expected_vac_n = re.findall(r"([\d]+)", jobs_header)[0]

    if counted_vac_n != int(expected_vac_n):
        print(f"Unexpected number of vacancies found:\ncounted {counted_vac_n}\nexpected {expected_vac_n}")

    return counted_vac_n


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""Returns number or vacancies found on 'https://careers.veeam.com/' 
                                                    \naccording to passed filter arguments.""")
    parser.add_argument("country", help="Country filter.")
    parser.add_argument("language", help="Language filter.")
    parser.add_argument("-e", "--expected", default=None, help="""Expected number of vacancies to compare. 
                                                                \nNumber found on web page is used by default.""")
    args = parser.parse_args()

    driver = Firefox()
    driver.fullscreen_window()

    cf = CareersFilter(driver)

    cf.select_country(args.country)
    cf.select_language(args.language)

    print(count_vacancies(driver, args.expected))
