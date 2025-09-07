# PrestigeCorp Portfolio

This repository contains multiple applications and tools developed for PrestigeCorp.

## Repository Structure

```
repo/
├── api/                  # Shared backend utilities
├── apps/                 # Individual deployable apps
│   ├── fresh-news/       # News scraping and search application
│   ├── site-audit/       # Website auditing tool
│   └── newspaper-scraper/ # Advanced newspaper scraping system
├── tests/                # All test scripts together
├── docs/                 # Deployment and fix documentation
├── requirements.txt      # Pinned versions for the whole project
└── README.md             # This file
```

## Applications

### Fresh News (`apps/fresh-news`)
A news scraping and search application using Google Custom Search Engine.

### Site Audit (`apps/site-audit`)
A tool for auditing websites and analyzing their structure.

### Newspaper Scraper (`apps/newspaper-scraper`)
An advanced system for scraping newspaper content with multiple strategies.

## Dependencies

All dependencies are managed through `requirements.txt`. To install:

```bash
pip install -r requirements.txt
```

## Deployment

Each application in the `apps/` directory can be deployed independently, primarily to Vercel.