Setup: automatic Google Scholar counts

1) Add your Google Scholar user id as a GitHub repository secret:
   - Name: `SCHOLAR_USER_ID`
   - Value: the id in your profile URL (e.g. `_cxg7m4AAAAJ`)

2) The workflow runs daily (08:00 UTC) and commits `assets/scholar.json` with the latest counts.

3) The site reads `assets/scholar.json` and updates the citation counts automatically.

Notes and caveats

- There is no official Google Scholar API. This solution scrapes your Scholar profile page once per day.
- Scraping Google Scholar may violate their terms and may result in blocking; keep the frequency low and monitor failures.
- If you prefer not to scrape, you can run the script locally and commit `assets/scholar.json` manually, or host a trusted server that fetches counts and exposes them as JSON.

If you want, I can: add a badge (image), change frequency, or switch to a different fetch method (e.g., server with proxy).