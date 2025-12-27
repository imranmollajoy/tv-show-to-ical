import os
import json
import requests
import datetime as dt
import pytz
import re
from icalendar import Calendar, Event, Timezone
from dotenv import load_dotenv

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
RADICALE_URL = os.getenv("RADICALE_URL")
RADICALE_USERNAME = os.getenv("RADICALE_USERNAME")
RADICALE_PASSWORD = os.getenv("RADICALE_PASSWORD")

# Constants
TMDB_BASE_URL = "https://api.themoviedb.org/3"
OUTPUT_FILENAME = "tmdb_show_schedule.ics"
CALENDAR_NAME = "TV Show Release Dates"
LOCAL_TIMEZONE = pytz.timezone('Asia/Dhaka')

# will be overriden by config.json, howeber do not remove
CUT_OFF_DAYS = 30

def generate_uid(show_title, season_number, episode_number, air_date):
    sanitized_title = re.sub(r'[^A-Za-z0-9]', '_', show_title)
    return f"{sanitized_title}-S{season_number:02d}E{episode_number:02d}-{air_date}@tmdb-scraper.com"

def fetch_json(url, params=None):
    """Generic helper to fetch JSON from TMDB."""
    params = params or {}
    params['api_key'] = TMDB_API_KEY
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching: {e}")
        return None

def create_calendar_event(show_title, season_number, episode_number, episode_name, air_date_str):
    event = Event()
    try:
        start_date = dt.datetime.strptime(air_date_str, "%Y-%m-%d").date()
        end_date = start_date + dt.timedelta(days=1)
        
        event.add('dtstamp', dt.datetime.now(pytz.utc))
        event.add('summary', f"{show_title}: {episode_name}")
        event.add('dtstart', start_date)
        event.add('dtend', end_date)
        event.add('description', f"New ep of {show_title}.")
        event.add('uid', generate_uid(show_title, season_number, episode_number, air_date_str))
        return event
    except Exception as e:
        print(f"Skipping ep for {show_title}: {e}")
        return None

def scrape_and_save_ics(show_ids):
    cal = Calendar()
    cal.add('prodid', f'-//TMDB Show Schedule//{CALENDAR_NAME}//EN')
    cal.add('version', '2.0')
    cal.add('X-WR-CALNAME', CALENDAR_NAME)
    cal.add_component(Timezone.from_tzid(LOCAL_TIMEZONE.zone))

    past_cutoff = dt.date.today() - dt.timedelta(days=CUT_OFF_DAYS)

    for show_id in show_ids:
        show_data = fetch_json(f"{TMDB_BASE_URL}/tv/{show_id}")
        if not show_data: continue

        show_title = show_data.get('name')
        seasons = show_data.get('seasons', [])
        
        # Get the highest numbered season (excluding Specials/Season 0)
        valid_seasons = [s for s in seasons if s.get('season_number', 0) > 0]
        if not valid_seasons: continue
        
        latest_season_num = max(s['season_number'] for s in valid_seasons)
        season_data = fetch_json(f"{TMDB_BASE_URL}/tv/{show_id}/season/{latest_season_num}")
        
        if not season_data: continue

        events_added = 0
        for ep in season_data.get('episodes', []):
            air_date_str = ep.get('air_date')
            if not air_date_str: continue
            
            air_date = dt.datetime.strptime(air_date_str, "%Y-%m-%d").date()
            if air_date >= past_cutoff:
                ep_num = ep.get('episode_number', 0)
                ep_display_name = f"S{latest_season_num:02d}E{ep_num:02d} - {ep.get('name')}"
                event = create_calendar_event(show_title, latest_season_num, ep_num, ep_display_name, air_date_str)
                if event:
                    cal.add_component(event)
                    events_added += 1
        
        print(f"Added {events_added} episodes for '{show_title}'")

    with open(OUTPUT_FILENAME, 'wb') as f:
        f.write(cal.to_ical())

def upload_to_radicale():
    if not all([RADICALE_URL, RADICALE_USERNAME]):
        print("Radicale credentials missing in .env. Skipping upload.")
        return

    try:
        with open(OUTPUT_FILENAME, 'rb') as f:
            response = requests.put(
                RADICALE_URL,
                data=f.read(),
                headers={'Content-Type': 'text/calendar; charset=utf-8'},
                auth=(RADICALE_USERNAME, RADICALE_PASSWORD)
            )
        print(f"Radicale Upload: {'Success' if response.status_code < 300 else 'Failed'}")
    except Exception as e:
        print(f"Upload Error: {e}")

if __name__ == "__main__":
    # Load IDs from the external JSON file
    try:
        with open('CONFIG.json', 'r') as f:
            config = json.load(f)
            show_ids = config["shows"]
            CUT_OFF_DAYS = config["cutoff"]
            print(CUT_OFF_DAYS)
        # scrape_and_save_ics(show_ids)
        # upload_to_radicale()
    except FileNotFoundError:
        print("Error: CONFIG.json not found.")