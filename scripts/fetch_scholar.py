#!/usr/bin/env python3
"""
Simple scraper for Google Scholar profile summary metrics (citations, h-index, i10-index).
Usage: python scripts/fetch_scholar.py --user USERID --output assets/scholar.json

Note: Scraping Google Scholar may violate their terms of service and may result in blocking. Use a low frequency (daily) and your own profile ID.
"""

import argparse
import json
import sys
from datetime import datetime

import requests
from bs4 import BeautifulSoup


def fetch_profile(user_id, timeout=30):
    url = f"https://scholar.google.com/citations?user={user_id}&hl=en"
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; GitHubAction/1.0; +https://github.com)'
    }
    r = requests.get(url, headers=headers, timeout=timeout)
    r.raise_for_status()
    return r.text, url


def parse_metrics(html):
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', id='gsc_rsb_st')
    if not table:
        raise ValueError('Metrics table not found in Scholar page')
    rows = table.find_all('tr')
    def val_from_row(i):
        tds = rows[i].find_all('td')
        return tds[1].text.strip().replace(',', '')
    citations = int(val_from_row(0))
    hindex = int(val_from_row(1))
    i10 = int(val_from_row(2))
    return citations, hindex, i10


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--user', required=True, help='Google Scholar user id (e.g. _cxg7m4AAAAJ)')
    p.add_argument('--output', default='assets/scholar.json', help='Output JSON file path')
    args = p.parse_args()

    try:
        html, profile_url = fetch_profile(args.user)
        citations, hindex, i10 = parse_metrics(html)
    except Exception as e:
        print('Error fetching or parsing Google Scholar profile:', e, file=sys.stderr)
        sys.exit(1)

    payload = {
        'citations': citations,
        'hindex': hindex,
        'i10': i10,
        'updated': datetime.utcnow().isoformat() + 'Z',
        'profile': f'https://scholar.google.com/citations?user={args.user}&hl=en'
    }

    with open(args.output, 'w', encoding='utf-8') as fh:
        json.dump(payload, fh, indent=2)

    print('Wrote', args.output)


if __name__ == '__main__':
    main()
