import datetime
import lxml.html
from billy.utils.fulltext import text_after_line_numbers
from .bills import MABillScraper
from .legislators import MALegislatorScraper
from .committees import MACommitteeScraper
from .events import MAEventScraper

settings = dict(
    SCRAPELIB_TIMEOUT=600,
    SCRAPELIB_RPM=30
)

metadata = {
    'capitol_timezone': 'America/New_York',
    'terms': [
        {
            'end_year': 2010,
            'start_year': 2009,
            'name': '186',
            'sessions': [ '186th' ]
        },
        {
            'end_year': 2012,
            'start_year': 2011,
            'name': '187',
            'sessions': [ '187th' ]
        },
        {
            'end_year': 2013,
            'start_year': 2014,
            'name': '188',
            'sessions': [ '188th' ]
        }
    ],
    'name': 'Massachusetts',
    'abbreviation': 'ma',
    'legislature_url': "http://www.malegislature.gov/",
    'session_details': {
        '186th': {
            'type': 'primary',
            'display_name': '186th Legislature (2009-2010)',
            '_scraped_name': '186th',
        },
        '187th': {
            'type': 'primary',
            'display_name': '187th Legislature (2011-2012)',
            '_scraped_name': '187th',
        },
        '188th': {
            'type': 'primary',
            'display_name': '188th Legislature (2013-2014)',
            '_scraped_name': '188th',
        }
    },
    'legislature_name': 'Massachusetts General Court',
    'chambers': {
        'upper': {'name': 'Senate', 'title': 'Senator'},
        'lower': {'name': 'House', 'title': 'Representative'},
    },
    'feature_flags': ['events', 'influenceexplorer'],
}

def session_list():
    import re
    from billy.scrape.utils import url_xpath
    sessions = url_xpath('http://www.malegislature.gov/Bills/Search',
        "//select[@id='Input_GeneralCourtId']/option/text()")
    # Ok, this is actually a mess. Let's clean it up.
    # sessions.remove('--Select Value--')  # They removed this.
    sessions = [ re.sub("\(.*$", "", session).strip() for session in sessions ]
    return sessions


def extract_text(doc, data):
    doc = lxml.html.fromstring(data)
    text = ' '.join([x.text_content()
                     for x in doc.xpath('//td[@class="longTextContent"]//p')])
    return text
