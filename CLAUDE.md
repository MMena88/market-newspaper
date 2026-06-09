# CLAUDE.md

## Project Name
Daily Market Newspaper

## Main Goal
Build a project that automatically creates a short daily market newspaper every day at **8:00 AM Eastern Time**.

The output should be either:

1. A webpage that updates daily, or
2. A daily generated file, preferably Markdown or HTML.

The newspaper must give a short, clear analysis of the market condition for that day.

---

## Important Rule About Timezone
Use the timezone:

```txt
America/New_York
```

Do not hardcode only `EST`, because Eastern Time changes between EST and EDT depending on daylight saving time.

The daily report must run at:

```txt
8:00 AM America/New_York
```

---

## Rules Claude Must Follow Before Creating the Project

Before writing code, Claude must do the following:

1. Confirm the project structure.
2. Choose the simplest reliable architecture.
3. Explain how the daily automation will run.
4. Identify the data sources that will be used.
5. Make sure API keys are never hardcoded.
6. Use environment variables for all secrets.
7. Make sure the report can still be generated even if one data source fails.
8. Add error handling and logs.
9. Keep the design simple, clean, and easy to maintain.
10. Add clear setup instructions in the README.

Claude should not overcomplicate the project unless it is necessary.

---

## Recommended Project Architecture

Claude should create one of these options:

### Option A: Static Website + Scheduled Generator

Recommended stack:

```txt
Python
Markdown or HTML
GitHub Actions cron
Static website hosting
```

The scheduled task should:

1. Run every day at 8:00 AM America/New_York.
2. Fetch market data.
3. Generate the daily newspaper.
4. Save the report as an HTML or Markdown file.
5. Update the homepage with the latest report.
6. Commit the new report automatically if using GitHub Actions.

### Option B: Web App With Cron Job

Recommended stack:

```txt
Next.js or Flask
Scheduled cron job
Database or file storage
```

This is better if the project needs a dashboard, login, archive search, or more advanced features.

For the first version, Claude should prefer **Option A** unless told otherwise.

---

## Required Daily Newspaper Sections

Each daily report must include these sections:

```md
# Daily Market Newspaper

## Date
Use the current date in America/New_York.

## Market Snapshot
Briefly summarize the general market mood.

## Equity Market
Mention the condition of major U.S. indexes or futures, such as:
- S&P 500
- Nasdaq
- Dow Jones

## Crypto Market
Mention the condition of:
- Bitcoin
- Ethereum
- General crypto sentiment

## Commodities
Mention important movement in:
- Gold
- Oil

## Forex / Dollar
Mention the condition of:
- U.S. Dollar Index, if available
- Major FX sentiment, if relevant

## Bonds / Yields
Mention U.S. Treasury yield movement if available.

## Key News or Macro Events
Mention important scheduled or recent events that may affect the market, such as:
- CPI
- PPI
- Federal Reserve comments
- Jobs data
- Earnings reports
- Geopolitical risk

## Short Market Analysis
Give a professional but concise interpretation of the market condition.

The analysis should answer:
- Is the market risk-on, risk-off, or neutral?
- What is driving the market today?
- What should traders or investors watch during the session?

## Important Levels to Watch
Mention relevant support and resistance levels only if reliable data is available.

## Disclaimer
This is not financial advice. The report is for informational and educational purposes only.
```

---

## Writing Style Rules

The daily market analysis must be:

- Professional
- Short
- Clear
- Easy to read
- Neutral
- Data-driven
- Not exaggerated
- Not promotional

Avoid phrases like:

```txt
Guaranteed move
Sure profit
Risk-free trade
100% bullish
100% bearish
```

Use careful language such as:

```txt
The market appears...
This may suggest...
Traders may be watching...
The tone is currently...
A break above/below could indicate...
```

---

## Data Source Rules

Claude must use reliable data sources.

Possible sources include:

- Yahoo Finance
- Alpha Vantage
- Finnhub
- Polygon.io
- Twelve Data
- CoinGecko
- CoinMarketCap
- Federal Reserve Economic Data
- Economic calendar APIs
- Official government data sources

Claude must not scrape websites aggressively or violate website terms.

If API keys are needed, Claude must create a `.env.example` file like this:

```env
ALPHA_VANTAGE_API_KEY=
FINNHUB_API_KEY=
POLYGON_API_KEY=
NEWS_API_KEY=
```

Actual API keys must never be committed.

---

## Automation Rules

Claude must implement a daily scheduler.

If using GitHub Actions, create a workflow similar to:

