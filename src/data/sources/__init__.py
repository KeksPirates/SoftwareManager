from data.sources.rutracker import RutrackerScraper
from data.sources.uztracker import UztrackerScraper
from data.sources.steamrip import SteamripScraper
from data.sources.monkrus import MonkrusScraper

# Register Scrapers here
SCRAPERS = [
    RutrackerScraper(),
    SteamripScraper(),
    MonkrusScraper(),
    UztrackerScraper(),
]