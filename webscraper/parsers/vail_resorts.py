"""
Webscraper for various Vail Resorts mountains, like:
    Okemo
    Mt. Snow
    Stowe
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from webscraper import Parser, Rating
from lib.util import get_inch_range_from_string


class Vail(Parser):
    """
    Parser for all known Vail Resorts trail reports so far.
    """

    lift_css_selector = ".liftStatus__lifts__row"
    trail_css_selector = ".trailStatus__trails__row"
    snow_report_css_selector = "div.snow_report__content"

    trail_type_to_rating: dict = {
        "beginner": Rating.GREEN.value,
        "intermediate": Rating.BLUE.value,
        "mostdifficult": Rating.BLACK.value,
        "expert": Rating.DOUBLE_BLACK.value,
        "terrainpark": Rating.TERRAIN_PARK.value,
    }

    def get_lift_name(self, lift: WebElement) -> str:
        name_element: WebElement = lift.find_element(
            By.CSS_SELECTOR, "span.liftStatus__lifts__row__title"
        )
        return name_element.text

    def get_item_status(self, item: WebElement) -> str:
        """
        See if this item is open, or else return "Closed".
        """
        try:
            item.find_element(By.CSS_SELECTOR, "div.icon-status-open")
            return "Open"
        except Exception as _:  # pylint: disable=broad-except
            return "Closed"

    def get_lift_status(self, lift: WebElement) -> str:
        return self.get_item_status(lift)

    def get_trail_status(self, trail: WebElement) -> str:
        return self.get_item_status(trail)

    def get_trail_name(self, trail: WebElement) -> str:
        name_element: WebElement = trail.find_element(
            By.CLASS_NAME, "trailStatus__trails__row--name"
        )
        return name_element.get_attribute("innerText")

    def get_trail_type(self, trail: WebElement) -> str:
        trail_types = [
            "beginner",
            "intermediate",
            "mostdifficult",
            "expert",
            "terrainpark",
        ]
        # Trail difficulty is the 2nd icon in the row.
        trail_icon: WebElement = trail.find_element(
            By.CSS_SELECTOR, "div.trailStatus__trails__row--icon:nth-of-type(2)"
        )
        icon_class = trail_icon.get_attribute("class")
        for trail_type in trail_types:
            if icon_class.find(trail_type) != -1:
                return trail_type

        raise RuntimeError("Trail type not found")

    def get_trail_groomed(self, trail: WebElement) -> bool:
        return Parser.element_has_child(trail, "div.icon-status-snowcat")

    def get_trail_night_skiing(self, trail: WebElement) -> bool:
        return False

    def get_snow_report_metric(self, metric_element: WebElement) -> dict:
        """
        Vail allows various snow condition statistics to be parsed similarly.
        """
        metric_text = metric_element.find_element(
            By.CLASS_NAME, "snow_report__metrics__measurement"
        ).text
        return get_inch_range_from_string(metric_text)

    def get_recent_snow(self, snow_report: WebElement) -> dict:
        last_24_element = snow_report.find_element(
            By.CSS_SELECTOR, "ul > li:nth-of-type(2)"
        )
        last_48_element = snow_report.find_element(
            By.CSS_SELECTOR, "ul > li:nth-of-type(3)"
        )
        last_7_days_element = snow_report.find_element(
            By.CSS_SELECTOR, "ul > li:nth-of-type(4)"
        )
        return {
            24: self.get_snow_report_metric(last_24_element),
            48: self.get_snow_report_metric(last_48_element),
            (24 * 7): self.get_snow_report_metric(last_7_days_element),
        }

    def get_base_layer(self, snow_report: WebElement) -> dict:
        base_layer_element = snow_report.find_element(
            By.CSS_SELECTOR, "ul > li:nth-of-type(5)"
        )
        return self.get_snow_report_metric(base_layer_element)

    def get_season_snow(self, snow_report: WebElement) -> dict:
        season_snow_element = snow_report.find_element(
            By.CSS_SELECTOR, "ul > li:nth-of-type(6)"
        )
        return self.get_snow_report_metric(season_snow_element)
