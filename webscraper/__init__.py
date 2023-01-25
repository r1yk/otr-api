# pylint: disable=broad-except
"""
Webscraper
"""
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
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
from sqlalchemy import select, or_
from sqlalchemy.orm import Query
from sqlalchemy.orm.session import Session

from lib.models import Resort, Lift, Trail
from lib.postgres import get_session
from lib.util import get_key_value_pairs, get_changes
from webscraper.parser import Parser


class Rating(Enum):
    """
    Constant mapping from trail types -> integers.
    """

    GREEN = 0
    BLUE = 1
    BLACK = 2
    DOUBLE_BLACK = 3
    TRIPLE_BLACK = 4
    GLADES = 5
    DOUBLE_GLADES = 6
    WOODED = 7
    TERRAIN_PARK = 8


class Webscraper:
    """
    Webscraper
    """

    def __init__(self, browser: WebDriver, resort: Resort):
        self.browser = browser
        self.resort = resort
        self.db_session: Session = Session.object_session(resort)
        self.parser = self.get_parser()

    def add_or_update(
        self, db_rows: List, scraped_data: List, updated_at: datetime
    ) -> None:
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
                    self.examine_changes(item, changes, updated_at)
                    item.updated_at = updated_at

            # Otherwise add a new item to the database that's tied to this resort.
            else:
                print("new item", scraped_item.name)
                scraped_item.id = generate_id()
                scraped_item.resort_id = self.resort.id
                scraped_item.updated_at = updated_at
                self.db_session.add(scraped_item)

    def get_parser(self) -> Parser:
        """
        Construct and return an instance of a `Parser` based on the
        `parser_name` column in the database.
        """
        items = self.resort.parser_name.split(".")
        module_name, class_name = items[0], items[1]

        # Import the file in `webscraper/parsers/` that contains the implementation of the parser
        import_module(f"webscraper.parsers.{module_name}")

        # Find the class definition within the imported module
        ParserClass: Type[Parser] = getattr(  # pylint: disable=invalid-name
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

            db_lifts, scraped_lifts = self.get_lifts(), self.parser.get_lifts()
            db_trails, scraped_trails = self.get_trails(), self.parser.get_trails()

            self.add_or_update(db_lifts, scraped_lifts, now)
            self.add_or_update(db_trails, scraped_trails, now)

            self.resort.total_lifts = len(scraped_lifts)
            self.resort.open_lifts = len([l for l in scraped_lifts if l.is_open])

            self.resort.total_trails = len(scraped_trails)
            self.resort.open_trails = len([t for t in scraped_trails if t.is_open])
            self.resort.updated_at = now

        except Exception as exception:
            print_exception(exception)

    def examine_changes(self, item, changes: dict, updated_at: datetime) -> None:
        """Handle additional actions to be taken when specific columns are updated."""
        print("UPDATE: ", item.name, changes)
        is_open_change: Union[Tuple, None] = changes.get("is_open")
        if is_open_change:
            is_open = is_open_change[1]
            if is_open:
                item.last_opened_on = updated_at.date()
            else:
                item.last_closed_on = updated_at.date()

    def scrape_snow_report(self):
        """
        Scrape any/all information about the snow report.
        """

        try:
            # If there's a different URL for the snow report, navigate to that first.
            if (
                self.resort.snow_report_url
                and self.resort.snow_report_url != self.resort.trail_report_url
            ):
                self.browser.get(self.resort.snow_report_url)
                if self.resort.additional_wait_seconds:
                    print("Additional wait: ", self.resort.additional_wait_seconds)
                    sleep(self.resort.additional_wait_seconds)

            self.resort.snow_report = self.parser.parse_snow_report()

        except Exception as exception:
            print_exception(exception)


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
        webscraper.scrape_snow_report()
        session.commit()

    browser.close()


def scrape_resorts(query: Optional[Query] = None) -> None:
    """
    Carry out a webscrape for all resorts, or all resorts
    matching an optionally provided `Query`.
    """
    resort_query = query or select(Resort).where(
        or_(
            Resort.updated_at == None,  # pylint: disable=singleton-comparison
            Resort.updated_at < datetime.utcnow() - timedelta(minutes=10),
        )
    )

    with get_session() as session:

        def _scrape_trail_report(resort):
            browser = get_browser()
            webscraper = Webscraper(browser, resort)
            webscraper.scrape_trail_report()
            webscraper.scrape_snow_report()
            browser.close()
            session.commit()

        resorts: List[Resort] = session.execute(resort_query).scalars()
        with ThreadPoolExecutor(max_workers=1) as scrape_executor:
            for resort in resorts:
                scrape_executor.submit(_scrape_trail_report, resort)
