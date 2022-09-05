from datetime import datetime, timedelta
from enum import Enum
from importlib import import_module
import sys
from time import sleep
from traceback import print_exception
from typing import List, Optional, Union, Tuple, Type

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
        """Return `true` if a there is a match for a given `css_selector` within a given web element."""
        try:
            element.find_element(By.CSS_SELECTOR, css_selector)
            return True
        except:
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
        """Find the status of this trail within the HTML element (i.e. open, closed, partially open)."""

    def get_trail_groomed(self, trail: WebElement) -> bool:
        """Return whether or not this trail has groomed snow."""

    def get_trail_night_skiing(self, trail: WebElement) -> bool:
        """Return whether or not this trail has lighting for skiing after dark."""

    def get_trail_rating(self, trail: WebElement) -> int:
        """Get the trail type as described by the resort, and return the corresponding normalized `Rating` value."""
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
        """Add this lift or trail to the DB if it doesn't exist, or update it if it does."""
        name_lookup = get_key_value_pairs(db_rows, key="unique_name")
        for scraped_item in scraped_data:
            item = name_lookup.get(scraped_item.unique_name)
            # If this item exists in the database, merge in any freshly-scraped data.
            if item:
                scraped_item.id = item.id
                self.db_session.merge(scraped_item)
                changes = get_changes(item)
                if changes:
                    self.examine_changes(item, changes, at)
                    item.updated_at = at

            # Otherwise add a new item to the database that's tied to this resort.
            else:
                print("new item", scraped_item.name)
                scraped_item.id = generate_id()
                scraped_item.resort_id = self.resort.id
                scraped_item.updated_at = at
                self.db_session.add(scraped_item)

    def get_parser(self) -> Parser:
        """Construct and return an instance of a `Parser` based on the `parser_name` column in the database."""
        items = self.resort.parser_name.split(".")
        module_name, class_name = items[0], items[1]

        # Import the file in `webscraper/parsers/` that contains the implementation of the parser
        import_module(f"webscraper.parsers.{module_name}")

        # Find the class definition within the imported module
        ParserClass: Type[Parser] = getattr(
            sys.modules[f"webscraper.parsers.{module_name}"], class_name
        )

        # Return an initialized `Parser` that can access the browser
        return ParserClass(self.browser)

    def get_lifts(self) -> List["Lift"]:
        """Return a `Lift` for each row in the `lifts` table that belongs to this resort."""
        return self.db_session.execute(
            select(Lift).where(Lift.resort_id == self.resort.id)
        ).scalars()

    def get_trails(self) -> List["Trail"]:
        """Return a `Trail` for each row in the `lifts` table that belongs to this resort."""
        return self.db_session.execute(
            select(Trail).where(Trail.resort_id == self.resort.id)
        ).scalars()

    def scrape_trail_report(self):
        """Trigger the end-to-end webscraping session."""
        print("\n", f"scraping {self.resort.name}...")
        try:
            now = datetime.now()
            self.browser.get(self.resort.trail_report_url)
            print("Loaded", self.resort.trail_report_url)
            if self.resort.additional_wait_seconds:
                print("Additional wait: ", self.resort.additional_wait_seconds)
                sleep(self.resort.additional_wait_seconds)

            parser = self.get_parser()

            db_lifts, scraped_lifts = self.get_lifts(), parser.get_lifts()
            db_trails, scraped_trails = self.get_trails(), parser.get_trails()

            self.add_or_update(db_lifts, scraped_lifts, now)
            self.add_or_update(db_trails, scraped_trails, now)

            self.resort.total_lifts = len(scraped_lifts)
            self.resort.open_lifts = len([l for l in scraped_lifts if l.is_open])

            self.resort.total_trails = len(scraped_trails)
            self.resort.open_trails = len([t for t in scraped_trails if t.is_open])
            self.resort.updated_at = now

        except Exception as e:
            print_exception(e)

    def examine_changes(self, item, changes: dict, at: datetime) -> None:
        """Handle additional actions to be taken when specific columns are updated."""
        print("UPDATE: ", item.name, changes)
        is_open_change: Union[Tuple, None] = changes.get("is_open")
        if is_open_change:
            open = is_open_change[1]
            if open:
                item.last_opened_on = at.date()
            else:
                item.last_closed_on = at.date()


def get_browser(options: Optional[List[str]] = None) -> WebDriver:
    """Return a running instance of (optionally headless) Google Chrome."""
    chrome_options = Options()
    if options:
        for option in options:
            chrome_options.add_argument(option)

    if dotenv_values().get("MODE") == "headless":
        chrome_options.add_argument("--headless")

    return Chrome(options=chrome_options)


def scrape_resort(resort_id: str) -> None:
    """Carry out a webscrape for a single resort."""
    browser = get_browser()
    with get_session() as session:
        resort = session.get(Resort, resort_id)
        webscraper = Webscraper(browser, resort)
        webscraper.scrape_trail_report()
        session.commit()

    browser.close()


def scrape_resorts(query: Optional[Query] = None) -> None:
    """Carry out a webscrape for all resorts, or all resorts matching an optionally provided `Query`."""
    resort_query = query or select(Resort).where(
        or_(
            Resort.updated_at == None,
            Resort.updated_at < datetime.utcnow() - timedelta(minutes=10),
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
