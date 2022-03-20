from datetime import datetime, timedelta
from typing import List, Optional

from selenium.webdriver import Chrome
from sqlalchemy import select, or_
from sqlalchemy.orm import Query

from ski_resort import Resort
from postgres import get_session


def scrape_resorts(query: Optional[Query] = None) -> None:
    resort_query = query or select(Resort).where(
        or_(
            Resort.updated_at == None,
            Resort.updated_at < datetime.now() - timedelta(minutes=30)
        )
    )

    browser = Chrome()
    with get_session() as session:
        resorts: List[Resort] = session.execute(resort_query).scalars()
        for resort in resorts:
            resort.scrape_trail_report(browser)
        session.commit()
    browser.close()
