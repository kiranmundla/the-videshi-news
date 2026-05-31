#!/usr/bin/env python3
"""
Telegram Visa Sightings Scraper for The Videshi
Reads @VB_USA_AIS (bot) and @VisaAppointmentsIndia (community),
filters for India consulates, parses slot data, inserts to Supabase.
Runs every 15 minutes via cron on GCP e2-micro.
"""

import asyncio
import json
import os
import re
import sys
import time
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests
from telethon import TelegramClient

# ── Config ──────────────────────────────────────────────────────────────────
API_ID = 38578749
API_HASH = 'f90bdc2b980f63209f506ac0de772a47'
SESSION_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'videshi_telegram')

SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://dkuxxqofanrfvzwmhxci.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')  # anon key required
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

# State file to track last processed message IDs
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'telegram-scraper-state.json')

# India consulates we care about
INDIA_CITIES = ['Mumbai', 'Delhi', 'New Delhi', 'Chennai', 'Hyderabad', 'Kolkata']
INDIA_KEYWORDS = INDIA_CITIES + ['India', 'BOM', 'DEL', 'MAA', 'HYD', 'CCU']

# Visa types
VISA_TYPES = ['B1/B2', 'B1', 'B2', 'H-1B', 'H1B', 'H-4', 'H4', 'F-1', 'F1',
              'L-1', 'L1', 'L-2', 'L2', 'O-1', 'O1', 'J-1', 'J1', 'EB-1', 'EB1',
              'EB-2', 'EB2', 'EB-3', 'EB3', 'IR-1', 'IR1', 'CR-1', 'CR1']

CHANNELS = [
    {'username': 'VB_USA_AIS', 'type': 'bot'},
    {'username': 'VisaAppointmentsIndia', 'type': 'community'},
]

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)


# ── State management ────────────────────────────────────────────────────────
def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


# ── Bot channel parser (structured messages from @VB_USA_AIS) ───────────────
def parse_bot_message(text, msg_date):
    """Parse structured bot messages. Returns a sighting dict or None."""
    if not text:
        return None

    # Check if India-related
    if not any(kw.lower() in text.lower() for kw in INDIA_KEYWORDS):
        return None

    # Extract city
    city = None
    for c in INDIA_CITIES:
        if c.lower() in text.lower():
            city = c
            break
    if city == 'New Delhi':
        city = 'Delhi'

    # Extract visa type
    visa_type = None
    for vt in VISA_TYPES:
        if vt.lower() in text.lower():
            visa_type = vt.upper().replace('H1B', 'H-1B').replace('F1', 'F-1').replace('L1', 'L-1')
            break

    # Extract dates (look for YYYY-MM-DD or Month DD, YYYY patterns)
    date_patterns = [
        r'(\d{4}-\d{2}-\d{2})',
        r'(\d{1,2}/\d{1,2}/\d{4})',
        r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{1,2},?\s*\d{4})',
    ]
    dates_found = []
    for pat in date_patterns:
        dates_found.extend(re.findall(pat, text, re.IGNORECASE))

    # Build slot_date from the latest date mentioned (usually the new availability)
    slot_date = dates_found[-1] if dates_found else None

    return {
        'consulate_city': city or 'Unknown',
        'visa_type': visa_type or 'B1/B2',
        'slot_date': slot_date,
        'source': 'telegram_bot',
        'source_channel': '@VB_USA_AIS',
        'raw_message': text[:500],
        'spotted_at': msg_date.isoformat(),
        'spotter_name': 'VB_USA_AIS Bot',
        'confidence': 'high',
    }


# ── Community message parser (LLM-powered for @VisaAppointmentsIndia) ──────
def parse_community_message_llm(text, msg_date, sender_name):
    """Use OpenAI to parse freeform community messages."""
    if not OPENAI_API_KEY:
        return parse_community_message_regex(text, msg_date, sender_name)

    prompt = f"""Parse this Telegram message from a US visa appointment tracking group.
Extract ONLY if it's a confirmed slot sighting (someone saw or booked a slot).
Ignore questions, complaints, or general discussion.

Message: "{text}"

Return JSON (no markdown):
{{
  "is_sighting": true/false,
  "consulate_city": "Mumbai/Delhi/Chennai/Hyderabad/Kolkata/null",
  "visa_type": "B1/B2, H-1B, F-1, etc or null",
  "slot_date": "YYYY-MM-DD or null",
  "confidence": "high/medium/low"
}}"""

    try:
        resp = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {OPENAI_API_KEY}',
                'Content-Type': 'application/json',
            },
            json={
                'model': 'gpt-4o-mini',
                'messages': [{'role': 'user', 'content': prompt}],
                'temperature': 0,
                'max_tokens': 200,
            },
            timeout=10,
        )
        resp.raise_for_status()
        content = resp.json()['choices'][0]['message']['content'].strip()
        # Clean markdown wrapping if present
        content = re.sub(r'^```json\s*', '', content)
        content = re.sub(r'\s*```$', '', content)
        parsed = json.loads(content)

        if not parsed.get('is_sighting') or parsed.get('confidence') == 'low':
            return None

        if not parsed.get('consulate_city') or parsed['consulate_city'] == 'null':
            return None

        return {
            'consulate_city': parsed['consulate_city'],
            'visa_type': parsed.get('visa_type') or 'B1/B2',
            'slot_date': parsed.get('slot_date'),
            'source': 'telegram_community',
            'source_channel': '@VisaAppointmentsIndia',
            'raw_message': text[:500],
            'spotted_at': msg_date.isoformat(),
            'spotter_name': sender_name or 'Community Member',
            'confidence': parsed.get('confidence', 'medium'),
        }
    except Exception as e:
        log.warning(f'LLM parse failed: {e}')
        return parse_community_message_regex(text, msg_date, sender_name)


