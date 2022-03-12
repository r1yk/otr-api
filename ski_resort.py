from typing import List, Optional
import json
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

class Resort():
    _lifts_css_selector = None
    _trails_css_selector = None
    _trail_sections_css_selector = None
    _snow_report_url = None

    def __init__(self):
        """Fire up the browser, and fetch the snow report."""
        self.browser = webdriver.Chrome()
        self.browser.get(self._snow_report_url)

    def __del__(self):
        """Close the browser."""
        self.browser.close()
    
    @property
    def lifts_css_selector(self) -> str:
        return self._lifts_css_selector
        
    @property
    def trails_css_selector(self) -> str:
        return self._trails_css_selector

    @property
    def trail_sections_css_selector(self) -> str:
        return self._trail_sections_css_selector

    @property
    def snow_report_url(self) -> str:
        return self._snow_report_url

    def get_lifts(self, peak: Optional[WebElement] = None) -> List[WebElement]:
        """Get the HTML element containing all lift information."""
        return self.browser.find_elements(by = By.CSS_SELECTOR, value=self.lifts_css_selector)
    
    def get_trails(self, trail_section: Optional[WebElement] = None) -> List[WebElement]:
        """
        Get the HTML element containing all trail information.
        If a trail_section is supplied, only return the trails belonging to that section.
        """
        if trail_section is not None:
            return trail_section.find_elements(by=By.CSS_SELECTOR, value=self.trails_css_selector)
        
        return self.browser.find_elements(by=By.CSS_SELECTOR, value=self.trails_css_selector)

    def get_trail_sections(self) -> List[WebElement]:
        """Get the HTML container for all trail information."""
        return self.browser.find_elements(by=By.CSS_SELECTOR, value=self.trail_sections_css_selector)
    
    def get_trail_name(self, trail: WebElement) -> str:
        """Find the name of this trail within the HTML element."""

    def get_trail_status(self, trail: WebElement) -> str:
        """Find the status of this trail within the HTML element (i.e. open, closed, partially open)."""

    def get_trail_groomed(self, trail: WebElement) -> bool:
        """Return whether or not this trail has groomed snow."""

    def get_trail_night_skiing(self, trail: WebElement) -> bool:
        """Return whether or not this trail has lighting for skiing after dark."""

    def get_trails_summary(self) -> List[dict]:
        trails = self.get_trails()
        summary = [
            {
                'name': self.get_trail_name(trail),
                'status': self.get_trail_status(trail),
                'groomed': self.get_trail_groomed(trail),
                'night_skiing': self.get_trail_night_skiing(trail)
            } for trail in trails
        ]
        return summary



class BoltonValley(Resort):
    _lifts_css_selector = '.SnowReport-Lift.SnowReport-feature'
    _trails_css_selector = '.SnowReport-Trail.SnowReport-feature'
    _trail_sections_css_selector = '.SnowReport-section.SnowReport-section--trails'
    _snow_report_url = 'https://snow.boltonvalley.com/snow-report/snow/snow-report/'

    def get_trail_name(self, trail: WebElement) -> str:
        trail_name_element = trail.find_element(by=By.CLASS_NAME, value='SnowReport-feature-title')
        return trail_name_element.text
    
    def get_trail_status(self, trail: WebElement) -> str:
        trail_status_icon: WebElement = trail.find_element(
            by=By.CLASS_NAME, value='SnowReport-item-status')
        trail_status: WebElement = trail_status_icon.find_element(by=By.TAG_NAME, value='span')
        return trail_status.text
    
    def get_trail_groomed(self, trail: WebElement) -> bool:
        try:
            # If this element is found, the trail is groomed.
            trail.find_element(
                by=By.CLASS_NAME, value='pti-groomed')
            return True
        except:
            return False
    
    def get_trail_night_skiing(self, trail: WebElement) -> bool:
        try:
            # If this element is found, the trail is open for night skiing.
            trail.find_element(
                by=By.CLASS_NAME, value='pti-moon-mining')
            return True
        except:
            return False

b = BoltonValley()
# sections = b.get_trail_sections()
# for section in sections:
#     trails = b.get_trails(section)
#     for trail in trails:
#         print(b.get_trail_name(trail))
#         print(b.get_trail_status(trail))
#         print(b.get_trail_groomed(trail))
#         print(b.get_trail_night_skiing(trail))
summary = b.get_trails_summary()
print(json.dumps(summary, indent=2))