from datetime import datetime
import sys
from typing import List

from nanoid import generate as generate_id
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from sqlalchemy import Boolean, Column, DateTime, String, ForeignKey, select
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.session import Session

import parsers
from util import get_name_to_id, Settable, get_name_to_self

Base = declarative_base()


class Lift(Base):
    __tablename__ = 'lifts'
    id = Column(String, primary_key=True)
    resort_id = Column(ForeignKey('resorts.id'))
    name = Column(String)
    status = Column(String)


class Trail(Base):
    __tablename__ = 'trails'
    id = Column(String, primary_key=True)
    resort_id = Column(ForeignKey('resorts.id'))
    name = Column(String)
    trail_type = Column(String)
    status = Column(String)
    groomed = Column(Boolean)
    night_skiing = Column(Boolean)


class Resort(Base):
    __tablename__ = 'resorts'
    id = Column(String, primary_key=True)
    name = Column(String)
    parser_name = Column(String)
    lifts_container_css_selector = Column(String)
    lift_css_selector = Column(String)
    trails_container_css_selector = Column(String)
    trail_css_selector = Column(String)
    trail_report_url = Column(String)
    snow_report_url = Column(String)
    updated_at = Column(DateTime)

    def get_parser(self, browser: WebDriver) -> 'parsers.Parser':
        """Construct and return an instance of a `Parser` based on the `parser_name` column in the database."""
        css_selectors = filter(lambda column_name: 'css_selector' in column_name
                               and getattr(self, column_name) is not None,
                               self.__dict__.keys())
        parser_args = {}
        for selector in css_selectors:
            print(selector)
            parser_args[selector] = getattr(self, selector)
        print(parser_args)
        constructor = getattr(sys.modules['parsers'], self.parser_name)
        return constructor(browser, **parser_args)

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
        session: Session = Session.object_session(self)

        browser.get(self.trail_report_url)
        parser: 'parsers.Parser' = self.get_parser(browser)

        lift_db_rows = self.get_lifts()
        trail_db_rows = self.get_trails()
        lift_name_to_self = get_name_to_self(lift_db_rows)
        trail_name_to_self = get_name_to_self(trail_db_rows)

        scraped_lift_data = parser.get_lifts()
        for scraped_lift in scraped_lift_data:
            lift = lift_name_to_self.get(scraped_lift.name)
            if lift:
                lift.status = scraped_lift.status
            else:
                print('new lift', scraped_lift.name)
                session.add(Lift(
                    id=generate_id(),
                    resort_id=self.id,
                    name=scraped_lift.name,
                    status=scraped_lift.status
                ))

        scraped_trail_data = parser.get_trails()
        for scraped_trail in scraped_trail_data:
            trail = trail_name_to_self.get(scraped_trail.name)
            if trail:
                trail.status = scraped_trail.status
            else:
                print('new trail', scraped_trail.name)
                session.add(Trail(
                    id=generate_id(),
                    resort_id=self.id,
                    name=scraped_trail.name,
                    trail_type=scraped_trail.trail_type,
                    status=scraped_trail.status,
                    groomed=scraped_trail.groomed,
                    night_skiing=scraped_trail.night_skiing
                ))
        self.updated_at = datetime.now()


# def add_or_update(new_data: Settable, existing_key_value_pairs: dict):
