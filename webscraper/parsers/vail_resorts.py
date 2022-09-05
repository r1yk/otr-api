from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from webscraper import Parser, Rating


class Vail(Parser):
    lift_css_selector = ".liftStatus__lifts__row"
    trail_css_selector = ".trailStatus__trails__row"

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
        try:
            item.find_element(By.CSS_SELECTOR, "div.icon-status-open")
            return "Open"
        except:
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
