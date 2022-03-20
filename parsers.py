from typing import List, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.webdriver import WebDriver

import ski_resort
from util import Settable


class Parser(Settable):
    lifts_container_css_selector: str
    lift_css_selector: str
    trails_container_css_selector: str
    trail_css_selector: str

    def __init__(self, browser: WebDriver, **parser_kwargs):
        self.browser = browser
        super().__init__(**parser_kwargs)

    def get_lift_elements(self) -> List[WebElement]:
        """Get the HTML elements containing all lift information."""
        if hasattr(self, 'lifts_container_css_selector'):
            lift_elements = []
            lifts_containers = self.browser.find_elements(
                By.CSS_SELECTOR, self.lifts_container_css_selector
            )
            for container in lifts_containers:
                lift_elements.extend(container.find_elements(
                    By.CSS_SELECTOR, self.lift_css_selector))
            return lift_elements

        return self.browser.find_elements(
            By.CSS_SELECTOR, self.lift_css_selector
        )

    def get_lift_name(self, lift: WebElement) -> str:
        """Find the name of this lift within the HTML element."""

    def get_lift_status(self, lift: WebElement) -> str:
        """Find the status of this lift within the HTML element."""

    def get_lifts(self) -> List['Settable']:
        return [
            Settable(
                name=self.get_lift_name(lift_element),
                status=self.get_lift_status(lift_element)
            ) for lift_element in self.get_lift_elements()
        ]

    def get_trail_elements(self) -> List[WebElement]:
        if hasattr(self, 'trails_container_css_selector'):
            trail_elements = []
            trails_containers = self.browser.find_elements(
                By.CSS_SELECTOR, self.trails_container_css_selector
            )
            for container in trails_containers:
                trail_elements.extend(
                    container.find_elements(
                        By.CSS_SELECTOR, self.trail_css_selector))
            return trail_elements

        return self.browser.find_elements(
            By.CSS_SELECTOR, self.trail_css_selector
        )

    def get_trails(self) -> List['Settable']:
        return [
            Settable(
                name=self.get_trail_name(trail_element),
                trail_type=self.get_trail_type(trail_element),
                status=self.get_trail_status(trail_element),
                groomed=self.get_trail_groomed(trail_element),
                night_skiing=self.get_trail_night_skiing(trail_element)
            ) for trail_element in self.get_trail_elements()
        ]

    def get_trail_name(self, trail: WebElement) -> str:
        """Find the name of this trail within the HTML element."""

    def get_trail_type(self, trail: WebElement) -> str:
        """Return either the difficulty or classification (i.e. "Terrain park" of this trail."""

    def get_trail_status(self, trail: WebElement) -> str:
        """Find the status of this trail within the HTML element (i.e. open, closed, partially open)."""

    def get_trail_groomed(self, trail: WebElement) -> bool:
        """Return whether or not this trail has groomed snow."""

    def get_trail_night_skiing(self, trail: WebElement) -> bool:
        """Return whether or not this trail has lighting for skiing after dark."""


class SnowReportCSS(Parser):
    """A common UI setup that seems to be shared by quite a few mountains."""

    def __init__(self, browser: WebDriver, **kwargs):
        self.lifts_container_css_selector = 'section.SnowReport-section--lifts'
        self.lift_css_selector = 'article.SnowReport-Lift.SnowReport-feature'
        self.trails_container_css_selector = 'section.SnowReport-section--trails'
        self.trail_css_selector = 'article.SnowReport-Trail.SnowReport-feature'
        super().__init__(browser, **kwargs)

    def get_lift_name(self, lift: WebElement) -> str:
        lift_name_element = lift.find_element(
            By.CLASS_NAME, 'SnowReport-feature-title'
        )
        return lift_name_element.text

    def get_lift_status(self, lift: WebElement) -> List[dict]:
        lift_status_element: WebElement = lift.find_element(
            By.CLASS_NAME, 'SnowReport-item-status'
        )
        return lift_status_element.find_element(
            By.CLASS_NAME, 'SnowReport-sr-label'
        ).text

    def get_trail_name(self, trail: WebElement) -> str:
        trail_name_element = trail.find_element(
            By.CLASS_NAME, 'SnowReport-feature-title')
        return trail_name_element.text

    def get_trail_status(self, trail: WebElement) -> str:
        trail_status_icon: WebElement = trail.find_element(
            By.CLASS_NAME, 'SnowReport-item-status')
        trail_status: WebElement = trail_status_icon.find_element(
            By.TAG_NAME, 'span')
        return trail_status.text

    def get_trail_type(self, trail: WebElement) -> str:
        parent: WebElement = trail.find_element(
            By.XPATH, 'ancestor::section'
        )
        header: WebElement = parent.find_element(
            By.TAG_NAME, 'h2'
        )
        return header.text

    def get_trail_groomed(self, trail: WebElement) -> bool:
        try:
            # If this element is found, the trail is groomed.
            trail.find_element(
                By.CLASS_NAME, 'pti-groomed')
            return True
        except:
            return False

    def get_trail_night_skiing(self, trail: WebElement) -> bool:
        try:
            # If this element is found, the trail is open for night skiing.
            trail.find_element(
                By.CLASS_NAME, 'pti-moon-mining')
            return True
        except:
            return False


class SuicideSix(Parser):
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


class Stowe(Parser):
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


class Sugarbush(Parser):
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
