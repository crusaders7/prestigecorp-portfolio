#!/usr/bin/env python3
"""
End-to-end test of the improved Illawarra Mercury scraper
"""

from scrape import handler as ScrapeHandler
from search import handler as SearchHandler
import json
import sys
import os
import requests
from bs4 import BeautifulSoup

# Add the parent directory to the Python path so we can import the modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_search_function(query, max_results=10):
    """Test the search functionality directly"""
    print(f"Testing search for: {query}")

    try:
        # Create a search handler instance
        search_handler = SearchHandler()

        # Call the search method directly
        urls = search_handler.search_illawarra_mercury(query, max_results)

        print(f"Search found {len(urls)} results")
        for i, url in enumerate(urls[:5], 1):
            print(f"  {i}. {url}")

        return urls

    except Exception as e:
        print(f"Search test failed: {e}")
        return []


def test_scrape_function(urls, query=""):
    """Test the scraping functionality directly"""
    if not urls:
        print("No URLs to scrape")
        return []

    print(f"\nTesting scrape for {len(urls)} URLs...")

    articles = []
    errors = []

    # Create a scrape handler instance
    scrape_handler = ScrapeHandler()

    # Test with first 3 URLs
    for i, url in enumerate(urls[:3], 1):
        print(f"\nScraping article {i}: {url}")

        try:
            article_data = scrape_handler.extract_article_data(url, query)

            if article_data:
                articles.append(article_data)
                print(f"  ✅ Success: {article_data.get('title', 'No title')}")
                print(
                    f"  Content length: {len(article_data.get('content', ''))} characters")
                if article_data.get('content'):
                    preview = article_data['content'][:150] + "..." if len(
                        article_data['content']) > 150 else article_data['content']
                    print(f"  Preview: {preview}")
            else:
                errors.append(f"Failed to extract data from {url}")
                print(f"  ❌ Failed to extract data")

        except Exception as e:
            errors.append(f"Error scraping {url}: {str(e)}")
            print(f"  ❌ Error: {e}")

    print(f"\nSummary: {len(articles)} successful, {len(errors)} failed")
    return articles


def main():
    print("=" * 60)
    print("END-TO-END TEST: Illawarra Mercury Scraper")
    print("=" * 60)

    # Test search
    urls = test_search_function("shellharbour council")

    if urls:
        # Test scraping
        articles = test_scrape_function(urls, "shellharbour council")

        if articles:
            print(f"\n✅ SUCCESS: Found and scraped {len(articles)} articles!")
            print("\nThe Illawarra Mercury scraper is working correctly.")

            # Show summary of scraped articles
            print("\n" + "=" * 40)
            print("SCRAPED ARTICLES SUMMARY:")
            print("=" * 40)

            for i, article in enumerate(articles, 1):
                print(f"\nArticle {i}:")
                print(f"  Title: {article.get('title', 'No title')}")
                print(f"  Author: {article.get('author', 'No author')}")
                print(f"  Date: {article.get('date', 'No date')}")
                print(f"  URL: {article.get('url', 'No URL')}")
                print(
                    f"  Content: {len(article.get('content', ''))} characters")
        else:
            print(f"\n❌ FAILED: Could not scrape any articles")
    else:
        print(f"\n❌ FAILED: Could not find any articles")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
