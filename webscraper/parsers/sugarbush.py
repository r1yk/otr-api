# pylint: disable=broad-except
"""
Webscraper for Sugarbush Resort
"""
from typing import List

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from webscraper import Parser, Rating


class Sugarbush(Parser):
    """
    Parser for the Sugarbush Resort trail report.
    """

    lift_css_selector = "ul.Lifts_list__3PwcO > li"
    trail_css_selector = "ul.Trails_trailsList__3gYwp > li"

    trail_type_to_rating: dict = {
        "Easiest": Rating.GREEN.value,
        "More Difficult": Rating.BLUE.value,
        "Very Difficult": Rating.BLACK.value,
        "Expert": Rating.DOUBLE_BLACK.value,
        "Wooded Area": Rating.WOODED.value,
    }

    def get_lift_name(self, lift: WebElement) -> str:
        return lift.find_element(By.CSS_SELECTOR, "h3.Lifts_name__1YvQ1").text

    def get_lift_status(self, lift: WebElement) -> str:
        return lift.find_element(By.CSS_SELECTOR, "p.Lifts_status__z9n5V").text

    def get_trail_name(self, trail: WebElement) -> str:
        return trail.find_element(
            By.CSS_SELECTOR, "dd > h4.Trails_trailName__1_oua"
        ).text

    def get_trail_status(self, trail: WebElement) -> str:
        return trail.find_element(
            By.CSS_SELECTOR, "dd > p.Trails_trailStatus__jJDvi"
        ).text

    def get_trail_type(self, trail: WebElement) -> str:
        return trail.find_element(
            By.CSS_SELECTOR, "div.Trails_trailDetailDifficulty__2n1p- > dd > span"
        ).text

    def get_trail_groomed(self, trail: WebElement) -> bool:
        try:
            trail_features: List[WebElement] = trail.find_elements(
                By.CSS_SELECTOR, "ul.Trails_trailFeatures__2pFdC > li"
            )
            for feature in trail_features:
                if feature.text == "Grooming":
                    return True
            return False
        except Exception as _:
            return False

    def get_trail_night_skiing(self, trail: WebElement) -> bool:
        return False
