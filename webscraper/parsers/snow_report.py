"""
Webscraper for a common UI setup shared by a few mountains, like:
    Bolton Valley
    Jay Peak
    possibly others?
"""
from typing import List

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from webscraper import Parser, Rating


class SnowReportCSS(Parser):
    """A common UI setup that seems to be shared by quite a few mountains."""

    lift_css_selector = "article.SnowReport-Lift.SnowReport-feature"
    trail_css_selector = "article.SnowReport-Trail.SnowReport-feature"

    def get_lift_name(self, lift: WebElement) -> str:
        lift_name_element = lift.find_element(By.CLASS_NAME, "SnowReport-feature-title")
        return lift_name_element.text

    def get_lift_status(self, lift: WebElement) -> List[dict]:
        lift_status_element: WebElement = lift.find_element(
            By.CLASS_NAME, "SnowReport-item-status"
        )
        return lift_status_element.find_element(
            By.CLASS_NAME, "SnowReport-sr-label"
        ).text

    def get_trail_name(self, trail: WebElement) -> str:
        trail_name_element = trail.find_element(
            By.CLASS_NAME, "SnowReport-feature-title"
        )
        return trail_name_element.text

    def get_trail_status(self, trail: WebElement) -> str:
        trail_status_icon: WebElement = trail.find_element(
            By.CLASS_NAME, "SnowReport-item-status"
        )
        trail_status: WebElement = trail_status_icon.find_element(By.TAG_NAME, "span")
        return trail_status.text

    def get_trail_type(self, trail: WebElement) -> str:
        parent: WebElement = trail.find_element(By.XPATH, "ancestor::section")
        header: WebElement = parent.find_element(By.TAG_NAME, "h2")
        return header.text

    def get_trail_groomed(self, trail: WebElement) -> bool:
        return Parser.element_has_child(trail, ".pti-groomed")

    def get_trail_night_skiing(self, trail: WebElement) -> bool:
        return Parser.element_has_child(trail, ".pti-moon-mining")


class BoltonValley(SnowReportCSS):
    """
    Parser for the Bolton Valley trail report
    """

    trail_type_to_rating: dict = {
        "EASIER": Rating.GREEN.value,
        "MODERATE": Rating.BLUE.value,
        "ADVANCED": Rating.BLACK.value,
        "EXTREMELY DIFFICULT": Rating.DOUBLE_BLACK.value,
        "TERRAIN PARK": Rating.TERRAIN_PARK.value,
    }


class JayPeak(SnowReportCSS):
    """
    Parser for the Jay Peak trail report
    """

    trail_type_to_rating: dict = {
        "BEGINNER": Rating.GREEN.value,
        "INTERMEDIATE": Rating.BLUE.value,
        "ADVANCED": Rating.BLACK.value,
        "TERRAIN PARK": Rating.TERRAIN_PARK.value,
        "INTERMEDIATE GLADE": Rating.GLADES.value,
        "ADVANCED GLADE": Rating.DOUBLE_GLADES.value,
    }


class BurkeMountain(Parser):
    """
    Parser for the Burke Mountain trail report
    """

    lift_css_selector = "div#lifts > table > tbody > tr"
    trail_css_selector = "div#trails > table > tbody >tr"

    trail_type_to_rating: dict = {
        "level-1": Rating.GREEN.value,
        "level-2": Rating.BLUE.value,
        "level-3": Rating.BLACK.value,
        "level-4": Rating.DOUBLE_BLACK.value,
    }

    def get_lift_name(self, lift: WebElement) -> str:
        return lift.find_element(By.CSS_SELECTOR, 'td[data-label="Lift Name"]').text

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
        return type_element.get_attribute("class")

    def get_trail_status(self, trail: WebElement) -> str:
        return trail.find_element(
            By.CSS_SELECTOR, 'td[data-label="Status"] > span'
        ).get_attribute("class")

    def get_trail_groomed(self, trail: WebElement) -> bool:
        return (
            trail.find_element(
                By.CSS_SELECTOR, 'td[data-label="Groomed"] > span'
            ).get_attribute("class")
            == "open"
        )

    def get_trail_night_skiing(self, trail: WebElement) -> bool:
        return False
