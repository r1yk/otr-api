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
from lib.util import get_inch_range_from_string


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

    snow_report_css_selector = "div.SnowReport-Tab-pane:nth-of-type(3)"

    trail_type_to_rating: dict = {
        "EASIER": Rating.GREEN.value,
        "MODERATE": Rating.BLUE.value,
        "ADVANCED": Rating.BLACK.value,
        "EXTREMELY DIFFICULT": Rating.DOUBLE_BLACK.value,
        "TERRAIN PARK": Rating.TERRAIN_PARK.value,
    }

    def get_base_layer(self, snow_report: WebElement) -> dict:
        print(snow_report.get_attribute("id"))
        base_depth_range = snow_report.find_elements(
            By.CSS_SELECTOR, "div.SnowConditions > dl > dd"
        )[0].text
        return get_inch_range_from_string(base_depth_range)

    def get_recent_snow(self, snow_report: WebElement) -> dict:
        recent_snow_elements = snow_report.find_elements(
            By.CSS_SELECTOR, "section.snowfall > div > dl"
        )[0:2]
        (last_24_hours, last_7_days) = (
            recent_snow_elements[0],
            recent_snow_elements[1],
        )
        return {
            24: get_inch_range_from_string(
                last_24_hours.find_element(By.TAG_NAME, "dd").text
            ),
            (24 * 7): get_inch_range_from_string(
                last_7_days.find_element(By.TAG_NAME, "dd").text
            ),
        }

    def get_season_snow(self, snow_report: WebElement) -> dict:
        season_snow_element = snow_report.find_elements(
            By.CSS_SELECTOR, "section.snowfall > div > dl"
        )[-1]
        return get_inch_range_from_string(
            season_snow_element.find_element(By.TAG_NAME, "dd").text
        )


class JayPeak(SnowReportCSS):
    """
    Parser for the Jay Peak trail report
    """

    snow_report_css_selector = "div#snow-cond"

    trail_type_to_rating: dict = {
        "BEGINNER": Rating.GREEN.value,
        "INTERMEDIATE": Rating.BLUE.value,
        "ADVANCED": Rating.BLACK.value,
        "TERRAIN PARK": Rating.TERRAIN_PARK.value,
        "INTERMEDIATE GLADE": Rating.GLADES.value,
        "ADVANCED GLADE": Rating.DOUBLE_GLADES.value,
    }

    def get_base_layer(self, snow_report: WebElement) -> dict:
        conditions_container = snow_report.find_elements(
            By.CSS_SELECTOR,
            "section.SnowReport-first",
        )[1]
        base_depth_range = conditions_container.find_elements(
            By.CSS_SELECTOR, "div.SnowReport-measures--columns > dl > dd"
        )[0].text
        return get_inch_range_from_string(base_depth_range)

    def get_recent_snow(self, snow_report: WebElement) -> dict:
        recent_snow_elements = snow_report.find_elements(
            By.CSS_SELECTOR,
            "section.SnowReport-section--measurements > div.SnowReport-snowfall > dl",
        )[0:3]
        (last_24_hours, last_48_hours, last_7_days) = (
            recent_snow_elements[0],
            recent_snow_elements[1],
            recent_snow_elements[2],
        )
        return {
            24: get_inch_range_from_string(
                last_24_hours.find_element(By.TAG_NAME, "dd").text
            ),
            48: get_inch_range_from_string(
                last_48_hours.find_element(By.TAG_NAME, "dd").text
            ),
            (24 * 7): get_inch_range_from_string(
                last_7_days.find_element(By.TAG_NAME, "dd").text
            ),
        }

    def get_season_snow(self, snow_report: WebElement) -> dict:
        season_snow_element = snow_report.find_elements(
            By.CSS_SELECTOR,
            "section.SnowReport-section--measurements > div.SnowReport-snowfall > dl",
        )[-1]
        return get_inch_range_from_string(
            season_snow_element.find_element(By.TAG_NAME, "dd").text
        )
