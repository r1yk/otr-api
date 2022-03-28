from datetime import datetime, timedelta
from enum import Enum
from importlib import import_module
import sys
from time import sleep
from traceback import print_exception
from typing import List, Optional

from dotenv import dotenv_values
from nanoid import generate as generate_id
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from sqlalchemy import select, or_
from sqlalchemy.orm import Query
from sqlalchemy.orm.session import Session

from lib.models import Resort, Lift, Trail
from lib.postgres import get_session
from lib.util import get_key_value_pairs, get_changes, Settable


class Rating(Enum):
    GREEN = 0
    BLUE = 1
    BLACK = 2
    DOUBLE_BLACK = 3
    TRIPLE_BLACK = 4
    GLADES = 5
    DOUBLE_GLADES = 6
    WOODED = 7
    TERRAIN_PARK = 8


class Parser(Settable):
    lift_css_selector = None
    trail_css_selector = None
    trail_type_to_rating: dict = {}

    def __init__(self, browser: WebDriver):
        self.browser = browser

    @classmethod
    def element_has_child(cls, element: WebElement, css_selector: str) -> bool:
        try:
            element.find_element(
                By.CSS_SELECTOR, css_selector)
            return True
        except:
            return False

    def get_lift_elements(self) -> List[WebElement]:
        """Get the HTML elements containing all lift information."""
        print('Looking for lifts...')
        elements = WebDriverWait(self.browser, timeout=10).until(lambda browser: browser.find_elements(
            By.CSS_SELECTOR, self.lift_css_selector
        ))
        print(f'Found {len(elements)} lifts')
        return elements

    def get_lift_name(self, lift: WebElement) -> str:
        """Find the name of this lift within the HTML element."""

    def get_lift_status(self, lift: WebElement) -> str:
        """Find the status of this lift within the HTML element."""

    def get_lifts(self) -> List['Lift']:
        lifts = []
        for lift_element in self.get_lift_elements():
            lift = Lift(
                name=self.get_lift_name(lift_element),
                unique_name=self.get_lift_name(lift_element),
                status=self.get_lift_status(lift_element))
            lift.is_open = lift.status.lower() == 'open'
            lifts.append(lift)
        return lifts

    def get_trail_elements(self) -> List[WebElement]:
        print('Looking for trails...')
        elements = WebDriverWait(self.browser, timeout=10).until(lambda browser: browser.find_elements(
            By.CSS_SELECTOR, self.trail_css_selector
        ))
        print(f'Found {len(elements)} trails')
        return elements

    def get_trails(self) -> List['Trail']:
        trails = []
        for trail_element in self.get_trail_elements():
            trail = Trail(
                name=self.get_trail_name(trail_element),
                trail_type=self.get_trail_type(trail_element),
                status=self.get_trail_status(trail_element).lower(),
                groomed=self.get_trail_groomed(trail_element),
                night_skiing=self.get_trail_night_skiing(trail_element),
                icon=self.get_trail_icon(trail_element)
            )
            trail.is_open = trail.status.lower() == 'open'
            trails.append(trail)
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

    def get_trail_icon(self, trail: WebElement) -> str:
        trail_type = self.get_trail_type(trail)
        if trail_type:
            return self.trail_type_to_rating.get(trail_type)
        return None


class Webscraper:
    def __init__(self, browser: WebDriver, resort: Resort):
        self.browser = browser
        self.resort = resort
        self.db_session: Session = Session.object_session(resort)

    def add_or_update(self, db_rows: List, scraped_data: List, at: datetime) -> None:
        name_lookup = get_key_value_pairs(db_rows, key='unique_name')
        for scraped_item in scraped_data:
            item = name_lookup.get(scraped_item.unique_name)
            # If this item exists in the database, merge in any freshly-scraped data.
            if item:
                scraped_item.id = item.id
                self.db_session.merge(scraped_item)
                changes = get_changes(item)
                if changes:
                    print('UPDATE:', item.name, changes)
                    item.updated_at = at
            # Otherwise add a new item to the database that's tied to this resort.
            else:
                print('new item', scraped_item.name)
                scraped_item.id = generate_id()
                scraped_item.resort_id = self.resort.id
                scraped_item.updated_at = at
                self.db_session.add(scraped_item)

    def get_parser(self) -> Parser:
        """Construct and return an instance of a `Parser` based on the `parser_name` column in the database."""
        # constructor = getattr(
        #     sys.modules['parsers'], self.resort.parser_name)
        items = self.resort.parser_name.split('.')
        module_name, class_name = items[0], items[1]

        constructor = import_module(
            f'webscraper.parsers.{module_name}')

        constructor = getattr(
            sys.modules[f'webscraper.parsers.{module_name}'], class_name
        )

        return constructor(self.browser)

    def get_lifts(self) -> List['Lift']:
        return self.db_session.execute(select(Lift).where(
            Lift.resort_id == self.resort.id
        )).scalars()

    def get_trails(self) -> List['Trail']:
        return self.db_session.execute(select(Trail).where(
            Trail.resort_id == self.resort.id
        )).scalars()

    def scrape_trail_report(self):
        print(f'scraping {self.resort.name}...')
        try:
            now = datetime.now()
            self.browser.get(self.resort.trail_report_url)
            print('Loaded', self.resort.trail_report_url)
            if self.resort.additional_wait_seconds:
                print('Additional wait: ', self.resort.additional_wait_seconds)
                sleep(self.resort.additional_wait_seconds)

            parser = self.get_parser()

            db_lifts, scraped_lifts = self.get_lifts(), parser.get_lifts()
            db_trails, scraped_trails = self.get_trails(), parser.get_trails()

            self.add_or_update(db_lifts, scraped_lifts, now)
            self.add_or_update(db_trails, scraped_trails, now)

            self.resort.total_lifts = len(scraped_lifts)
            self.resort.open_lifts = len(
                [l for l in scraped_lifts if l.is_open])

            self.resort.total_trails = len(scraped_trails)
            self.resort.open_trails = len(
                [t for t in scraped_trails if t.is_open])
            self.resort.updated_at = now

        except Exception as e:
            print_exception(e)


def get_browser(options: Optional[List[str]] = None) -> WebDriver:
    chrome_options = Options()
    if options:
        for option in options:
            chrome_options.add_argument(option)

    if dotenv_values().get('MODE') == 'headless':
        chrome_options.add_argument('--headless')

    return Chrome(options=chrome_options)


def scrape_resort(resort_id: str) -> None:
    browser = get_browser()
    with get_session() as session:
        resort = session.get(Resort, resort_id)
        webscraper = Webscraper(browser, resort)
        webscraper.scrape_trail_report()
        session.commit()

    browser.close()


def scrape_resorts(query: Optional[Query] = None) -> None:
    resort_query = query or select(Resort).where(
        or_(
            Resort.updated_at == None,
            Resort.updated_at < datetime.now() - timedelta(minutes=10)
        )
    )

    browser = get_browser()
    with get_session() as session:
        resorts: List[Resort] = session.execute(resort_query).scalars()
        for resort in resorts:
            webscraper = Webscraper(browser, resort)
            webscraper.scrape_trail_report()
            session.commit()

    browser.close()