```yml
name: Generate Daily Market Newspaper

on:
  schedule:
    - cron: "0 13 * * *"
  workflow_dispatch:

jobs:
  generate-report:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Generate report
        run: python scripts/generate_report.py

      - name: Commit daily report
        run: |
          git config user.name "github-actions"
          git config user.email "github-actions@github.com"
          git add .
          git commit -m "Add daily market newspaper" || echo "No changes to commit"
          git push
```

Important note:

```txt
13:00 UTC equals 8:00 AM Eastern Standard Time.
During daylight saving time, 8:00 AM New York time equals 12:00 UTC.
```

Because GitHub Actions cron uses UTC, Claude must handle daylight saving time correctly.

Preferred approach:

1. Run the GitHub Action hourly or around both possible UTC times.
2. Inside the script, check if the current time in America/New_York is 8:00 AM.
3. Generate the report only when it is actually 8:00 AM New York time.

This avoids problems with EST vs EDT.

---

## Suggested Folder Structure

Claude should create a clean project structure like this:

```txt
daily-market-newspaper/
│
├── CLAUDE.md
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── scripts/
│   ├── generate_report.py
│   ├── fetch_market_data.py
│   ├── analyze_market.py
│   └── render_report.py
│
├── reports/
│   └── YYYY-MM-DD.md
│
├── public/
│   ├── index.html
│   └── reports/
│
└── .github/
    └── workflows/
        └── daily-report.yml
```

---

## Functional Requirements

The project must be able to:

1. Generate a new daily report.
2. Save reports by date.
3. Keep an archive of previous reports.
4. Update the homepage with the newest report.
5. Include timestamps.
6. Handle missing data gracefully.
7. Log errors without crashing unnecessarily.
8. Run manually for testing.
9. Run automatically at the scheduled time.
10. Include a disclaimer.

---

## Report Generation Logic

Claude should design the generation process like this:

```txt
Start
↓
Check current time in America/New_York
↓
If current hour is not 8 AM, exit safely
↓
Fetch market data
↓
Fetch macro/news data if available
↓
Clean and validate data
↓
Generate short analysis
↓
Render Markdown or HTML report
↓
Save report with date
↓
Update homepage
↓
Log success or errors
End
```

---

## Market Analysis Rules

The market analysis should consider:

- Index direction
- Futures direction
- Bitcoin and Ethereum movement
- Gold and oil movement
- U.S. dollar strength or weakness
- Treasury yields
- Important economic events
- Major news catalysts
- Market volatility if available

The analysis should classify the market tone as one of:

```txt
Risk-on
Risk-off
Neutral
Mixed
```

Example logic:

```txt
If equities are up, crypto is up, yields are stable, and the dollar is weak, tone may be Risk-on.

If equities are down, crypto is down, gold is up, yields are moving sharply, and the dollar is strong, tone may be Risk-off.

If signals are conflicting, tone may be Mixed or Neutral.
```

---

## Important Development Rules

Claude must:

1. Write clean and readable code.
2. Use functions, not one giant script.
3. Include comments only where helpful.
4. Avoid unnecessary dependencies.
5. Add a `README.md` with setup and run instructions.
6. Add a `.gitignore`.
7. Add a `.env.example`.
8. Avoid committing generated secrets.
9. Make the project easy to deploy.
10. Test the report generation manually.

---

## README Must Include

The README must explain:

1. What the project does.
2. How to install dependencies.
3. How to add API keys.
4. How to run the report manually.
5. How the scheduled automation works.
6. Where reports are saved.
7. How to deploy the webpage.
8. How to troubleshoot errors.

---

## Manual Run Command

Claude should include a command like:

```bash
python scripts/generate_report.py
```

There should also be a test mode, for example:

```bash
python scripts/generate_report.py --force
```

The `--force` option should generate a report even if it is not 8:00 AM New York time.

---

## Quality Checklist Before Finishing

Before Claude says the project is complete, Claude must verify:

- The project runs without syntax errors.
- The scheduler file exists.
- The report generator exists.
- The homepage is generated or updated.
- The report archive works.
- The `.env.example` file exists.
- The README has clear instructions.
- No API keys are included in the repository.
- The generated report includes a disclaimer.
- The timezone is handled correctly.

---

## Final Instruction to Claude

Build the first version as simple and functional.

Prioritize:

1. Reliability
2. Clear daily output
3. Correct timezone handling
4. Clean structure
5. Easy deployment

Do not add unnecessary complexity in version one.
