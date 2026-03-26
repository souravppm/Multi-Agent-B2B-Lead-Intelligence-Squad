import os
from tavily import TavilyClient
from firecrawl import FirecrawlApp
from dotenv import load_dotenv

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
firecrawl = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

def search_company_news(company_name):
    """Web search for recent news and tech stack."""
    query = f"recent business news and technology stack for {company_name} 2024 2025"
    return tavily.search(query=query, search_depth="advanced")

def scrape_website(url):
    """Scrape and clean website content into Markdown."""
    return firecrawl.scrape_url(url, params={'formats': ['markdown']})
