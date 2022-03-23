from datetime import datetime, timedelta
from typing import List, Optional

from dotenv import dotenv_values
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver

from sqlalchemy import select, or_
from sqlalchemy.orm import Query

from ski_resort import Resort
from postgres import get_session


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
        resort.scrape_trail_report(browser)
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
            resort.scrape_trail_report(browser)
            session.commit()

    browser.close()
