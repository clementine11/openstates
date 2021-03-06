import re

from billy.scrape import NoDataForPeriod
from billy.scrape.legislators import LegislatorScraper, Legislator

import scrapelib
import lxml.html


def xpath_one(el, expr):
    ret = el.xpath(expr)
    if len(ret) != 1:
        print ret
        raise Exception
    return ret[0]


class LALegislatorScraper(LegislatorScraper):
    jurisdiction = 'la'
    latest_only = True

    def lxmlize(self, url):
        page = self.urlopen(url)
        page = lxml.html.fromstring(page)
        page.make_links_absolute(url)
        return page

    def scrape_upper(self, chamber, term):
        pass

    def scrape_lower_legislator(self, url, leg_info, term):
        page = self.lxmlize(url)
        photo = xpath_one(page, '//img[@rel="lightbox"]').attrib['src']
        infoblk = xpath_one(page,
                         '//font/b[contains(text(), "CAUCUS MEMBERSHIP")]')
        infoblk = infoblk.getparent()
        info = infoblk.text_content()
        cty = xpath_one(infoblk, "./b[contains(text(), 'ASSIGNMENTS')]")
        cty = cty.getnext()

        party_flags = {
            "Democratic": "Democratic",
            "Republican": "Republican"
        }

        party = 'other'
        for p in party_flags:
            if p in info:
                party = party_flags[p]

        kwargs = {"url": url,
                  "party": party,
                  "photo_url": photo}

        leg = Legislator(term,
                         'lower',
                         leg_info['dist'],
                         leg_info['name'],
                         email=leg_info['email'],
                         **kwargs)

        kwargs = {
            "address": leg_info['office'],
            "phone": leg_info['phone'],
        }

        if leg_info['email'] != "":
            kwargs['email'] = leg_info['email']

        leg.add_office('district',
                       'District Office',
                       **kwargs)


        leg.add_source(url)
        self.save_legislator(leg)

    def scrape_lower(self, chamber, term):
        url = "http://house.louisiana.gov/H_Reps/H_Reps_FullInfo.asp"
        page = self.lxmlize(url)
        meta = ["name", "dist", "office", "phone", "email"]
        for tr in page.xpath("//table[@id='table61']//tr"):
            tds = tr.xpath("./td")
            if tds == []:
                continue

            info = {}
            for i in range(0, len(meta)):
                info[meta[i]] = tds[i].text_content().strip()

            hrp = tr.xpath(
                ".//a[contains(@href, 'H_Reps')]")[0].attrib['href']

            self.scrape_lower_legislator(hrp, info, term)

    def scrape(self, chamber, term):
        if chamber == "upper":
            return self.scrape_upper(chamber, term)
        elif chamber == "lower":
            return self.scrape_lower(chamber, term)
