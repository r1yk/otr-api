"""
Saskadena Six webscraper
"""
from typing import List, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from webscraper import Parser, Rating


class SaskadenaSix(Parser):
    """
    Parser for the Saskadena Six trail report
    """

    trail_type_to_rating: dict = {
        "Easy": Rating.GREEN.value,
        "Intermediate": Rating.BLUE.value,
        "Advanced": Rating.BLACK.value,
        "Expert": Rating.DOUBLE_BLACK.value,
    }

    def __init__(self, browser):
        self._lifts_and_trails = None
        super().__init__(browser)

    def get_lift_elements(self, _: Optional[WebElement] = None) -> List[WebElement]:
        return self.get_lifts_and_trails().get("lifts")

    def get_lift_name(self, lift: WebElement) -> str:
        name_element = lift.find_element(By.CLASS_NAME, "title")
        return name_element.text

    def get_lift_status(self, lift: WebElement) -> str:
        status_element = lift.find_element(By.CLASS_NAME, "field--name-field-status")
        return status_element.text

    def get_trail_elements(self, _: Optional[WebElement] = None) -> List[WebElement]:
        return self.get_lifts_and_trails().get("trails")

    def get_lifts_and_trails(self) -> List[WebElement]:
        """
        Saskadena Six lumps trails and lifts together and makes it tough to distinguish them :(
        """
        trail_elements = []
        lift_elements = []
        if self._lifts_and_trails is None:
            all_elements = self.browser.find_elements(
                By.CLASS_NAME, "node--type-lift-trail"
            )
            for element in all_elements:
                if Parser.element_has_child(element, ".level"):
                    trail_elements.append(element)
                else:
                    lift_elements.append(element)

            self._lifts_and_trails = {"lifts": lift_elements, "trails": trail_elements}

        return self._lifts_and_trails

    def get_trail_name(self, trail: WebElement) -> str:
        trail_name_element = trail.find_element(By.CLASS_NAME, "title")
        return trail_name_element.text

    def get_trail_status(self, trail: WebElement) -> str:
        trail_status_element = trail.find_element(
            By.CLASS_NAME, "field--name-field-status"
        )
        return trail_status_element.text

    def get_trail_type(self, trail: WebElement) -> str:
        trail_type_element = trail.find_element(By.CLASS_NAME, "level")
        return trail_type_element.text

    def get_trail_groomed(self, trail: WebElement) -> bool:
        return None

    def get_trail_night_skiing(self, trail: WebElement) -> bool:
        return False
