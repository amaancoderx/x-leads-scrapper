from crewai import Agent, Crew, Task
from crewai.tools import tool
from logging_config import get_logger
from pydantic import BaseModel, Field
from typing import List, Dict
import os
import requests
import re

class Lead(BaseModel):
    """Model for a Cardano lead"""
    name: str = Field(description="Name of the person or project")
    username: str = Field(description="Twitter/X username")
    handle: str = Field(description="Full Twitter/X URL")
    description: str = Field(description="Brief description of the lead")
    followers: str = Field(description="Follower count or 'N/A'")

class LeadsList(BaseModel):
    """List of Cardano leads"""
    leads: List[Lead] = Field(description="List of Cardano-related leads")

def extract_username_from_url(url: str) -> str:
    """Extract X.com username from URL"""
    if not url:
        return ""
    m = re.search(r'x\.com\/([^\/\?\#]+)', url, re.IGNORECASE)
    if m:
        username = m.group(1)
        if username.lower() not in ['home', 'explore', 'notifications', 'messages', 'search', 'i']:
            return username
    return ""

def parse_followers(text) -> str:
    """Convert follower strings to readable format"""
    if text is None:
        return "N/A"
    return str(text)

def run_apify_search(topic: str, apify_token: str, max_pages: int = 1) -> List[Dict]:
    """Run Apify Google search for Cardano leads"""
    APIFY_RUN_SYNC_URL = "https://api.apify.com/v2/acts/apify~google-search-scraper/run-sync-get-dataset-items"
    headers = {"Content-Type": "application/json"}
    params = {"token": apify_token}
    queries_field = f"site:x.com {topic} cardano"

    payload = {
        "focusOnPaidAds": False,
        "forceExactMatch": False,
        "includeIcons": False,
        "includeUnfilteredResults": False,
        "maxPagesPerQuery": max_pages,
        "mobileResults": False,
        "queries": queries_field,
        "resultsPerPage": 100,
        "saveHtml": False,
        "saveHtmlToKeyValueStore": True,
    }

    resp = requests.post(APIFY_RUN_SYNC_URL, params=params, json=payload, headers=headers, timeout=120)
    resp.raise_for_status()
    data = resp.json()

    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "items" in data:
        return data["items"]
    return []

def parse_apify_items(items: List[Dict]) -> List[Dict]:
    """Parse Apify results into lead format"""
    leads = []
    for item in items:
        json_obj = item.get("json") if isinstance(item, dict) and "json" in item else item
        organic = []

        if isinstance(json_obj, dict):
            if "organicResults" in json_obj:
                organic = json_obj["organicResults"]
            elif "results" in json_obj:
                organic = json_obj["results"]

        if not organic:
            continue

        for r in organic:
            name = r.get("title") or ""
            url = r.get("url") or r.get("link") or ""
            username = extract_username_from_url(url)
            description = r.get("description") or r.get("snippet") or ""
            followers_raw = r.get("followersAmount") or r.get("followers") or ""
            followers = parse_followers(followers_raw)

            leads.append({
                "name": name,
                "username": username,
                "handle": url,
                "description": description,
                "followers": followers
            })
    return leads

@tool("search_cardano_leads")
def search_cardano_leads(topic: str) -> List[Dict]:
    """Search for Cardano-related leads on X.com for a given topic using Apify.

    Args:
        topic: The topic to search for (e.g., 'developers', 'NFT artists', 'projects')

    Returns:
        List of leads with name, username, handle, description, followers
    """
    apify_token = os.getenv("APIFY_TOKEN")
    if not apify_token:
        return []

    try:
        items = run_apify_search(topic, apify_token, max_pages=1)
        leads = parse_apify_items(items)
        return leads
    except Exception as e:
        print(f"Error searching for leads: {e}")
        return []

class ResearchCrew:
    def __init__(self, verbose=True, logger=None):
        self.verbose = verbose
        self.logger = logger or get_logger(__name__)
        self.logger.info("ResearchCrew initialized")

    def kickoff(self, inputs: dict):
        """Execute the search directly using Apify without AI agents"""
        topic = inputs.get("text", "")
        self.logger.info(f"Searching for Cardano {topic} leads via Apify")

        apify_token = os.getenv("APIFY_TOKEN")
        if not apify_token:
            self.logger.error("APIFY_TOKEN not found in environment")
            return LeadsList(leads=[])

        try:
            # Run Apify search
            items = run_apify_search(topic, apify_token, max_pages=1)
            self.logger.info(f"Apify returned {len(items)} items")

            # Parse results
            leads_data = parse_apify_items(items)
            self.logger.info(f"Parsed {len(leads_data)} leads")

            # Convert to pydantic models
            leads = [Lead(**lead) for lead in leads_data]
            result = LeadsList(leads=leads)

            # Create a result object that mimics CrewAI output
            class Result:
                def __init__(self, data):
                    self.pydantic = data
                    self.json_dict = data.model_dump()

            return Result(result)

        except Exception as e:
            self.logger.error(f"Error in Apify search: {str(e)}", exc_info=True)
            return LeadsList(leads=[])