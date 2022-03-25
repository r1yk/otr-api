from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from webscraper import Parser, Rating


class BurkeMountain(Parser):
    lift_css_selector = 'div#lifts > table > tbody > tr'
    trail_css_selector = 'div#trails > table > tbody > tr'

    trail_type_to_rating: dict = {
        'level-1': Rating.GREEN.value,
        'level-2': Rating.BLUE.value,
        'level-3': Rating.BLACK.value,
        'level-4': Rating.DOUBLE_BLACK.value
    }

    def get_lift_name(self, lift: WebElement) -> str:
        return lift.find_element(
            By.CSS_SELECTOR, 'td[data-label="Lift Name"]'
        ).text

    def get_lift_status(self, lift: WebElement) -> str:
        status: WebElement = lift.find_element(
            By.CSS_SELECTOR, 'td[data-label="Status"] > span'
        )
        return status.text

    def get_trail_name(self, trail: WebElement) -> str:
        return trail.find_element(
            By.CSS_SELECTOR, 'td[data-label="Trail Name"] > div.label'
        ).text

    def get_trail_type(self, trail: WebElement) -> str:
        type_element: WebElement = trail.find_element(
            By.CSS_SELECTOR, 'td[data-label="Trail Name"] > div.label > span'
        )
        return type_element.get_attribute('class')

    def get_trail_status(self, trail: WebElement) -> str:
        return trail.find_element(
            By.CSS_SELECTOR, 'td[data-label="Status"] > span'
        ).get_attribute('class')

    def get_trail_groomed(self, trail: WebElement) -> bool:
        return trail.find_element(
            By.CSS_SELECTOR, 'td[data-label="Groomed"] > span'
        ).get_attribute('class') == 'open'

    def get_trail_night_skiing(self, trail: WebElement) -> bool:
        return False
