
# TMDB TV Show Calendar Scraper

A Python utility that fetches TV show release schedules from **The Movie Database (TMDB)**, generates an `.ics` calendar file, and automatically syncs it to a **Radicale** CalDAV server (optional).

## Features

* **Automated Fetching:** Scrapes the latest season information for your favorite shows.
* **Customizable Cutoff:** Only includes episodes aired within a specific window (e.g., the last 30 days and all future dates).
* **ICS Generation:** Creates a standard iCalendar file compatible with Google Calendar, Apple Calendar, and Outlook.
* **Radicale Integration:** Automatically uploads the calendar to your private Radicale instance via WebDAV.
* **Timezone Support:** Properly handles timezones using `pytz`.

## Prerequisites

* Python 3.8+
* A free [TMDB API Key](https://www.themoviedb.org/documentation/api)
* (Optional) A [Radicale](https://radicale.org/) server instance for syncing.

## Installation

1. **Clone the repository:**

```bash
git clone https://github.com/doomkey/tv-show-to-ical.git
cd tv-show-to-ical

```

1. **Install dependencies:**

```bash
pip install -r requirements.txt

```

1. **Configure Environment Variables:**
Copy the `.env.example` file to `.env` and fill in your credentials.

```bash
cp .env.example .env

```

* `TMDB_API_KEY`: Your API key.
* `RADICALE_URL`: The full URL to your specific Radicale calendar (e.g., `https://cal.example.com/user/calendar.ics/`). Leave blank if not needed.
* `RADICALE_USERNAME`: Your Radicale login. Leave blank if not needed.
* `RADICALE_PASSWORD`: Your Radicale password. Leave blank if not needed.

---

## Configuration (`CONFIG.json`)

Manage your show list and settings in the `CONFIG.json` file:

```json
{
  "cutoff": 30,
  "shows": [1984]
}

```

* **`cutoff`**: `Integer`. The number of days in the past to include episodes for.
* **`shows`**: An `array` of TMDB Series IDs. You can find these in the URL of the show's page on TMDB (e.g., `themoviedb.org/tv/1984-show-name` -> ID is `225171`).

---

## Usage

Run the script using Python:

```bash
python main.py

```

Then you can upload the generated ics to your favorite calendar app.

### How it works

1. **Read Config:** Loads show IDs and the date cutoff.
2. **Scrape TMDB:** Iterates through each show, identifies the latest season, and collects episode air dates.
3. **Generate ICS:** Saves the data into `tmdb_show_schedule.ics`.
4. **Upload:** If Radicale credentials are provided, it performs a `PUT` request to update your remote calendar.

---

## Project Structure

* `main.py`: The core logic for scraping and uploading.
* `CONFIG.json`: Your list of TV shows and preferences.
* `.env`: Sensitive API keys and credentials.
* `requirements.txt`: Python library dependencies.

---

## Troubleshooting

* **Missing Episodes:** Ensure the show ID in `CONFIG.json` is correct and that the episode has a confirmed `air_date` on TMDB.
* **Upload Failures:** Verify that your `RADICALE_URL` ends with the `.ics` resource name and that your user has "Write" permissions on the server.
