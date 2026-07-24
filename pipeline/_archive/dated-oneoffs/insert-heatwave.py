#!/usr/bin/env python3
import json, requests, os, sys

def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                if line.startswith('export '):
                    line = line[7:]
                key, _, val = line.partition('=')
                val = val.strip().strip('"').strip("'")
                os.environ[key.strip()] = val

load_env(os.path.expanduser('~/.env.supabase'))

from datetime import datetime, timezone

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']

article = {
    "headline": "India\u2019s Heatwave Has Killed 56 People and Caused 25,000 Cases of Suspected Heatstroke Since March. If You Are Visiting This Summer, Read This.",
    "subheadline": "Thirty-four people died in a single district in Uttar Pradesh in two days \u2014 all over 60 with preexisting conditions. Temperatures have breached 42 degrees Celsius across northern India while power outages leave families without fans or running water.",
    "slug": "india-heatwave-56-dead-25000-heatstroke-cases-up-ballia-nri-summer-travel-risks-20260605",
    "category": "lifestyle-health",
    "vertical": "culture",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": "https://images.pexels.com/photos/9633009/pexels-photo-9633009.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=750&w=1260",
    "image_caption": "Scorching temperatures across India have caused 25,000 suspected heatstroke cases since March",
    "image_attribution": "Pexels",
    "is_editorial": False,
    "diaspora_angle": "The diaspora summer travel season \u2014 June through August, aligned with American and British school holidays \u2014 coincides directly with India\u2019s most dangerous heat period. NRIs travelling with elderly parents or young children face specific medical risks.",
    "sources": json.dumps([
        "The Indian Eye \u2014 Heat wave kills 56 in India; 25,000 heatstroke cases March-May (June 5, 2026)",
        "Associated Press \u2014 Doctors advise people over 60 to stay indoors in India heat (June 4, 2026)",
        "Outlook Business \u2014 Parametric Insurance as Heatwave Safety Net (June 1, 2026)",
        "India Meteorological Department \u2014 Heatwave advisory data, June 2026"
    ]),
    "body": """Fifty-six people have died from heat-related causes in India since March, and 25,000 cases of suspected heatstroke have been registered across the country from March through May, according to official data released this week. For the millions of NRIs who travel to India every summer with elderly parents, young children, and school-age kids in tow, this is not a weather story. It is a medical one.

The deadliest cluster occurred in Ballia district, Uttar Pradesh, where 34 people died in just two days \u2014 23 on Thursday and 11 on Friday. Every single victim was over 60 years old and had preexisting health conditions that worsened in the extreme heat. Heart attacks, brain strokes, and severe diarrhoea were the primary causes of death, according to Ballia\u2019s Chief Medical Officer Jayant Kumar.

Ballia recorded a maximum temperature of 42.2 degrees Celsius (108 degrees Fahrenheit) on Friday \u2014 4.7 degrees above normal. But this is not an outlier. Parts of Madhya Pradesh, Rajasthan, Uttar Pradesh, and Haryana have seen temperatures soar past 45 degrees Celsius (113 degrees Fahrenheit) in recent weeks. The India Meteorological Department has issued heatwave and severe heatwave warnings across northern, central, and eastern India.

## The Nighttime Problem

What makes this summer\u2019s heat especially dangerous is not just the daytime peaks \u2014 it is the loss of nighttime cooling. The IMD reports that India\u2019s average nighttime temperatures are rising by approximately 0.21 degrees Celsius per decade. In urban areas with dense concrete construction, temperatures barely drop after sunset.

This matters because the human body relies on cooler nights to recover from daytime heat stress. When nighttime temperatures stay elevated, the body accumulates stress over consecutive days, leading to chronic heat exhaustion that can trigger organ failure in vulnerable individuals \u2014 particularly the elderly, young children, and anyone with cardiovascular or kidney conditions.

The problem is compounded by power outages. Uttar Pradesh, India\u2019s most populous state with over 240 million people, has experienced widespread electricity failures, leaving families without fans, air conditioners, or running water. Protests have broken out across the state. Chief Minister Yogi Adityanath issued a statement urging citizens to use electricity judiciously \u2014 cold comfort for families in villages where the grid has been down for hours.

## The Scale of the Crisis

A study by the India Energy and Climate Centre at the University of California, Berkeley estimates that a single day of extreme heat causes approximately 3,400 excess deaths nationally. A five-day heatwave causes nearly 30,000. These figures count deaths above what would normally be expected \u2014 meaning the official toll of 56 almost certainly understates the true impact.

The World Bank has warned that heat stress could cost India up to 4.5 per cent of GDP by 2030 through reduced working hours, infrastructure damage, and direct productivity losses. India\u2019s electricity demand has already crossed an unprecedented 270 gigawatts during recent peak heat days, straining a grid that was not built for this load.

## What NRI Families Should Know Before Travelling

The diaspora\u2019s summer travel season \u2014 June through August, aligned with American and British school holidays \u2014 coincides directly with India\u2019s most dangerous heat period. Here is what medical professionals and public health officials are advising.

**Elderly relatives**: If your parents or grandparents are over 60 and living in northern or central India, the Ballia deaths are a direct warning. Doctors are advising all people over 60 to stay indoors between 11 AM and 4 PM. If your relatives lack reliable air conditioning or uninterrupted power, this is not a lifestyle inconvenience \u2014 it is a survival risk. Consider whether a visit during peak heat is wise, or whether you can time your travel for September.

**Children under five**: Young children are disproportionately vulnerable to heat because their bodies regulate temperature less efficiently than adults. Keep them hydrated with oral rehydration solution, not just water. Avoid outdoor activities during peak hours. Watch for warning signs: irritability, rapid breathing, hot dry skin, and refusal to drink.

**Hydration and diet**: Drink before you are thirsty. The traditional Indian approach of nimbu pani (lemon water with salt and sugar) is medically sound \u2014 it replaces both electrolytes and fluids. Avoid alcohol, caffeine, and heavy meals during peak heat hours. Fresh curd, buttermilk, and watermelon are not just cultural staples \u2014 they are evidence-based cooling strategies.

**Power outages and planning**: If you are staying in a city or town with unreliable electricity, pack a battery-operated fan, ensure you have access to bottled water, and identify the nearest hospital with a dedicated heat stroke ward. Many state governments have set these up, but they are often overwhelmed during peak events.

**Travel timing**: If your itinerary is flexible, the medical advice is clear. Avoid northern India in June and early July. Coastal and southern destinations \u2014 Kerala, Goa, Karnataka \u2014 are typically cooler and have more reliable infrastructure. If you must be in the north, travel during early morning or evening hours and rest indoors during the day.

## A Structural Problem

India\u2019s heatwave crisis is not an anomaly. It is a structural consequence of climate change, urbanisation, and infrastructure that has not kept pace with rising temperatures. The country created South Asia\u2019s first heat action plan after a deadly 2010 heatwave in Ahmedabad \u2014 a programme that saves an estimated 1,190 lives per year. But coverage remains patchy, and enforcement is inconsistent.

For NRIs, the emotional pull of summer in India \u2014 family weddings, temple visits, the mango season \u2014 is powerful. But this year, the data is asking you to plan differently. Check the IMD\u2019s heatwave forecasts before you book. Talk to your relatives about their cooling infrastructure. And if someone over 60 or under five is in your travel party, treat the heat as a medical condition, not a weather complaint."""
}

r = requests.post(
    f"{SUPABASE_URL}/rest/v1/p2_articles",
    headers={
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    },
    json=article,
    timeout=30
)
if r.status_code in (200, 201):
    result = r.json()
    aid = result[0]["id"] if isinstance(result, list) else "unknown"
    print(f"OK - Published: {aid}")
else:
    print(f"ERROR {r.status_code}: {r.text[:300]}")
