# pylint: disable=broad-except
"""
This module contains the base Parser class that is inherited by custom parsers.
"""


from typing import List

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait


from lib.models import Lift, Trail


class Parser:
    """
    Base class that is inherited by each custom trail report parser.
    """

    lift_css_selector = None
    trail_css_selector = None
    snow_report_css_selector = None
    trail_type_to_rating: dict = {}

    def __init__(self, browser: WebDriver):
        self.browser = browser

    def display_trails(self) -> None:
        """Take any action needed to render trails in the DOM (like opening a "trails" panel
        or something)."""

    def display_lifts(self) -> None:
        """Take any action needed to render lifts in the DOM (like opening a "lifts" panel
        or something)."""

    @classmethod
    def element_has_child(cls, element: WebElement, css_selector: str) -> bool:
        """Return `true` if a there is a match for a given `css_selector`
        within a given web element."""
        try:
            element.find_element(By.CSS_SELECTOR, css_selector)
            return True
        except Exception as _:
            return False

    def get_lift_elements(self) -> List[WebElement]:
        """Get the HTML elements containing all lift information."""
        elements = WebDriverWait(self.browser, timeout=10).until(
            lambda browser: browser.find_elements(
                By.CSS_SELECTOR, self.lift_css_selector
            )
        )
        print(f"{len(elements)} lifts")
        return elements

    def get_lift_name(self, lift: WebElement) -> str:
        """Find the name of this lift within the HTML element."""

    def get_lift_status(self, lift: WebElement) -> str:
        """Find the status of this lift within the HTML element."""

    def get_lifts(self) -> List["Lift"]:
        """Return `Lift` instances for each web element representing a lift."""
        self.display_lifts()
        lifts = []
        for lift_element in self.get_lift_elements():
            lift = Lift(
                name=self.get_lift_name(lift_element),
                unique_name=self.get_lift_name(lift_element),
                status=self.get_lift_status(lift_element),
            )
            lift.is_open = lift.status.lower() == "open"
            lifts.append(lift)
        return lifts

    def get_trail_elements(self) -> List[WebElement]:
        """Return all web elements containing information about individual trails."""
        elements = WebDriverWait(self.browser, timeout=10).until(
            lambda browser: browser.find_elements(
                By.CSS_SELECTOR, self.trail_css_selector
            )
        )
        print(f"{len(elements)} trails")
        return elements

    def get_trails(self) -> List["Trail"]:
        "Return `Trail` instances for each web element representing a trail."
        self.display_trails()
        trails = []
        for trail_element in self.get_trail_elements():
            trail = Trail(
                name=self.get_trail_name(trail_element),
                trail_type=self.get_trail_type(trail_element),
                status=self.get_trail_status(trail_element).lower(),
                groomed=self.get_trail_groomed(trail_element),
                night_skiing=self.get_trail_night_skiing(trail_element),
                rating=self.get_trail_rating(trail_element),
            )
            trail.is_open = trail.status.lower() == "open"
            trails.append(trail)
        return trails

    def get_trail_name(self, trail: WebElement) -> str:
        """Find the name of this trail within the HTML element."""

    def get_trail_type(self, trail: WebElement) -> str:
        """Return either the difficulty or classification (i.e. "Terrain park" of this trail."""

    def get_trail_status(self, trail: WebElement) -> str:
        """
        Find the status of this trail within the HTML element
        (i.e. open, closed, partially open).
        """

    def get_trail_groomed(self, trail: WebElement) -> bool:
        """Return whether or not this trail has groomed snow."""

    def get_trail_night_skiing(self, trail: WebElement) -> bool:
        """Return whether or not this trail has lighting for skiing after dark."""

    def get_trail_rating(self, trail: WebElement) -> int:
        """
        Get the trail type as described by the resort, and return the
        corresponding normalized `Rating` value.
        """
        trail_type = self.get_trail_type(  # pylint: disable=assignment-from-no-return
            trail
        )

        if trail_type:
            return self.trail_type_to_rating.get(trail_type)
        return None

    def parse_snow_report(self) -> dict:
        """
        Get the WebElement containing the snow report, and mine it for any data
        that can be found + returned as a dict.
        """
        snow_report = self.get_snow_report_element()
        return {
            "baseLayer": self.get_base_layer(snow_report),
            "recentSnow": self.get_recent_snow(snow_report),
            "seasonSnow": self.get_season_snow(snow_report),
        }

    def get_snow_report_element(self) -> WebElement:
        """Get the HTML element that contains all snow information."""
        element = WebDriverWait(self.browser, timeout=10).until(
            lambda browser: browser.find_element(
                By.CSS_SELECTOR, self.snow_report_css_selector
            )
        )
        return element

    def get_base_layer(self, snow_report: WebElement) -> dict:
        """Return key-value pairs for everything that can be gleaned about the base depth."""

    def get_recent_snow(self, snow_report: WebElement) -> dict:
        """Return key-value pairs that describe everything that can be gleaned
        about recent snow accumulation in the report."""

    def get_season_snow(self, snow_report: WebElement) -> dict:
        """Return key-value pairs that describe everything that can be gleaned
        about total snow accumulation in the report."""
