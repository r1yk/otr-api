"""
Bromley webscraper
"""
import re

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from webscraper import Parser, Rating
from lib.util import get_inch_range_from_string


class Bromley(Parser):
    """
    Parser for the Bromley trail report
    """

    lift_css_selector = "div#lifts > div.lift-status-section > div.lift-status-info"
    trail_css_selector = "div#trails > div.lift-status-section > div.lift-status-info"
    snow_report_css_selector = "div.report-container"
    trail_type_to_rating: dict = {
        "Easiest": Rating.GREEN.value,
        "More Difficult": Rating.BLUE.value,
        "Most Difficult": Rating.BLACK.value,
        "Extremely Difficult": Rating.DOUBLE_BLACK.value,
    }

    def display_lifts(self):
        tabs = self.browser.find_elements(By.CLASS_NAME, "tab-box")
        tabs[0].click()

    def display_trails(self):
        tabs = self.browser.find_elements(By.CLASS_NAME, "tab-box")
        tabs[1].click()

    def get_lift_or_trail_status(self, lift_or_trail: WebElement) -> str:
        """Bromley treats lifts + trails with identical CSS."""
        try:
            lift_or_trail.find_element(By.CSS_SELECTOR, "svg.icon_snowreport_open")
            return "Open"
        except NoSuchElementException:
            return "Closed"

    def get_lift_name(self, lift: WebElement) -> str:
        return lift.find_element(By.CLASS_NAME, "lift-name").text.strip()

    def get_lift_status(self, lift: WebElement) -> str:
        return self.get_lift_or_trail_status(lift)

    def get_trail_name(self, trail: WebElement) -> str:
        return trail.find_element(By.CLASS_NAME, "trail-name").text.strip()

    def get_trail_type(self, trail: WebElement) -> str:
        """
        Navigate up to the report sections, and then find the most recently seen
        title for a difficulty.
        """
        current_difficulty_section: WebElement = trail.find_element(
            By.XPATH, "ancestor::div[@class='lift-status-section']"
        )
        difficulty_info = current_difficulty_section.find_elements(
            By.XPATH, "preceding-sibling::div[@class='difficulty-info']"
        )[-1]
        difficulty = difficulty_info.find_element(
            By.CLASS_NAME, "difficulty-level-title"
        )
        return difficulty.text

    def get_trail_status(self, trail: WebElement) -> str:
        return self.get_lift_or_trail_status(trail)

    def get_trail_groomed(self, trail: WebElement) -> bool:
        return False

    def get_trail_night_skiing(self, trail: WebElement) -> bool:
        return False

    def get_base_layer(self, snow_report: WebElement) -> dict:
        base_depth_element = snow_report.find_element(
            By.CSS_SELECTOR, "div > div.col-12:nth-child(4)"
        )
        base_depth = base_depth_element.find_element(By.TAG_NAME, "h1").text
        return get_inch_range_from_string(base_depth)

    def get_recent_snow(self, snow_report: WebElement) -> dict:
        parenthentical_regex = re.compile(r"\(.+\)")
        last_24_hours = (
            snow_report.find_element(By.CSS_SELECTOR, "div > div.col-12:nth-child(5)")
            .find_element(By.TAG_NAME, "h1")
            .text
        )
        cleaned = parenthentical_regex.sub("", last_24_hours)
        return {24: get_inch_range_from_string(cleaned)}

    def get_season_snow(self, snow_report: WebElement) -> dict:
        season_snow = snow_report.find_element(
            By.CSS_SELECTOR, "div > div.col-12:nth-child(6)"
        )
        return get_inch_range_from_string(
            season_snow.find_element(By.TAG_NAME, "h1").text
        )
