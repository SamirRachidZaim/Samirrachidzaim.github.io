Manual updates: Google Scholar counts

Automatic fetching has been disabled due to reliability and blocking issues with Google Scholar.

To update citation metrics manually, edit the `assets/scholar.json` file and commit the change. The website reads this file on load and will display the updated counts after deployment.

Example `assets/scholar.json`:

{
  "citations": 204,
  "hindex": 9,
  "i10": 9,
  "updated": "2026-01-21T00:00:00Z",
  "profile": "https://scholar.google.com/citations?user=_cxg7m4AAAAJ&hl=en"
}

How to update manually:

- Edit `assets/scholar.json` with the new numeric metrics and an ISO 8601 UTC timestamp in `updated`, for example `2026-02-03T12:00:00Z`.
- Commit and push:

  git add assets/scholar.json
  git commit -m "chore: manual update Google Scholar counts"
  git push

Notes:

- There is no official Google Scholar API and scraping from public CI runners was blocked (403). Manual updates remove that dependency.
- If you'd like automated, reliable updates later, consider using a self-hosted runner or a paid API (I can help implement either).