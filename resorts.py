import json
from typing import List, Optional
from ski_resort import Resort, SnowReport
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


class BoltonValley(SnowReport):
    _snow_report_url = 'https://snow.boltonvalley.com/snow-report/snow/snow-report/'


class JayPeak(SnowReport):
    _snow_report_url = 'https://digital.jaypeakresort.com/conditions/snow-report/snow-report/'


class WatervilleValley(SnowReport):
    _snow_report_url = 'https://features.waterville.com/propsnow/'


class SuicideSix(Resort):
    _trails_grouped_by_section = False
    _snow_report_url = 'https://www.suicide6.com/the-mountain/conditions'

    _lifts_and_trails: dict

    def __init__(self, browser):
        self._lifts_and_trails = None
        super().__init__(browser)

    def get_lift_elements(self, peak: Optional[WebElement] = None) -> List[WebElement]:
        return self.get_lifts_and_trails().get('lifts')

    def get_lift_name(self, lift: WebElement) -> str:
        name_element = lift.find_element(
            By.CLASS_NAME, 'title'
        )
        return name_element.text

    def get_lift_status(self, lift: WebElement) -> str:
        status_element = lift.find_element(
            By.CLASS_NAME, 'field--name-field-status'
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
                By.CLASS_NAME, 'node--type-lift-trail'
            )
            for element in all_elements:
                # If the element has a child with class "level", it's a trail. Otherwise it's a lift.
                try:
                    element.find_element(By.CLASS_NAME, 'level')
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
            By.CLASS_NAME, 'title'
        )
        return trail_name_element.text

    def get_trail_status(self, trail: WebElement) -> str:
        trail_status_element = trail.find_element(
            By.CLASS_NAME, 'field--name-field-status'
        )
        return trail_status_element.text

    def get_trail_type(self, trail: WebElement) -> str:
        trail_type_element = trail.find_element(
            By.CLASS_NAME, 'level'
        )
        return trail_type_element.text

    def get_trail_groomed(self, trail: WebElement) -> bool:
        return None

    def get_trail_night_skiing(self, trail: WebElement) -> bool:
        return False


class Stowe(Resort):
    _snow_report_url = 'https://www.stowe.com/the-mountain/mountain-conditions/terrain-and-lift-status.aspx'
    _lifts_css_selector = '.liftStatus__lifts__row'
    _trails_css_selector = '.trailStatus__trails__row'
    _trails_grouped_by_section = False

    def get_lift_name(self, lift: WebElement) -> str:
        name_element: WebElement = lift.find_element(
            By.CSS_SELECTOR, 'span.liftStatus__lifts__row__title'
        )
        return name_element.text

    def get_item_status(self, item: WebElement) -> str:
        try:
            item.find_element(
                By.CSS_SELECTOR, 'div.icon-status-open'
            )
            return 'Open'
        except:
            return 'Closed'

    def get_lift_status(self, lift: WebElement) -> str:
        return self.get_item_status(lift)

    def get_trail_status(self, trail: WebElement) -> str:
        return self.get_item_status(trail)

    def get_trail_name(self, trail: WebElement) -> str:
        name_element: WebElement = trail.find_element(
            By.CLASS_NAME, 'trailStatus__trails__row--name'
        )
        return name_element.get_attribute('innerText')

    def get_trail_type(self, trail: WebElement) -> str:
        trail_types = ['beginner', 'intermediate',
                       'mostdifficult', 'expert', 'terrainpark']
        # Trail difficulty is the 2nd icon in the row.
        trail_icon: WebElement = trail.find_element(
            By.CSS_SELECTOR, 'div.trailStatus__trails__row--icon:nth-of-type(2)'
        )
        icon_class = trail_icon.get_attribute('class')
        for trail_type in trail_types:
            if icon_class.find(trail_type) != -1:
                return trail_type

        raise RuntimeError(
            'Trail type not found'
        )

    def get_trail_groomed(self, trail: WebElement) -> bool:
        try:
            trail.find_element(
                By.CSS_SELECTOR, 'div.icon-status-snowcat'
            )
            return True
        except:
            return False

    def get_trail_night_skiing(self, trail: WebElement) -> bool:
        return False


class CannonMountain(Resort):
    _snow_report_url = 'https://www.cannonmt.com/mountain/trails-lifts'
    _trails_grouped_by_section = False
    _lifts_css_selector = 'tr.lift-data'
    _trails_css_selector = 'tr.trail-data'

    def get_lift_name(self, lift: WebElement) -> str:
        return lift.find_element(
            By.CLASS_NAME, 'lift-name'
        ).text

    def get_item_status(self, item: WebElement) -> str:
        # Cannon treats lifts + trails identically in terms of status.
        try:
            item.find_element(
                By.CSS_SELECTOR, '.icon.open'
            )
            return 'Open'
        except:
            return 'Closed'

    def get_lift_status(self, lift: WebElement) -> str:
        return self.get_item_status(lift)

    def get_trail_name(self, trail: WebElement) -> str:
        return trail.find_element(
            By.CSS_SELECTOR, 'td.trail-name'
        ).text

    def get_trail_status(self, trail: WebElement) -> str:
        return self.get_item_status(trail)

    def get_trail_type(self, trail: WebElement) -> str:
        type_icon: WebElement = trail.find_element(
            By.CSS_SELECTOR, 'td.difficulty > img'
        )
        return type_icon.get_attribute('alt')

    def get_trail_groomed(self, trail: WebElement) -> bool:
        try:
            trail.find_element(
                By.CSS_SELECTOR, 'td.groomed > img.groomed'
            )
            return True
        except:
            return False

    def get_trail_night_skiing(self, trail: WebElement) -> bool:
        return False


class Sugarbush(Resort):
    _snow_report_url = 'https://www.sugarbush.com/mountain/conditions'
    _trails_grouped_by_section = False
    _lifts_css_selector = 'ul.Lifts_list__3PwcO > li'
    _trails_css_selector = 'ul.Trails_trailsList__3gYwp > li'

    def get_lift_name(self, lift: WebElement) -> str:
        return lift.find_element(
            By.CSS_SELECTOR, 'h3.Lifts_name__1YvQ1'
        ).text

    def get_lift_status(self, lift: WebElement) -> str:
        return lift.find_element(
            By.CSS_SELECTOR, 'p.Lifts_status__z9n5V'
        ).text

    def get_trail_name(self, trail: WebElement) -> str:
        return trail.find_element(
            By.CSS_SELECTOR, 'dd > h4.Trails_trailName__1_oua'
        ).text

    def get_trail_status(self, trail: WebElement) -> str:
        return trail.find_element(
            By.CSS_SELECTOR, 'dd > p.Trails_trailStatus__jJDvi'
        ).text

    def get_trail_type(self, trail: WebElement) -> str:
        return trail.find_element(
            By.CSS_SELECTOR,
            'div.Trails_trailDetailDifficulty__2n1p- > dd > span'
        ).text

    def get_trail_groomed(self, trail: WebElement) -> bool:
        try:
            trail_features: List[WebElement] = trail.find_elements(
                By.CSS_SELECTOR, 'ul.Trails_trailFeatures__2pFdC > li'
            )
            for feature in trail_features:
                if feature.text == 'Grooming':
                    return True
            return False
        except:
            return False

    def get_trail_night_skiing(self, trail: WebElement) -> bool:
        return False
