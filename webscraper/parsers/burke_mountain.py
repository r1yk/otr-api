"""
Burke Mountain webscraper
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from webscraper import Parser, Rating
from lib.util import get_inch_range_from_string


class BurkeMountain(Parser):
    """
    Parser for the Burke Mountain trail report
    """

    lift_css_selector = "div#lifts > table > tbody > tr"
    trail_css_selector = "div#trails > table > tbody > tr"
    snow_report_css_selector = "div#snow"

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
        return status.get_attribute("class")

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

    def get_snow_report_metric(self, metric_element: WebElement) -> dict:
        """
        Burke allows various snow condition statistics to be parsed similarly.
        """
        return get_inch_range_from_string(
            metric_element.find_element(By.CSS_SELECTOR, "div.value").text
        )

    def get_recent_snow(self, snow_report: WebElement) -> dict:
        """Return key-value pairs that describe everything that can be gleaned
        about recent snow accumulation in the report."""
        last_24_element = snow_report.find_element(
            By.CSS_SELECTOR, "div.tallys > div.grid:nth-of-type(1)"
        )
        last_48_element = snow_report.find_element(
            By.CSS_SELECTOR, "div.tallys > div.grid:nth-of-type(2)"
        )
        last_7_days_element = snow_report.find_element(
            By.CSS_SELECTOR, "div.tallys > div.grid:nth-of-type(3)"
        )

        return {
            24: self.get_snow_report_metric(last_24_element),
            48: self.get_snow_report_metric(last_48_element),
            (24 * 7): self.get_snow_report_metric(last_7_days_element),
        }

    def get_base_layer(self, snow_report: WebElement) -> dict:
        base_layer_element = snow_report.find_element(
            By.CSS_SELECTOR, "div.tallys > div.grid:nth-of-type(4)"
        )
        return self.get_snow_report_metric(base_layer_element)

    def get_season_snow(self, snow_report: WebElement) -> dict:
        season_snow_element = snow_report.find_element(
            By.CSS_SELECTOR, "div.tallys > div.grid:nth-of-type(5)"
        )
        return self.get_snow_report_metric(season_snow_element)
