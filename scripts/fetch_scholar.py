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
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import re
import time
import os


def fetch_profile(user_id, timeout=30, retries=3, backoff_factor=0.3):
    """Fetch the Scholar profile page using a requests Session with retries.

    Raises ValueError with helpful messages when the user id is empty or when Google blocks the request.
    """
    if not user_id:
        raise ValueError('Google Scholar user id is empty')

    url = f"https://scholar.google.com/citations?user={user_id}&hl=en"

    # Use a realistic desktop browser User-Agent to reduce the chance of blocking
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://scholar.google.com/'
    }

    session = requests.Session()
    retry = Retry(total=retries, backoff_factor=backoff_factor, status_forcelist=(429, 500, 502, 503, 504), allowed_methods=['GET'])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    session.headers.update(headers)

    try:
        r = session.get(url, timeout=timeout)
    except requests.RequestException as e:
        raise ValueError(f'Network error fetching Google Scholar profile: {e}')

    # Detect common blocking responses
    text = r.text.lower()
    if r.status_code == 403 or 'captcha' in text or 'unusual traffic' in text or 'our systems have detected' in text:
        raise ValueError(f'Access blocked when fetching Google Scholar profile (status={r.status_code}). This may indicate running from an IP that Google is blocking or the profile id is invalid. url={url}')

    r.raise_for_status()
    return r.text, url

# --
# Validate CLI args early so runs fail with a clear message when the secret is missing or empty
# --

def parse_metrics(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Primary method: table with id 'gsc_rsb_st'
    table = soup.find('table', id='gsc_rsb_st')
    if table:
        rows = table.find_all('tr')
        def val_from_row(i):
            tds = rows[i].find_all('td')
            return tds[1].text.strip().replace(',', '')
        citations = int(val_from_row(0))
        hindex = int(val_from_row(1))
        i10 = int(val_from_row(2))
        return citations, hindex, i10

    # Fallback: elements with class 'gsc_rsb_std'
    stds = soup.find_all(class_='gsc_rsb_std')
    if stds and len(stds) >= 3:
        try:
            vals = [int(s.get_text(strip=True).replace(',', '')) for s in stds[:3]]
            return vals[0], vals[1], vals[2]
        except Exception:
            pass

    # Detect blocking / captcha text for clearer error messages
    text = soup.get_text(separator=' ').lower()
    if 'unusual traffic' in text or 'our systems have detected' in text or 'captcha' in text:
        snippet = text[:500]
        raise ValueError(f'Blocked by Google Scholar or CAPTCHA detected: {snippet!r}')

    # Last resort: regex search for labels followed by numbers
    def find_num(label_variants):
        for label in label_variants:
            m = re.search(rf'{label}[^0-9\n]*([0-9,]+)', html, re.I)
            if m:
                return int(m.group(1).replace(',', ''))
        return None

    citations = find_num(['Citations', 'Cited by'])
    hindex = find_num(['h-index', 'h index'])
    i10 = find_num(['i10-index', 'i10 index', 'i10'])

    if citations is not None and hindex is not None and i10 is not None:
        return citations, hindex, i10

    # If we get here, parsing failed
    raise ValueError('Metrics table not found in Scholar page; fetched page does not contain expected metrics.')

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--user', required=True, help='Google Scholar user id (e.g. _cxg7m4AAAAJ)')
    p.add_argument('--output', default='assets/scholar.json', help='Output JSON file path')
    p.add_argument('--save-debug', action='store_true', help='Save fetched HTML to a debug file on error')
    args = p.parse_args()

    if not args.user:
        print('Error: --user argument is empty. Set the SCHOLAR_USER_ID secret in GitHub Actions or pass --user USERID.', file=sys.stderr)
        sys.exit(2)

    try:
        html, profile_url = fetch_profile(args.user)
        citations, hindex, i10 = parse_metrics(html)
    except Exception as e:
        # Save HTML for debugging when requested
        if 'html' in locals() and args.save_debug:
            debug_path = args.output + '.debug.html'
            try:
                os.makedirs(os.path.dirname(debug_path), exist_ok=True)
                with open(debug_path, 'w', encoding='utf-8') as fh:
                    fh.write(html)
                print(f'Wrote debug HTML to {debug_path}', file=sys.stderr)
            except Exception as ew:
                print('Failed writing debug HTML:', ew, file=sys.stderr)
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
