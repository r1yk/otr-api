"""
Webscraper for Smugglers' Notch Resort
"""
import re
from typing import List, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException

from webscraper import Parser, Rating
from lib.util import get_inch_range_from_string


class Smuggs(Parser):
    """
    Parser for the Smugglers' Notch trail report.
    """

    snow_report_css_selector = "div#summary-area"

    trail_type_to_rating: dict = {
        "easier": Rating.GREEN.value,
        "more-difficult": Rating.BLUE.value,
        "most-difficult": Rating.BLACK.value,
        "expert-only": Rating.DOUBLE_BLACK.value,
        "extreme-expert": Rating.TRIPLE_BLACK.value,
        "terrain": Rating.TERRAIN_PARK.value,
    }

    report_sections = ["sterling-report", "madonna-report", "morse-report"]

    def __init__(self, browser):
        self._lifts_and_trails = None
        super().__init__(browser)

    def get_lift_elements(self, _: Optional[WebElement] = None) -> List[WebElement]:
        return self.get_lifts_and_trails().get("lifts")

    def get_trail_elements(self, _: Optional[WebElement] = None) -> List[WebElement]:
        return self.get_lifts_and_trails().get("trails")

    def get_lifts_and_trails(self) -> List[WebElement]:
        """
        Smuggs lumps trails and lifts together and makes it tough to distinguish them :(

        This relies on their naming convention where lifts end in " Lift".
        """
        trail_elements = []
        lift_elements = []
        lift_regex = re.compile(r".+\bLift$")

        if self._lifts_and_trails is None:
            for section in self.report_sections:
                report = self.browser.find_element(By.ID, section)
                report_items = report.find_elements(By.CLASS_NAME, "report")
                for item in report_items:
                    item_name = item.text.strip()
                    if lift_regex.match(item_name):
                        lift_elements.append(item)
                    else:
                        trail_elements.append(item)

            self._lifts_and_trails = {"lifts": lift_elements, "trails": trail_elements}

        return self._lifts_and_trails

    def get_lift_name(self, lift: WebElement) -> str:
        return lift.text.strip()

    def get_lift_status(self, lift: WebElement) -> str:
        try:
            if lift.find_element(By.CLASS_NAME, "closed"):
                return "Closed"
        except NoSuchElementException:
            return "Open"

        return None

    def get_trail_name(self, trail: WebElement) -> str:
        return trail.text.strip()

    def get_trail_status(self, trail: WebElement) -> str:
        try:
            if trail.find_element(By.CLASS_NAME, "closed"):
                return "Closed"
        except NoSuchElementException:
            return "Open"

        return None

    def get_trail_type(self, trail: WebElement) -> str:
        for trail_type in self.trail_type_to_rating:
            try:
                if trail.find_element(By.CLASS_NAME, trail_type):
                    return trail_type
            except NoSuchElementException:
                continue

        return None

    def get_trail_groomed(self, trail: WebElement) -> bool:
        try:
            if trail.find_element(By.CLASS_NAME, "groomed-now"):
                return True
        except NoSuchElementException:
            return False

        return None

    def get_trail_night_skiing(self, trail: WebElement) -> bool:
        return False

    def get_base_layer(self, snow_report: WebElement) -> dict:
        base_layer_element = snow_report.find_element(
            By.CSS_SELECTOR, "div#base-summary > p:nth-of-type(2) > b"
        )
        return get_inch_range_from_string(base_layer_element.text)

    def get_season_snow(self, snow_report: WebElement) -> dict:
        season_snow_element = snow_report.find_element(
            By.CSS_SELECTOR, "div#base-summary > p:nth-of-type(4) > b"
        )
        return get_inch_range_from_string(season_snow_element.text)
