from __future__ import unicode_literals
from utils import CanadianScraper, CanadianPerson as Person

import re

COUNCIL_PAGE = 'http://app.toronto.ca/im/council/councillors.jsp'
BROKEN_LINKS = ['http://www.toronto.ca/councillors/vaughan1.htm',
                'http://www.toronto.ca/councillors/milczyn1.htm']


class TorontoPersonScraper(CanadianScraper):

    def scrape(self):
        page = self.lxmlize(COUNCIL_PAGE)

        a = page.xpath('//a[contains(@href,"mayor")]')[0]
        yield self.scrape_mayor(a.attrib['href'])

        for a in page.xpath('//a[contains(@href,"councillors/")]'):
            page = lxmlize(a.attrib['href'])
            h1 = page.xpath('string(//h1)')
            if 'Council seat is vacant' not in h1 and a.attrib['href'] not in BROKEN_LINKS:
                yield self.scrape_councilor(page, h1, a.attrib['href'])

    def scrape_councilor(self, page, h1, url):
        name = h1.split('Councillor')[1]
        ward_full = page.xpath('string(//a/descendant-or-self::*[contains(text(), "Profile:")])').replace('\xa0', ' ')
        ward_num, ward_name = re.search(r'(Ward \d+) (.+)', ward_full).groups()

        p = Person(primary_org='legislature', name=name, district=ward_num, role='Councillor')
        p.add_source(COUNCIL_PAGE)
        p.add_source(url)

        p.image = page.xpath('string(//main//img/@src)').replace('www.', 'www1.')  # @todo fix lxmlize to use the redirected URL to make links absolute
        email = page.xpath('string((//a[contains(@href, "@")])[1])')
        p.add_contact('email', email)

        addr_cell = page.xpath('//*[contains(text(), "Toronto City Hall")]/'
                               'ancestor::td')[0]
        phone = (addr_cell.xpath('string((.//text()[contains(., "Phone:")])[1])')
                          .split(':')[1])
        p.add_contact('voice', phone, 'legislature')

        address = '\n'.join(addr_cell.xpath('./p[2]/text()')[:2])
        if address:
            p.add_contact('address', address, 'legislature')

        return p

    def scrape_mayor(self, url):
        page = self.lxmlize(url)
        name = page.xpath("//h1/text()")[0].replace("Toronto Mayor", "").strip()

        p = Person(primary_org='legislature', name=name, district="Toronto", role='Mayor')
        p.add_source(COUNCIL_PAGE)
        p.add_source(url)

        p.image = page.xpath('string(//article/img/@src)').replace('www.', 'www1.')

        url = page.xpath('//a[contains(text(), "Contact the Mayor")]')[0].attrib['href'].replace('www.', 'www1.')
        p.add_source(url)
        page = self.lxmlize(url)

        mail_elem, phone_elem = page.xpath('//h3')[:2]
        address = ''.join(mail_elem.xpath('./following-sibling::p//text()'))
        phone = phone_elem.xpath('string(./following-sibling::p[1])')

        p.add_contact('address', address, 'legislature')
        p.add_contact('voice', phone, 'legislature')
        return p
