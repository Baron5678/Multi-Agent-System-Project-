"""
Demo driver for the multi-agent startup scheduler.
"""

from config import API_KEY
from core.message_router import MessageRouter
from core.data_models import UserPreferences, SchedulingRequest
from agents.user_agent import UserAgent
from agents.investor_agent import InvestorAgent
from agents.event_agent import EventAgent
from agents.geolocation_agent import GeolocationAgent
from agents.commute_agent import CommuteAgent
from agents.scheduling_agent import SchedulingAgent

# 1. Define simple system prompts
USER_PROMPT = (
    "Extract the startup founder's industry, location, stage, and available dates from the input text, "
    "and return as a JSON object matching {'industry': str, 'location': str, 'stage': str, 'available_dates': [str]}."
)
INVESTOR_PROMPT = (
    "Given the founder preferences as JSON, return a JSON array of investor objects "
    "[{name, location, interests, profile_url}] that best match."
)
EVENT_PROMPT = (
    "Given the founder preferences as JSON, return a JSON array of upcoming event objects "
    "[{name, date, location, description, event_url}]."
)
GEO_PROMPT = (
    "Convert the given address string into a JSON object {latitude: float, longitude: float}."
)
COMMUTE_PROMPT = (
    "Given origin and destination coordinates as JSON "
    "{\"origin\": {latitude, longitude}, \"destination\": {latitude, longitude}}, "
    "return a JSON object {origin, destination, travel_time_minutes, distance_km}."
)
SCHEDULER_PROMPT = (
    "Given a JSON object with 'user', 'investors', and 'events' fields, each formatted per schema, "
    "build a prioritized meeting schedule and return it as JSON {slots: [...slots...]}."
)

# 2. Instantiate agents
agents = {
    'UserAgent': UserAgent(USER_PROMPT),
    'InvestorAgent': InvestorAgent(INVESTOR_PROMPT),
    'EventAgent': EventAgent(EVENT_PROMPT),
    'GeolocationAgent': GeolocationAgent(GEO_PROMPT),
    'CommuteAgent': CommuteAgent(COMMUTE_PROMPT),
    'SchedulingAgent': SchedulingAgent(SCHEDULER_PROMPT),
}

router = MessageRouter(agents)

# 3. Demo input from founder
raw_input = (
    "I'm a seed-stage AI startup based in Berlin. "
    "I'm free on 2025-05-05 and 2025-05-06 for meetings."
)

# 4. Extract preferences
print("[UserAgent] Extracting preferences…")
prefs: UserPreferences = agents['UserAgent'].get_preferences(raw_input)
print(f"Parsed preferences: {prefs}\n")

# 5. Fetch investors and events
print("[InvestorAgent] Fetching investors…")
investors = agents['InvestorAgent'].get_investors(prefs)
print(f"Found investors: {investors}\n")

print("[EventAgent] Fetching events…")
events = agents['EventAgent'].get_events(prefs)
print(f"Found events: {events}\n")

# 6. Geocode founder location
print("[GeolocationAgent] Geocoding founder location…")
coords_user = agents['GeolocationAgent'].get_coordinates(prefs.location)
print(f"Founder coordinates: {coords_user}\n")

# 7. Compute commute for each meeting candidate
print("[CommuteAgent] Calculating commute times…")
for obj in investors + events:
    loc = getattr(obj, 'location', None)
    if loc:
        coords_target = agents['GeolocationAgent'].get_coordinates(loc)
        commute = agents['CommuteAgent'].calculate_commute(coords_user, coords_target)
        setattr(obj, 'commute', commute)
print("Commute info added.\n")

# 8. Build final schedule
print("[SchedulingAgent] Building schedule…")
req = SchedulingRequest(user=prefs, investors=investors, events=events)
schedule = agents['SchedulingAgent'].build_schedule(req)
print("Final schedule:\n", schedule.json(indent=2))