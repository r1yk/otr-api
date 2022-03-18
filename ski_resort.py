from typing import List, Optional

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver

from sqlalchemy import Boolean, Column, String, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Settable():
    def __init__(self, *args, **properties):
        if properties:
            for property in properties.keys():
                setattr(self, f'_{property}', properties.get(property))


class Parser(Settable):
    lifts_container_css_selector: str
    lift_css_selector: str
    trails_container_css_selector: str
    trail_css_selector: str

    def __init__(self, browser: WebDriver, **parser_kwargs):
        self.browser = browser
        super().__init__(parser_kwargs)

    def get_lift_elements(self) -> List[WebElement]:
        """Get the HTML elements containing all lift information."""
        lift_elements = []
        lifts_containers = self.browser.find_elements(
            By.CSS_SELECTOR, self.lifts_container_css_selector
        )
        for container in lifts_containers:
            lift_elements.extend(container.find_elements(
                By.CSS_SELECTOR, self.lift_css_selector))
        return lift_elements

    def get_lift_name(self, lift: WebElement) -> str:
        """Find the name of this lift within the HTML element."""

    def get_lift_status(self, lift: WebElement) -> str:
        """Find the status of this lift within the HTML element."""

    def get_lifts(self, lift_name_to_id: Optional[dict] = None) -> List['Lift']:
        lifts = []
        for lift_element in self.get_lift_elements():
            lift_name = self.get_lift_name(lift_element)
            lifts.append(
                Lift(
                    id=lift_name_to_id.get(
                        lift_name) if lift_name_to_id else None,
                    name=lift_name,
                    status=self.get_lift_status(lift_element)
                )
            )
        return lifts

    def get_trail_elements(self) -> List[WebElement]:
        trail_elements = []
        trails_containers = self.browser.find_elements(
            By.CSS_SELECTOR, self.trails_container_css_selector
        )
        for container in trails_containers:
            trail_elements.extend(
                container.find_elements(
                    By.CSS_SELECTOR, self.trail_css_selector))
        return trail_elements

    def get_trails(self, trail_name_to_id: Optional[dict] = None) -> List['Trail']:
        trails = []
        for trail_element in self.get_trail_elements():
            trail_name = self.get_trail_name(trail_element)
            trails.append(
                Trail(
                    id=trail_name_to_id.get(
                        trail_name) if trail_name_to_id else None,
                    name=trail_name,
                    trail_type=self.get_trail_type(trail_element),
                    status=self.get_trail_status(trail_element),
                    groomed=self.get_trail_groomed(trail_element),
                    night_skiing=self.get_trail_night_skiing(trail_element)
                )
            )
        return trails

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


class Resort(Base):
    __tablename__ = 'resorts'
    id = Column(String, primary_key=True)
    name = Column(String)
    parser_name = Column(String)
    lifts_container_ss_selector = Column(String)
    trails_container_css_selector = Column(String)
    trail_css_selector = Column(String)
    trail_report_url = Column(String)
    snow_report_url = Column(String)

    def get_parser(self, browser: WebDriver) -> Parser:
        pass


class Lift(Base):
    __tablename__ = 'lifts'
    id = Column(String, primary_key=True)
    resort_id = Column(ForeignKey('resorts._id'))
    name = Column(String)
    status = Column(String)


class Trail(Base):
    __tablename__ = 'trails'
    id = Column(String, primary_key=True)
    resort = Column(ForeignKey('resorts._id'))
    name = Column(String)
    trail_type = Column(String)
    status = Column(String)
    groomed = Column(Boolean)
    night_skiing = Column(Boolean)


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
