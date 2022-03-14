from typing import List, Optional
import json
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By


class Settable():
    def __init__(self, **properties):
        if properties:
            for property in properties.keys():
                setattr(self, f'_{property}', properties.get(property))


class Resort():
    _lifts_css_selector: str
    _trails_css_selector: str
    _trail_sections_css_selector: str
    _trail_section_name_css_selector: str
    _trails_grouped_by_section: bool
    _snow_report_url: str

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
    def trail_section_name_css_selector(self) -> str:
        return self._trail_section_name_css_selector

    @property
    def trails_grouped_by_section(self) -> bool:
        return self._trails_grouped_by_section

    @property
    def snow_report_url(self) -> str:
        return self._snow_report_url

    def get_lifts(self, peak: Optional[WebElement] = None) -> List[WebElement]:
        """Get the HTML element containing all lift information."""
        return self.browser.find_elements(by=By.CSS_SELECTOR, value=self.lifts_css_selector)

    def get_trails(self, trail_section: Optional[WebElement] = None) -> List['Trail']:
        """
        Get the HTML element containing all trail information.
        If a trail_section is supplied, only return the trails belonging to that section.
        """
        if self.trails_grouped_by_section and not trail_section:
            # If we're requesting all trails AND they're grouped by section, retrieve them section-by-section.
            trail_sections = self.get_trail_sections()
            trails = []
            for trail_section in trail_sections:
                trails.extend(self.get_trails(trail_section))
            return trails

        search_within = trail_section if trail_section else self.browser
        trail_elements = search_within.find_elements(
            by=By.CSS_SELECTOR, value=self.trails_css_selector)

        return [
            Trail(
                resort=self,
                name=self.get_trail_name(element),
                trail_type=self.get_trail_section_name(trail_section)
                if trail_section else self.get_trail_type(element),
                status=self.get_trail_status(element),
                groomed=self.get_trail_groomed(element),
                night_skiing=self.get_trail_night_skiing(element)
            ) for element in trail_elements
        ]

    def get_trail_sections(self) -> List[WebElement]:
        """Get the HTML container for all trail information."""
        return self.browser.find_elements(by=By.CSS_SELECTOR, value=self.trail_sections_css_selector)

    def get_trail_section_name(self, trail_section: WebElement) -> str:
        """Return the difficulty or classification of a group of trails."""
        return trail_section.find_element(by=By.CSS_SELECTOR, value=self.trail_section_name_css_selector).text

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

    def get_trails_summary(self) -> List[dict]:
        trails = self.get_trails()
        summary = [
            {
                'name': trail.name,
                'trail_type': trail.trail_type,
                'status': trail.status,
                'groomed': trail.groomed,
                'night_skiing': trail.night_skiing
            } for trail in trails
        ]
        return summary


class Trail(Settable):
    _resort: Resort
    _name: str
    _trail_type: str
    _status: str
    _groomed: bool
    _night_skiing: bool

    @property
    def resort(self) -> Resort:
        """An instance of the Resort that this trail belongs to"""
        return self._resort

    @property
    def trail_type(self) -> str:
        """Either the difficulty of the trail, or its type (i.e. "Terrain park")"""
        return self._trail_type

    @property
    def name(self) -> str:
        """The name of the trail as it appears in reports/maps."""
        return self._name

    @property
    def status(self) -> str:
        """The last-reported status of the trail (i.e. open, closed, partially open)"""
        return self._status

    @property
    def groomed(self) -> bool:
        """True when the trail is groomed, False for natural snow."""
        return self._groomed

    @property
    def night_skiing(self) -> bool:
        """True if the trail is open + lit during night skiing hours"""
        return self._night_skiing


class SnowReport(Resort):
    _lifts_css_selector = '.SnowReport-Lift.SnowReport-feature'
    _trails_css_selector = '.SnowReport-Trail.SnowReport-feature'
    _trail_sections_css_selector = '.SnowReport-section.SnowReport-section--trails'
    _trail_section_name_css_selector = 'h2.SnowReport-section-title'
    _trails_grouped_by_section = True

    def get_trail_name(self, trail: WebElement) -> str:
        trail_name_element = trail.find_element(
            by=By.CLASS_NAME, value='SnowReport-feature-title')
        return trail_name_element.text

    def get_trail_status(self, trail: WebElement) -> str:
        trail_status_icon: WebElement = trail.find_element(
            by=By.CLASS_NAME, value='SnowReport-item-status')
        trail_status: WebElement = trail_status_icon.find_element(
            by=By.TAG_NAME, value='span')
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
