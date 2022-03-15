import json
from typing import List, Optional
from ski_resort import Resort, SnowReport
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


class BoltonValley(SnowReport):
    _snow_report_url = 'https://snow.boltonvalley.com/snow-report/snow/snow-report/'


class JayPeak(SnowReport):
    _snow_report_url = 'https://digital.jaypeakresort.com/conditions/snow-report/snow-report/'


class SuicideSix(Resort):
    _trails_grouped_by_section = False
    _snow_report_url = 'https://www.suicide6.com/the-mountain/conditions'

    _lifts_and_trails: dict

    def __init__(self):
        self._lifts_and_trails = None
        super().__init__()

    def get_lift_elements(self, peak: Optional[WebElement] = None) -> List[WebElement]:
        return self.get_lifts_and_trails().get('lifts')

    def get_lift_name(self, lift: WebElement) -> str:
        name_element = lift.find_element(
            by=By.CLASS_NAME, value='title'
        )
        return name_element.text

    def get_lift_status(self, lift: WebElement) -> str:
        status_element = lift.find_element(
            by=By.CLASS_NAME, value='field--name-field-status'
        )
        return status_element.text

    def get_trail_elements(self, trail_section: Optional[WebElement] = None) -> List[WebElement]:
        return self.get_lifts_and_trails().get('trails')

    def get_lifts_and_trails(self) -> List[WebElement]:
        # Suicide Six lumps trails and lifts together and makes it tough to distinguish them :(
        trail_elements = []
        lift_elements = []
        if self._lifts_and_trails is None:
            all_elements = self.browser.find_elements(
                by=By.CLASS_NAME, value='node--type-lift-trail'
            )
            for element in all_elements:
                # If the element has a child with class "level", it's a trail. Otherwise it's a lift.
                try:
                    element.find_element(by=By.CLASS_NAME, value='level')
                    trail_elements.append(element)
                except:
                    lift_elements.append(element)

            self._lifts_and_trails = {
                'lifts': lift_elements,
                'trails': trail_elements
            }

        return self._lifts_and_trails

    def get_trail_name(self, trail: WebElement) -> str:
        trail_name_element = trail.find_element(
            by=By.CLASS_NAME, value='title'
        )
        return trail_name_element.text

    def get_trail_status(self, trail: WebElement) -> str:
        trail_status_element = trail.find_element(
            by=By.CLASS_NAME, value='field--name-field-status'
        )
        return trail_status_element.text

    def get_trail_type(self, trail: WebElement) -> str:
        trail_type_element = trail.find_element(
            by=By.CLASS_NAME, value='level'
        )
        return trail_type_element.text

    def get_trail_groomed(self, trail: WebElement) -> bool:
        return None

    def get_trail_night_skiing(self, trail: WebElement) -> bool:
        return False


class CannonMountain(Resort):
    _snow_report_url = 'https://www.cannonmt.com/mountain/trails-lifts'
    _trails_grouped_by_section = False
    _lifts_css_selector = 'tr.lift-data'
    _trails_css_selector = 'tr.trail-data'

    def get_lift_name(self, lift: WebElement) -> str:
        return lift.find_element(
            by=By.CLASS_NAME, value='lift-name'
        ).text

    def get_item_status(self, item: WebElement) -> str:
        # Cannon treats lifts + trails identically in terms of status.
        try:
            item.find_element(
                by=By.CSS_SELECTOR, value='.icon.open'
            )
            return 'Open'
        except:
            return 'Closed'

    def get_lift_status(self, lift: WebElement) -> str:
        return self.get_item_status(lift)

    def get_trail_name(self, trail: WebElement) -> str:
        return trail.find_element(
            by=By.CSS_SELECTOR, value='td.trail-name'
        ).text

    def get_trail_status(self, trail: WebElement) -> str:
        return self.get_item_status(trail)

    def get_trail_type(self, trail: WebElement) -> str:
        type_icon: WebElement = trail.find_element(
            by=By.CSS_SELECTOR, value='td.difficulty > img'
        )
        return type_icon.get_attribute('alt')

    def get_trail_groomed(self, trail: WebElement) -> bool:
        try:
            trail.find_element(
                by=By.CSS_SELECTOR, value='td.groomed > img.groomed'
            )
            return True
        except:
            return False

    def get_trail_night_skiing(self, trail: WebElement) -> bool:
        return False


# # resorts = [
# #     BoltonValley, JayPeak, SuicideSix
# # ]
# resorts = [CannonMountain]
# for resort in resorts:
#     r = resort()
#     print(json.dumps(r.get_lifts_summary(), indent=2))
#     print(json.dumps(r.get_trails_summary(), indent=2))

#     del r


# c = CannonMountain()
# lifts = c.get_lift_elements()
# for lift in lifts:
#     print(c.get_lift_name(lift))
#     print(c.get_lift_status(lift))
