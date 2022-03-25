from datetime import datetime, timezone
import sys
from time import sleep
from traceback import print_exception
from typing import List

from nanoid import generate as generate_id
from selenium.webdriver.chrome.webdriver import WebDriver
from sqlalchemy import Boolean, Column, DateTime, Integer, String, ForeignKey, select
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.session import Session

import parsers
from util import get_key_value_pairs, get_changes

Base = declarative_base()


class Lift(Base):
    __tablename__ = 'lifts'
    id = Column(String, primary_key=True)
    resort_id = Column(ForeignKey('resorts.id'))
    name = Column(String)
    unique_name = Column(String)
    status = Column(String)
    is_open = Column(Boolean)
    updated_at = Column(DateTime)


class Trail(Base):
    __tablename__ = 'trails'
    id = Column(String, primary_key=True)
    resort_id = Column(ForeignKey('resorts.id'))
    name = Column(String)
    unique_name = Column(String)
    trail_type = Column(String)
    status = Column(String)
    is_open = Column(Boolean)
    groomed = Column(Boolean)
    night_skiing = Column(Boolean)
    updated_at = Column(DateTime)
    icon = Column(String)

    def __init__(self, *args, **kwargs):
        if kwargs.get('name') and kwargs.get('trail_type'):
            self.unique_name = f"{kwargs.get('name')}_{kwargs.get('trail_type')}"
        super().__init__(*args, **kwargs)


class Resort(Base):
    __tablename__ = 'resorts'
    id = Column(String, primary_key=True)
    name = Column(String)
    parser_name = Column(String)
    trail_report_url = Column(String)
    snow_report_url = Column(String)
    updated_at = Column(DateTime)
    additional_wait_seconds = Column(Integer)
    total_trails = Column(Integer)
    open_trails = Column(Integer)
    total_lifts = Column(Integer)
    open_lifts = Column(Integer)

    def add_or_update(self, db_rows: List, scraped_data: List, at: datetime) -> None:
        session: Session = Session.object_session(self)
        name_lookup = get_key_value_pairs(db_rows, key='unique_name')
        for scraped_item in scraped_data:
            item = name_lookup.get(scraped_item.unique_name)
            # If this item exists in the database, merge in any freshly-scraped data.
            if item:
                scraped_item.id = item.id
                session.merge(scraped_item)
                changes = get_changes(item)
                if changes:
                    print('UPDATE:', item.name, changes)
                    item.updated_at = at
            # Otherwise add a new item to the database that's tied to this resort.
            else:
                print('new item', scraped_item.name)
                scraped_item.id = generate_id()
                scraped_item.resort_id = self.id
                scraped_item.updated_at = at
                session.add(scraped_item)

    def get_parser(self, browser: WebDriver) -> 'parsers.Parser':
        """Construct and return an instance of a `Parser` based on the `parser_name` column in the database."""
        constructor = getattr(sys.modules['parsers'], self.parser_name)
        return constructor(browser)

    def get_lifts(self) -> List['Lift']:
        session: Session = Session.object_session(self)
        return session.execute(select(Lift).where(
            Lift.resort_id == self.id
        )).scalars()

    def get_trails(self) -> List['Trail']:
        session: Session = Session.object_session(self)
        return session.execute(select(Trail).where(
            Trail.resort_id == self.id
        )).scalars()

    def scrape_trail_report(self, browser: WebDriver):
        print(f'scraping {self.name}...')
        try:
            now = datetime.now(timezone.utc)
            browser.get(self.trail_report_url)
            print('Loaded', self.trail_report_url)
            if self.additional_wait_seconds:
                print('Additional wait: ', self.additional_wait_seconds)
                sleep(self.additional_wait_seconds)

            parser: 'parsers.Parser' = self.get_parser(browser)

            db_lifts, scraped_lifts = self.get_lifts(), parser.get_lifts()
            db_trails, scraped_trails = self.get_trails(), parser.get_trails()

            self.add_or_update(db_lifts, scraped_lifts, now)
            self.add_or_update(db_trails, scraped_trails, now)

            self.total_lifts = len(scraped_lifts)
            self.open_lifts = len([l for l in scraped_lifts if l.is_open])

            self.total_trails = len(scraped_trails)
            self.open_trails = len([t for t in scraped_trails if t.is_open])
            self.updated_at = now

        except Exception as e:
            print_exception(e)
