"""
Parsers for Killington + Pico Mountain
"""
import re
from typing import List, Optional

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement

from webscraper import Parser, Rating


class Killington(Parser):
    """
    Killington trail report parser
    """

    trail_type_to_rating: dict = {
        "difficulty-level-green": Rating.GREEN.value,
        "difficulty-level-blue": Rating.BLUE.value,
        "difficulty-level-black": Rating.BLACK.value,
        "difficulty-level-black-2": Rating.DOUBLE_BLACK.value,
    }

    red_x_color = "#D0021B"

    def __init__(self, browser):
        self._lifts_and_trails = None
        self._trail_rating_regex = re.compile(r"difficulty-level-([a-z]+)(-\d)?")
        super().__init__(browser)

    def get_lift_elements(self, _: Optional[WebElement] = None) -> List[WebElement]:
        return self.get_lifts_and_trails().get("lifts")

    def get_trail_elements(self, _: Optional[WebElement] = None) -> List[WebElement]:
        return self.get_lifts_and_trails().get("trails")

    def get_lifts_and_trails(self) -> List[WebElement]:
        """
        Killington lumps trails and lifts together and makes it tough to distinguish them :(

        This relies on trail elements having info about their difficulty, while lifts do not.
        """
        trail_elements = []
        lift_elements = []

        if self._lifts_and_trails is None:
            # Skip the first panel that's lifts-only
            table_panels = self.browser.find_elements(
                By.CSS_SELECTOR, "div.panel-body > table"
            )[1:]

            for table in table_panels:
                table_rows = table.find_elements(By.CSS_SELECTOR, "tbody > tr")
                for row in table_rows:
                    try:
                        row.find_element(By.CSS_SELECTOR, "td.difficulty")
                        trail_elements.append(row)
                    except NoSuchElementException:
                        lift_elements.append(row)

                self._lifts_and_trails = {
                    "lifts": lift_elements,
                    "trails": trail_elements,
                }

        return self._lifts_and_trails

    def get_lift_or_trail_name(self, lift_or_trail: WebElement) -> str:
        """Killington treats lifts + trails with identical CSS."""
        return (
            lift_or_trail.find_element(By.CLASS_NAME, "name")
            .get_attribute("textContent")
            .strip()
        )

    def get_lift_or_trail_status(self, lift_or_trail: WebElement) -> str:
        """
        Killington treats lifts + trails with identical CSS.

        This one is fucking tenuous. The only descriptors in the markup that seem to point
        to the status are the color (ok, fine) and shape (gross) of the SVG icon that's
        either a green check or a red X. If we see their red color, it's closed.
        """
        status = lift_or_trail.find_element(By.CSS_SELECTOR, "td.status")
        for svg_path in status.find_elements(By.TAG_NAME, "path"):
            if svg_path.get_attribute("fill") == self.red_x_color:
                return "Closed"

        return "Open"

    def get_lift_name(self, lift: WebElement) -> str:
        return self.get_lift_or_trail_name(lift)

    def get_lift_status(self, lift: WebElement) -> str:
        return self.get_lift_or_trail_status(lift)

    def get_trail_name(self, trail: WebElement) -> str:
        return self.get_lift_or_trail_name(trail)

    def get_trail_status(self, trail: WebElement) -> str:
        return self.get_lift_or_trail_status(trail)

    def get_trail_type(self, trail: WebElement) -> str:
        trail_css_classes = trail.find_element(
            By.CSS_SELECTOR, "td.difficulty > div"
        ).get_attribute("class")
        difficulty = self._trail_rating_regex.search(trail_css_classes)
        if difficulty:
            return difficulty[0]
        return None

    def get_trail_groomed(self, trail: WebElement) -> bool:
        try:
            trail.find_element(By.CSS_SELECTOR, "td.groomed > div")
            return True
        except NoSuchElementException:
            return False

    def get_trail_night_skiing(self, trail: WebElement) -> bool:
        return False
