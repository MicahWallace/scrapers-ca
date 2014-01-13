from pupa.scrape import Scraper, Legislator

from utils import lxmlize, CONTACT_DETAIL_TYPE_MAP, CONTACT_DETAIL_NOTE_MAP

import re

COUNCIL_PAGE = 'http://www.wilmot.ca/current-council.php'


class WilmotPersonScraper(Scraper):

  def get_people(self):
    page = lxmlize(COUNCIL_PAGE)

    councillors = page.xpath('//table[@id="Main Content"]//td[@colspan="3"]//td/p/b')
    for councillor in councillors:
      district, name = councillor.xpath('./text()')[0].split(':')
      if 'Mayor' in district:
        yield scrape_mayor(councillor, name)
        continue

      p = Legislator(name=name, post_id=district)
      p.add_source(COUNCIL_PAGE)
      p.role = 'Councillor'

      base_info = councillor.xpath('./parent::p/text()')
      for info in councillor.xpath('./parent::p/following-sibling::p'):
        if info.xpath('.//b'):
          break
        base_info = base_info + info.xpath('./text()')

      address = ''
      complete = False
      while not complete:
        address = address + ' ' + base_info.pop(0)
        if re.search(r'[A-Z][0-9A-Z][A-Z] \d[A-Z]\d', address):
          complete = True
      p.add_contact('address', address, 'legislature')

      base_info.pop(-1)
      base_info = ' '.join(base_info).split()
      for i, contact in enumerate(base_info):
        if re.match(r'[0-9]', contact):
          continue
        if 'fax' in contact:
          p.add_contact('fax', base_info[i + 1], 'legislature')
        else:
          p.add_contact(CONTACT_DETAIL_TYPE_MAP[contact.strip()], base_info[i + 1], CONTACT_DETAIL_NOTE_MAP[contact.strip()])
      email = councillor.xpath('./parent::p/following-sibling::p/a[contains(@href, "mailto")]/text()')[0]
      p.add_contact('email', email, None)
      yield p


def scrape_mayor(div, name):

  p = Legislator(name=name, post_id='wilmont')
  p.add_source(COUNCIL_PAGE)
  p.role = 'Mayor'

  info = div.xpath('./parent::p//text()')
  info.pop(0)
  address = ' '.join(info[:3])
  phone = info[3].split()[1]
  fax = info[4].split()[1]
  email = info[-1]
  p.add_contact('address', address, 'legislature')
  p.add_contact('voice', phone, 'legislature')
  p.add_contact('fax', fax, 'legislature')
  p.add_contact('email', email, None)
  return p