def parse_community_message_regex(text, msg_date, sender_name):
    """Fallback regex parser for community messages."""
    if not text:
        return None
    if not any(kw.lower() in text.lower() for kw in INDIA_KEYWORDS):
        return None

    # Skip questions
    if text.strip().endswith('?'):
        return None
    # Skip if it looks like a question
    q_words = ['anyone', 'has anyone', 'is there', 'when will', 'how to', 'can someone']
    if any(text.lower().startswith(q) for q in q_words):
        return None

    # Look for positive sighting indicators
    sighting_words = ['got', 'booked', 'available', 'slot', 'opened', 'found', 'grabbed', 'scheduled', 'dropped']
    if not any(sw in text.lower() for sw in sighting_words):
        return None

    city = None
    for c in INDIA_CITIES:
        if c.lower() in text.lower():
            city = c
            break
    if not city:
        return None
    if city == 'New Delhi':
        city = 'Delhi'

    visa_type = None
    for vt in VISA_TYPES:
        if vt.lower() in text.lower():
            visa_type = vt
            break

    return {
        'consulate_city': city,
        'visa_type': visa_type or 'B1/B2',
        'slot_date': None,
        'source': 'telegram_community',
        'source_channel': '@VisaAppointmentsIndia',
        'raw_message': text[:500],
        'spotted_at': msg_date.isoformat(),
        'spotter_name': sender_name or 'Community Member',
        'confidence': 'medium',
    }


# ── Supabase insert ────────────────────────────────────────────────────────
def insert_sightings(sightings):
    """Insert sightings into Supabase visa_sightings table."""
    if not sightings:
        return 0

    if not SUPABASE_KEY:
        log.error('SUPABASE_KEY not set')
        return 0

    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal',
    }

    inserted = 0
    for s in sightings:
        row = {
            'consulate_city': s['consulate_city'],
            'visa_type': s['visa_type'],
            'slot_date': s.get('slot_date'),
            'source': s['source'],
            'source_channel': s.get('source_channel'),
            'raw_message': s.get('raw_message'),
            'spotted_at': s['spotted_at'],
            'spotter_name': s.get('spotter_name'),
            'confidence': s.get('confidence', 'medium'),
        }
        try:
            resp = requests.post(
                f'{SUPABASE_URL}/rest/v1/visa_sightings',
                headers=headers,
                json=row,
                timeout=10,
            )
            if resp.status_code in (200, 201):
                inserted += 1
            else:
                log.warning(f'Supabase insert failed ({resp.status_code}): {resp.text[:200]}')
        except Exception as e:
            log.warning(f'Supabase insert error: {e}')

    return inserted


# ── Main scraper ────────────────────────────────────────────────────────────
async def scrape():
    state = load_state()
    client = TelegramClient(SESSION_PATH, API_ID, API_HASH)
    await client.connect()

    if not await client.is_user_authorized():
        log.error('Telegram session not authorized. Re-run auth on local machine.')
        return

    me = await client.get_me()
    log.info(f'Connected as {me.first_name}')

    all_sightings = []

    for ch in CHANNELS:
        username = ch['username']
        ch_type = ch['type']
        last_id = state.get(f'last_id_{username}', 0)

        try:
            entity = await client.get_entity(username)
            log.info(f'Reading @{username} (last_id: {last_id})')
        except Exception as e:
            log.error(f'Could not get entity @{username}: {e}')
            continue

        new_msgs = []
        async for msg in client.iter_messages(entity, min_id=last_id, limit=500):
            new_msgs.append(msg)

        if not new_msgs:
            log.info(f'  No new messages in @{username}')
            continue

        log.info(f'  Found {len(new_msgs)} new messages in @{username}')

        for msg in new_msgs:
            if not msg.text:
                continue

            if ch_type == 'bot':
                sighting = parse_bot_message(msg.text, msg.date)
            else:
                sender_name = None
                if msg.sender:
                    sender_name = getattr(msg.sender, 'first_name', None) or \
                                  getattr(msg.sender, 'title', None) or \
                                  'Community Member'
                sighting = parse_community_message_llm(msg.text, msg.date, sender_name)

            if sighting:
                all_sightings.append(sighting)

        # Update state with highest message ID
        max_id = max(m.id for m in new_msgs)
        state[f'last_id_{username}'] = max_id

    await client.disconnect()

    # Insert to Supabase
    if all_sightings:
        inserted = insert_sightings(all_sightings)
        log.info(f'Inserted {inserted}/{len(all_sightings)} sightings to Supabase')
    else:
        log.info('No India-related sightings found this run')

    # Save state
    state['last_run'] = datetime.now(timezone.utc).isoformat()
    save_state(state)
    log.info('Done')


if __name__ == '__main__':
    asyncio.run(scrape())
