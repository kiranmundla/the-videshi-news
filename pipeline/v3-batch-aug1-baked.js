export const meta = {
  name: "v3-batch-aug1",
  description: "Write V3 articles for The Videshi - Aug 1 batch",
  phases: ["write", "enrich", "publish"]
};

var candidates = [
  {
    "topic_id": "d7644cf8-a6f2-4123-8eb6-927972c5d7c7",
    "title": "It might take \u2018a lightning bolt from God\u2019 to get these Senate Democratic hopefuls to bow for independents - Politico",
    "category": "news",
    "coverage": "new",
    "llm_score": 5,
    "source_urls": [
      "https://news.google.com/rss/articles/CBMiogFBVV95cUxNckl6M3JBNmIyYUY5cXNfcVFyT3ZKcGRwLTQ3VHAtaWdiZ2J5NVJqdDNON2huOGZDR29VbkJwT21yX0hLNjhzbU5pMWpnVE81X1M0RG5KTWFSZk5VU2ZMVmlHV19pTnRIRW8xOENtRkZVelE3QnFUMFIyY1BOdGc2NEhONEItNVREelRYdENfdTcxUFNCNGRuaGdQUEg4WlhpVFE?oc=5",
      "https://news.google.com/rss/articles/CBMiqgFBVV95cUxQelROTVlwMjRUazRaMFFaZDQxOUo2QXlQRFdLdG5SdE1ZV2ZySVQyOFFNcXB3RE1LOTQ4MEhXcmZPeUd2dmtYVURUY1JRZE9zX3JBNWRQc1dmVnA3aHk3VUs5Y0tnZU8zSEpRSk0zMVVlUUVzWUdaU05jWUYzTEk1SG0tNWZ5eWJ3T3hBalp4TUtPZXlwWDMyMjNEQ1NJQ2xOeGRaSkdNclBVQQ?oc=5",
      "https://news.google.com/rss/articles/CBMilgFBVV95cUxPZnhON1BzVlc4NVV4MEFucnY5OERtaWRjQWRQa1dPT09LempxemhpdTFYa0lSb3RpbWplUVV2bWpOaGhTQ1pjWlJCOWlzQmk1TG5vZHFMZzMySFpNdUlaUUZvaFZRVUQ0TE5CMlVIU094ZGRQcXpZZFhIQ0xmX05sdXdlZ2Uzdi0wN1I0NDFZN1puNWFSTkE?oc=5",
      "https://news.google.com/rss/articles/CBMiugFBVV95cUxNWlE4cF9CQXpqblF0dU91cDZEWGVEdHdfSlZ0TjgtY3hINnlBQ0p0YzJaSVUweWlIMVZBRVJrRG1LOS12bDgzbDN1QXljM2hCSlk2MUtYOTNHR1lCWE9rLUFWMUw5enlTdzRzenN0VW55dnc5VU1FMjlDWmdfTldJSFlhb3hEY3BRNFdhT2R4NFZfQ2xsSGRsblhuZUdHV3AyeVhvVnhoRWc1ZzdCdUhjaXdaTExoV0N4TXc?oc=5"
    ],
    "signals": [
      {
        "title": "It might take \u2018a lightning bolt from God\u2019 to get these Senate Democratic hopefuls to bow for independents - Politico",
        "source": "Politico"
      },
      {
        "title": "Democrats\u2019 novel red-state strategy: From the Politics Desk",
        "source": "NBC News"
      },
      {
        "title": "Dropout pressure builds in Montana\u2019s U.S. Senate race",
        "source": "Montana Free Press"
      },
      {
        "title": "Analysis | A divided field threatens Democrats\u2019 Montana Senate hopes",
        "source": "The Washington Post"
      },
      {
        "title": "Montana\u2019s Secretary of State weighs in on questions swirling around US Senate race",
        "source": "The Independent Record"
      }
    ]
  },
  {
    "topic_id": "b3587552-94e3-48eb-8c96-ad2804dc1672",
    "title": "Kuwait intercepts Iranian drones as Trump weighs fresh strikes - Investing.com",
    "category": "news",
    "coverage": "new",
    "llm_score": 5,
    "source_urls": [
      "https://news.google.com/rss/articles/CBMiXkFVX3lxTE5kMDV5b1pUV2JCZEZROEtPZGhucUN6SWNkVEpTZnc2VGRtVDljc01sd3REQ19VOFk2emlmNkc0OXBpRk9nMzZWbTZaZXpDXzJMRkRiSy1uckMzOVIxVUE?oc=5",
      "https://news.google.com/rss/articles/CBMiugFBVV95cUxPZFlzVnpaQVVja0hLYVRtSlpzVGEtbGpfaEpFTFV1RlRaTTJ0RHpJejkxMVlTbHRhWDc0X3dzWng0eUpibGlKcmhWZjh4SDV2TFZmTmZSX3FEWFNSSjk5eXAySk5oU3ZVNTVscG9COTVMQzhTQnBNYTZGRjlwYzJKTUdyMF85amxzR0Z2bzJyT1NBSlRPT1dGM045SklQU1YzQ2ZlS1dNZDEwclJQWW13QnZ2TlRzYTNycnc?oc=5",
      "https://news.google.com/rss/articles/CBMisgFBVV95cUxQUDJ1QkxLSTV4Tlk2WW5sSXM4RjVOcVYtV0JVazJfZjBBOFNiLVM2bFlHQzMxbDhhZWRVY19XVEZNWFI5TzhYeDFjVWpvc0trbWtPeHo1aDBpTG5mVXY4Rm9EYlJkVzhzZmMxMlZZMnAzdFRJV1NLbG1XT3h6aFA3RjhVWWVibFJlWHY3ZUVOUXR2Y2J5UnBCektJT3I0aHM5eVpYeDNhMGxRQTYtNjdtekRB0gG6AUFVX3lxTE5pd0VhWkxQUzVXV21PWnBwZHpra3QzQkRiVzM2MjBqTHZfbkpTRmVxZEE4TnBiZlY3c2t0MTZiQ1ZvdjBoenlqUkRiV2tLYnh5VDltczBqOHJwZnNZanBjWDlTRWdyd0o0aVRialJmSEdRRGt2QXhsbmNHcmhvWXN2cTk2dUdOd3JON1BrMXphRE9CdFBjUUJTcFNnZjRWcUp5OE5sbFF4RU81Y2R5WDlaRnpSYjZYb1VlZw?oc=5",
      "https://news.google.com/rss/articles/CBMibkFVX3lxTE51WEhTa2FEaHQ5MGh3N212TjRyX0V2Z0xYd2I4RUFKNmVORnhrUWhzeDRWUENLaVB1dTRjS2NFdTEtR3R0R016LWdWYjQyMnRQSDAxbHh0dTBfck1udEtUd2h5NFpLV0VfSmx6OWNn?oc=5"
    ],
    "signals": [
      {
        "title": "Kuwait says hostile drones destroyed after debris damages property",
        "source": "Arab News"
      },
      {
        "title": "Kuwait intercepts Iranian drones as Trump weighs fresh strikes - Investing.com",
        "source": "Investing.com"
      },
      {
        "title": "Kuwait Says Shot Down Iranian Drones Targeting 'Vital And Military' Sites",
        "source": "NDTV"
      },
      {
        "title": "UKMTO SAYS IT RECEIVED REPORT OF AN INCIDENT 11NM NORTHEAST OFF LIMA, OMAN",
        "source": "news.cgtn.com"
      }
    ]
  },
  {
    "topic_id": "2594808b-8414-458e-8963-ca890e2eee3f",
    "title": "Gujarat lung cancer cases rise as tobacco cultivation expands despite Centre's diversification push - BusinessLine",
    "category": "lifestyle-health",
    "coverage": "new",
    "llm_score": 5,
    "source_urls": [
      "https://news.google.com/rss/articles/CBMi8wFBVV95cUxPOXhJaGotVE0tZ25KdFJER25JZzZKNVptMmdhUDJxLTFKUUNsVWJGQ1ExeFJZTTl5VVJaRmV5VFlmVzQ1Wm9MVjdfR21oakxRa0ZoZVVQMHNBMzlOTC11VWN5bFZmTjhKdWwtWlN3SGFxV3RDUTlKWWJ2V285ejhJbHJBMFZ5ZmJrNUFzcUhfcm9jMVB3WG9VZTBNNXg0YktJSWNOb1NjdHdwQzEwVW5MNzFBOFdxNzNLWnZ4dmxVRkc2WVBvZ1Rtd1BMZ1pKYzBWbm5GbDBkU1BlMnRhOWFaSzFOQWxEV2ZDUXFOUjVzYU5PNEHSAfoBQVVfeXFMUGFpbEN6czdPUUtSZTQ2T2pxc21Rdk03Smp5OExWaWFxTW9pdXQxcFFKaUhUWUJnZFctOFdqdkNrZXFYWEx1OFk4S3JCTC1saEU3UlB2TUpqZmFONEJ6bENrUFdocHh1UGJtNzI0RzlZOTg2ekFmc3EzQnVYWGVZTDVmMXVoM09OX0NMbDM1ZGt5RkQtc1ZCOHlnSTVBeGtmYzkxb0NNQkYxaUJrc1pBSF9mYzlGZnRLanZVVGdPU0NhT0o0a0hFcDQ3SHp6T1lJa05JdHhjMm5ZSUNLd2V6dU1QWUs5RmlPNU92MFNDQkpOMS1ZcVBFMVM5Zw?oc=5",
      "https://news.google.com/rss/articles/CBMi5gFBVV95cUxOLVJ6SWI3Zm9YM1V5V0tZek91MkJkMTM5MkF3LWswOGJ1NEQwRE9wdnZNbVA3WmxhR2VSbS1HbzgxTFRHVXVialRDeG1QU3VoVlFTVi03cHoyVVpWMDJ4MnJ4TVZoVTV1eTR6M1JKR0g5NnlTOFRDdXEwbXpvRGtZbjRfSS0xNThuNTl5YXhTRGQ0LVJ1VDViNFhCYUxJZVFpa0ljY0NUTEo5WEVFYS0tUm0xOW9mWVgzdlRUVVFSX09HQ3dEVEhBR21JSzlWTVVsSjdvbmtlQy0ycGFpX19YNTliX0xaZw?oc=5",
      "https://news.google.com/rss/articles/CBMiygFBVV95cUxNeEZnT19GVXlwc3hwWU14YXRnTkFFcDRkbFdNNzd5WnhYeTE5ZzVoTkJJMjVPa2NpaDdlbUV3RUpoWFRfb2JQb24tR1pxVElfYmRpX1p2SW91UERXY2hqbmRFb1Z1RzlEcFVwLXIzZV9RT2htY3piY1BrQ2JVWlo3YnZMMGNFSXpsUXFZVDdqOEZfdjNlUW1MWTlITHJFNFA5R05ET1NoblJlakx0aDcwM3M5RmxSWmFLdEI5T2drbmE3NUtubHBUOXBB?oc=5",
      "https://news.google.com/rss/articles/CBMiqwFBVV95cUxNTkFGN3JRa1ZOblJTUmdfNFU2dXBsaGZCbGdLUXVtNjRyYUxPeXhHOGl6OUdybmJJbTdtdExiRFZaUExuY0w3VUl6QzR3REFQYWZYZEdaNExWRWt3b2FQbEV6SjA1LXlISl9UWlZDa2dEN0lUc3RDYlJ2U2hYS2p6U2tQdDVzcFN5bVl5MkVEODl5RnE4UDdRcVhmOGZwejI0NzBkRmdRaWp5OFU?oc=5"
    ],
    "signals": [
      {
        "title": "Gujarat lung cancer cases rise as tobacco cultivation expands despite Centre's diversification push - BusinessLine",
        "source": "BusinessLine"
      },
      {
        "title": "Gujarat Cancer And Research Institute Reports Steady Increase In Lung Cancer Cases, Tobacco Remains Key Risk Factor",
        "source": "NDTV"
      },
      {
        "title": "Ahmedabad Records 39% Rise in Lung Cancer Cases Over Five Y\u2026",
        "source": "GujaratSamachar English"
      },
      {
        "title": "World Lung Cancer Day 2026: GCRI Calls for Early Detection, Tobacco-Free Life",
        "source": "theblunttimes.in"
      },
      {
        "title": "Committed to providing best possible treatment for serious diseases: Gujarat govt",
        "source": "Big News Network.com"
      }
    ]
  },
  {
    "topic_id": "0a9903e5-ee56-4897-8c96-e8a9664b794e",
    "title": "By Not Giving Reasons, Collegium Doing Disservice To Judges Doing Good Work : Justice Ujjal Bhuyan - Live Law",
    "category": "news",
    "coverage": "new",
    "llm_score": 5,
    "source_urls": [
      "https://news.google.com/rss/articles/CBMi5wFBVV95cUxNM3c4VVl5ZllwMDVSbC13dko0TzlCazBYblRfZnNxUXAxYnpsdDljV0xHdzZrNjB0ZTZIelZHYnY2cGpQUmhjZ0ZwODlhVFczMmtkWDdDR2xqWlRnSDJMZEpya3M2UlkyQXZ2akplcmNCV1RyYXJrT0hGVVBOZWROUTRnTmxjQ0lmeEswSGlCYjZrbF8tVkdxMkhZUVJBa0hLV0REcmZxcVpSc2Z0UlVPR2hVaG1zekZUMjdPSVNvcjd5eEdHQXpFVHR6YVR2cjZUYmwyYUUxb0dXMDhCa3lTY1EtTmw4YXc?oc=5",
      "https://news.google.com/rss/articles/CBMi1gFBVV95cUxPX2NzU0trZHZaeDYwZVcwdzMyX1ZKOU0xNkxvYnJhOE16bG1sOTl3QVFKQjB4RWhqWmUtT0UtVVlIcDJZNG9KNU1vMDd3VzNhLWZvZ0FIOE8xSnhzLTR4SnlvTnpOYkVZRmc3a3hpSzNxVVI1NkJZbnpPZjE5RnJkQVV5UkI5b0FLNmFEZW90dVF6TDN4c1FUZmdFdDRpZmVhUTY4RGp2ektSQU5TdElRbFBVUl94aVo4SWNpdWladGFPM2RwZmU3LUdXWTZlWDZSX25lemJn?oc=5",
      "https://news.google.com/rss/articles/CBMi0wFBVV95cUxQcjRIaUFzYW9MZ25hOXdpdVVBeTd2NHRZN0hza2VmZmZMZzFqNjNLRGtwQTRxUE1jdG9WSU4xRFN0a0QzakFkOWJ0eU1Wam5MTVFoODBCdmpOYmk2V2xrNkZIRlI1MlhGNHMzTkdpYnU2LWpQWXI4RE1Vcl9EWU9yRXlpSHNqWFRzdnVLeEUySjhURVNyaU5kMlBUdGR1S1dHZ0YwdmRIbGNLWnphbVhRU2RDZVA0b1MxMnNvRzRBQjlyTEljbjNUOEd2Q0pOSjFtbGVR0gHaAUFVX3lxTE1XUFBKbG9JTV9Jd0t6RjJoVUtXbklaQ2pxc3UxNkdpZ0J5WjFPUFcyMmhGUnd3cHdsWWVKVTdYWThVTXNDa21ZQ1RHV3JVZEpEdUI5cTRxbENPT1luZ0FYdUpkUTVPVUFlSTdKdTRYY24wWGE4MURreWtvQnowN0NlQmFUempEY2x1WGNuZmtacUxWVnBfUTNVMDM4V0ZNcjdfWEtJSkhuTzlKLWpOQ2xKUmNKaEFGUDQ1ZnlNYXM2LUlja0Y0QmFlU3FjN2xPZTdnbWY3VHA0R0lB?oc=5",
      "https://news.google.com/rss/articles/CBMirAFBVV95cUxPcjlhczFuLTlOaE5VMWtUSHRHQmNrZjFXSHp1eXpMQWU3YVUzQy1qM0tkTUNEdWdFUHFMQlZUU0FLejZrQVc1MFQtSW9kYW4xSHc2ME5jZTVzVm5TMFd0dmpQTjBCQmRFb0lDNDRXWW1XT0g3R29TeFVQMEJrWWxSQmVtTDI5eGdNRjFnUUNFbjE4cXZaT2hEelBPMGlZNFpabHhYT2s1UnZJcnN30gGyAUFVX3lxTFBQVDFrdmRjaUxhUmJOeXNXV040eGVjRXppM2NGRTlwakJ2VVdlTkVWSy1uYS1hT1NBaF90aTlyMWF6RTViemstcVA3d1QxQU1HUGxiVUVndDVjeDh1RkdxQVRRaDZud1U3MElDN1ZNZ0pnWTI0WnowYnBpaTZkUlRUaUE1enpLM2F1azE0LUh0d1NGM01FM3o1MXkycFR1Zm8wMjNHazFjMUV2WUNzbjBzY3c?oc=5"
    ],
    "signals": [
      {
        "title": "Justice Ujjal Bhuyan flags return of opacity in Collegium; slams appointment of judges who make unconstitutional remarks",
        "source": "Bar and Bench"
      },
      {
        "title": "Supreme Court judge's 'ant' remark during discussion on judicial transparency",
        "source": "India Today"
      },
      {
        "title": "SC Collegium\u2019s unexplained recommendations risk bad appointments: Justice Bhuyan",
        "source": "The Hindu"
      },
      {
        "title": "Collegium not giving reasons is disservice to judges: Justice Ujjal Bhuyan",
        "source": "ThePrint"
      },
      {
        "title": "By Not Giving Reasons, Collegium Doing Disservice To Judges Doing Good Work : Justice Ujjal Bhuyan - Live Law",
        "source": "Live Law"
      }
    ]
  },
  {
    "topic_id": "6caa8aad-be54-4114-9f78-c08e88dd786a",
    "title": "Kia India Sales July 2026 Up 27% To 28,200 Units \u2013 Best Ever July Performance - RushLane",
    "category": "markets-finance",
    "coverage": "new",
    "llm_score": 5,
    "source_urls": [
      "https://news.google.com/rss/articles/CBMirgFBVV95cUxNcGtFa3BMREJUZWRPSHFqZG9kNnFySy04azFCNERpWE5Gb0paeWdISmhUS1J5dUVJUnRHM0NHV0QwV1loVVF6M1ZIN3BVWHdUZVVoUkxHcDdYcmdZd0VsTW81ZUdMM1ptMVAzR05RT21zZ2VaOEJ5bGlWT3BYTExmV21ydF90THJvU2xhaUxld0lndWkzc3B2UVZsV2MzLXJ3dk84R2lnbzM0YXlRSGc?oc=5",
      "https://news.google.com/rss/articles/CBMi7gFBVV95cUxNbWdiOHJ0YU5weVYyR204bTdQVW9LWXdlUGRMSkMwWU5CYkNBZHlCRzBnRzRNb09yNklJQkMwQXR5akk4cGFNODhydTROMEF4R2FoczFzOU9WQzFHYmxJendSYW9SbEx0LURaaGlyY21CdjU3ODdCUHBLNTlLeXBRY1ItWlQzZjhqSmd6M0VtMnRpa2R4RVAxUFRHNndJS2RKV0E5YWQ3ODBOWjZrOGxBenI1MjhIQ3pzRmtWUWZTNGM5MVJ5bTFpdndnZzUtWkdVQ2hXU2lEcDZrU3g4NjJ3ekNka0R2dmFGR2t3Nkp30gHzAUFVX3lxTE5UaXk5a0tqM1VZNTdZZkd2ekt0SlVhTTV0cnBraTBaQlNfbFEwa0Y1YWNtdVJOVjVkLWtHSHNWU1BIMTlfSjlnYV9rWklVUkNOVDhVMDU5Q1hxMHlyWlNBeHg1TmYyUzdEZnFqRW1jcnlLblhycDVKR2NtV2RacHQ4bE9uZTlLUFl6cFdvZXNiMUNoaHVDQm0xTGJ5bHRRdXlpd0hRcEduZjh6ZzRra1dJX3lTdEtZbHlxa2FQM0VMYWVnLXZ4YkVBZkM0SjJuUHYtLUdpWE9VM013YnlObnVTSS1vcHJ0OXVfdnJzejVuN3MtNA?oc=5",
      "https://news.google.com/rss/articles/CBMijgFBVV95cUxOMktWV1NDR2JiVm5iaHJTcUJiYlM2elh1Z2tlaEJxYktfQTFrYXVEbzFONWZoUEtDUlFOenFLanlYS045ZnhPbFhibnE2Vy1RZFVrd2Z6TGxPYmlIMi1nOVdRRnY2em5aVGlINmoxUzhxS2pTdHJMWlRFRjV0V1VIY1JKMFUxclFwYmN3bllB0gGOAUFVX3lxTE4yS1ZXU0NHYmJWbmJoclNxQmJiUzZ6WHVna2VoQnFiS19BMWthdURvMU41ZmhQS0NSUU56cUtqeVhLTjlmeE9sWGJucTZXLVFkVWt3ZnpMbE9iaUgyLWc5V1FGdjZ6blpUaUg2ajFTOHFLalN0ckxaVEVGNXRXVUhjUkowVTFyUXBiY3duWUE?oc=5",
      "https://news.google.com/rss/articles/CBMiggFBVV95cUxNdjVsUjVjWVZ0MmpVWE1jWDl2NXBlenczWkxTUVo3Sm5QcjI2bEVqVUpwT3ZQLVZVWFNEM01yTWl0Mm9pTmVHWlBEbUt4b1JPbm1ubk9DbXNkYlh1bkFXVjRiZTJFR2tkZkxBWDJRTGE0Sml1MERPeTZmcHNHRU91Y0tR?oc=5"
    ],
    "signals": [
      {
        "title": "Kia India July sales up 27.4% at 28,200 units",
        "source": "BusinessLine"
      },
      {
        "title": "Kia India logs best-ever July wholesale sales, dispatches up 27.4% to 28,200 units",
        "source": "The Economic Times"
      },
      {
        "title": "Kia India Sales July 2026 Up 27% To 28,200 Units \u2013 Best Ever July Performance - RushLane",
        "source": "RushLane"
      },
      {
        "title": "Kia India records its highest-ever sales in July",
        "source": "NewsBytes"
      },
      {
        "title": "Kia India July sales hit record high at 28,200 units, rise 27% YoY",
        "source": "CNBC TV18"
      }
    ]
  },
  {
    "topic_id": "cef30590-6b21-40b9-8653-e70243940dc4",
    "title": "Honda 2W Sales July 2026 at 476k - ADV 160, Rebel 300, CB500 Upcoming Launches - RushLane",
    "category": "markets-finance",
    "coverage": "new",
    "llm_score": 5,
    "source_urls": [
      "https://news.google.com/rss/articles/CBMi3wFBVV95cUxPZzc3WDdESnQ0d0Nkb1ZMOEpmRU1mZFNIRm1veC1TeWlPcmJXcGdEdkFFMktmQTZibzVFT1A4b0xmcW1DaDN2SVZrcWRFYVlFRkV3WG5ZMnE3YmpSRF9hLXozWFFsS3dlSGJoSVNTR1h3TkdOWS1HWjcyek44OXRBX1RDSjRWYl8wUU1fbFpWZlNBQmUyZ0hyNmY0MTJfNGMwazFMamxCLVVVQTZBT09GYl9RNUZnaldVaVl0cGhkRWlqNHBPMnF5RElULW5WRkVKM0FpRGNqcEhHVEIxdS1n0gHkAUFVX3lxTE1UVDdhSFFORUNSVF84dTZ4NlZSQWVVZ1VnSTFlRWZQYlBINVVLeEh3NV92T0d1V1VXaGJiVzA4S09IWEk0OGlpT0VoUmEwaDQ0VWpadzd0VmE5U0RVTkpILTZRZWhlajJzaF9lQ3BVOTNoX2YzU0J4S3NhbHhHR1JMMmI4aU1PX1FhaUlpeXIzWDNYSmFoampDejJKd2k5RVlnTTB0bTFJc0tfM0VqMWkxNkdtd01fVS1xcE9jb1p5alAyV1ZNeXBtQlhDY2xLdHpGSDlXWVhUekJfc0E1TU1GM2UyYg?oc=5"
    ],
    "signals": [
      {
        "title": "Honda Motorcycle & Scooter India sales up 5 pc at 5,42,934 units in July",
        "source": "economictimes.com"
      },
      {
        "title": "Honda Motorcycle & Scooter India sales up 5 pc at 5,42,934 units in July",
        "source": "economictimes.com"
      }
    ]
  },
  {
    "topic_id": "5032acfa-449a-42e2-83d9-2c81c135ec77",
    "title": "Infantino abandons plans to sell World Cup profits to private equity following massive pushback - AP News",
    "category": "sports",
    "coverage": "new",
    "llm_score": 5,
    "source_urls": [
      "https://news.google.com/rss/articles/CBMixgFBVV95cUxNeEwyVHhSN1FCaTBmbHlpU3FWWld0MlJKVXBIOFdlNDFNQXlrWW5PbEpycWF6X2Zha2tlMGNjQ0hkQ1lSZzZMcXJEemY5eC1RWUlURVNZSUhkQ3dUbzc2eDNXR3AtRTB0Y2RBS3ctUTAtMHRIb0xtdUstMTlUVnVvS19IaTRNVVh1bDlkWGhELWI5LVZIYXdfVDNDUXFlTUxZVmJJUVNSRXp1M0g1WHhKdm5LLTNvUXFtdkRaV0FfSHFMUG1HY1E?oc=5"
    ],
    "signals": [
      {
        "title": "Gianni Infantino \u2019has lost Uefa\u2019s confidence\u2019 after Fifa chief scraps World Cup sell-off plan",
        "source": "The Guardian"
      }
    ]
  },
  {
    "topic_id": "40ac987c-05ca-4254-a0ea-79fbbc3ee9c4",
    "title": "JSW MG July 2026 Sales Highest Ever At 8,158 Units - 80% EVs - RushLane",
    "category": "technology",
    "coverage": "new",
    "llm_score": 5,
    "source_urls": [
      "https://news.google.com/rss/articles/CBMimwFBVV95cUxNZ09MNVFVYm9yX2YzRk1YbVZsbktTcUtMQ1IwbXNqc2lmMzY5a0ZXWDR2R3hjNTYwZHlORHItUmUwRnRuOHhLTFpkRUJyRkZ2Zy1oVW5nWlVwSHNvNElHMDV5ZXNBblExMWYwQUpnall2ckR5ZWh5ang5bVRyRXcwZGRfQjhUc2FJRkxkYkpDT3E4WmpFYzhkdndtWdIBmwFBVV95cUxNZ09MNVFVYm9yX2YzRk1YbVZsbktTcUtMQ1IwbXNqc2lmMzY5a0ZXWDR2R3hjNTYwZHlORHItUmUwRnRuOHhLTFpkRUJyRkZ2Zy1oVW5nWlVwSHNvNElHMDV5ZXNBblExMWYwQUpnall2ckR5ZWh5ang5bVRyRXcwZGRfQjhUc2FJRkxkYkpDT3E4WmpFYzhkdndtWQ?oc=5",
      "https://news.google.com/rss/articles/CBMiqwFBVV95cUxOS2NQeXd6U2FNOXpzYkZzX1V0VDljdzhyUlVoa05xREMzci1XVnVhRTZWcTljbVhVS1hRVFNRa0pZZ0J0SjJEc0Z2cXJSVkdBcm84b0Z2ZkNFVjlJQ0JXMU5MMU1HTWJBR051VHR1WHVLd1VUczVwdy0wMHVvWmhNVVk0R2trSWhIQWg5OWRCdFVqWVJUeXQ1ZE1LV0FOcFB2aDBVZmlOeTdqR3fSAbABQVVfeXFMTnF5c1ltRGtNcXE4OFREUGpRbzJBR1hPUjZZdTJSR1B5OVVHLUlETjctVi1lbklxd2ZmUjBvb1lZeDF0RGZwUk0yZTY2eEV3djAzb0RlRXNwcUMxOUVubnA1UnZsVGlXLVNCa2VlSTNkZjZNZzRhT1VWWkxTTFhKZ2REYU4wZ0lqSDIteHlRVnZHc09rcW5LbXIzZFp2Um0xbExwSWE5TDdVTGNicndXZ0w?oc=5",
      "https://news.google.com/rss/articles/CBMijwFBVV95cUxQUi1rS0tyNm84dFltQkVkMDNWVEhTdU9CQTBKdkxBcElJLUZQVEtjMGNUT3pYTHVyUFNPcHE3OXp5cjdGOThfMmltZy1SMHR4cjltWDA4amtoSW52cTIyZGxGZVdKY2VfQjFvTDRlR004YkViTkRkSG5oNThKaVU5R1p2MjJqU2VfWU5JWDUxUQ?oc=5",
      "https://news.google.com/rss/articles/CBMihgJBVV95cUxOS09fQ1BKUmtTM1BNbjNYNFhUbm5JSS1RcjBnNjZZNmZPTGpaUnQyNFoyVEpJVUdwc2Y4WjVuN0pJMXFVTVZ5OGM5aGpjWFVqbTF2a3czZktvN0lOY1JaaTF1TTQ2d014bXJ5a0h0c0k2VmVQTnpFRTlHRUJyTF9tWnREQWgzQjh5Q0xSX29hMFc4bl9IYVZiUG1zdHU2bjYzUi13VmNaSUxKb0F3SGN3d19iYlZ4RFRzNC1USlZIemt2LUtIcXBPaEFJUGdhRWM5SXB4V1ZFZlhoSmVOY1lHRmZ0c09rOUhMazBSUThQbk12ZlJZTHVKUlhwM0cyT1FwWl8wUG5R0gGLAkFVX3lxTE5FX1lqN2R1M05USm5WREpvcnl3dUVuanJpaVBQNDFfMk5kVExUTExKTk9RaXZJQmtwRkNNLWphNmVNc1Y1amhwZGladjRiMm9zWXNYVGV4ZVJwUW4wTzVVZDByMXFvcEw2Y25Gbzd5WHgwMHY5R3JBU09iNGZVUlUydmdZRnYtVmNhdmNVVXM3YnJqbHlGQnAxRERMM2NQc2xjVElDck5NdlhRS0V5TXhDbDlVdXA2SVBtbm1tUE16RHRhTlNHcGN1YzVDUW1IeWtDU0FUaV94YnVLWHBEZGhXbU55cVlRN1RzUTJ6MmlLX1lqYmpGdHpZMG1tcmNfZVNNYk45OHBpaXl6MA?oc=5"
    ],
    "signals": [
      {
        "title": "JSW MG July 2026 Sales Highest Ever At 8,158 Units - 80% EVs - RushLane",
        "source": "RushLane"
      },
      {
        "title": "JSW MG Motor India Sales Soar 22% in July to 8,158 Units",
        "source": "Rediff MoneyWiz"
      },
      {
        "title": "JSW MG Motor India reports 22 per cent sales growth in July",
        "source": "telanganatoday.com"
      },
      {
        "title": "JSW MG Motor India posts highest-ever monthly wholesales in July, dispatches rise 22% to 8,158 units",
        "source": "The Economic Times"
      },
      {
        "title": "JSW MG Motor sales rise 22% to record 8,158 units in July",
        "source": "ET Auto"
      }
    ]
  },
  {
    "topic_id": "e106a41c-b361-42ae-b740-8b4a586c02cd",
    "title": "Microsoft Confirms Plans To Make 8GB RAM Run Efficiently On Windows 11 Systems, Realizing That AI Has Made Lower Memory Configurations The Norm - Wccftech",
    "category": "technology",
    "coverage": "new",
    "llm_score": 5,
    "source_urls": [
      "https://news.google.com/rss/articles/CBMieEFVX3lxTE5NV0o3Y09HNUlzWV8yYTUzc2g5aXVxQmw0NWYyUk84eHRCeHUtRjJYMEc0NmRUSU5Xa0k3VnRMaWxzay05UkRXRUhSTzdLRGpka3BXZkQyZDVWSHA1cVJJY0Y4d01oTUtXd0gyNVNKX192ZEpfVlQyddIBfkFVX3lxTFB4ckN5WUFXbHhkcHE2Q05pTmhlUm1Lelk3SWZyMl9IZUttb3R0djh3a0V2U1VsTV96eC1KcndsU2VNZ3JXQm9HeU0wdjJvaHdkSEY5UU43NlZZSW5ULVhMY2tNOUtWNDVvanFRQmRaOHhZdUlXOC02MGd0Rk51dw?oc=5"
    ],
    "signals": [
      {
        "title": "Microsoft Confirms Plans To Make 8GB RAM Run Efficiently On Windows 11 Systems, Realizing That AI Has Made Lower Memory Configurations The Norm - Wccftech",
        "source": "Wccftech"
      }
    ]
  },
  {
    "topic_id": "2b039214-a85e-4213-bb17-3f3975d1ddca",
    "title": "Full Ballard Link Line Could Take Until 2060 To Build, Sound Transit Says - The Urbanist",
    "category": "technology",
    "coverage": "new",
    "llm_score": 5,
    "source_urls": [
      "https://news.google.com/rss/articles/CBMiqwFBVV95cUxQZHlvdGxVdlY0N19hWUJDOU5CczFNaWFUUHlkdWM2ZkMzMU80alhrR0MtSC0zdUktWmx6akN0bUxDZ1MtTHNYblkxY0pYQWd3Tzc1VTN6NlRxTjBwSHFaOWhsd3k5d29TdkxuWU9fVjRfX19LWld2SVRqMUdhQ2xOVU1HVVFFT18teUhHSGI3VC1UUUtULWszNWVuamdVSzdMTFN6clJVYXBEYkU?oc=5"
    ],
    "signals": [
      {
        "title": "Sound Transit announces timeline for building light rail to Ballard",
        "source": "Seattle City Council Blog (.gov)"
      },
      {
        "title": "Sound Transit announces timeline for building light rail to Ballard",
        "source": "Seattle City Council Blog (.gov)"
      },
      {
        "title": "Sound Transit announces timeline for building light rail to Ballard",
        "source": "Seattle City Council Blog (.gov)"
      }
    ]
  },
  {
    "topic_id": "5c110681-557d-4bea-be57-6bb31735fa46",
    "title": "CWG 2026 India schedule today, August 1: Lovlina Borgohain leads 10 boxers into finals; Gulveer Singh in action - olympics.com",
    "category": "sports",
    "coverage": "new",
    "llm_score": 5,
    "source_urls": [
      "https://news.google.com/rss/articles/CBMirwFBVV95cUxQalVDNVlPY0FneElBbWo4STZMenVYaERub281akNpX0w2WndIRk83RGNycWdfM2NtVDAyMXl5aDZTWFZiMllwX2ZKV0haYWlxVlU5azRlN3ctYWhzVHB3bi1yUzBFaExZa1UwLXZ6TlBROFRvelk3NDJ4TDY5dUNXem9JNUVkNjBOdTlXNlpnRnNtUHBBTmhIQUw3ZjdxWkVJR1d3djdWTTlsa3JrSFFj?oc=5"
    ],
    "signals": [
      {
        "title": "Commonwealth Games Day 10 LIVE, India Schedule, Medal Events August 1: Full CWG 2026 Updates",
        "source": "The Indian Express"
      }
    ]
  },
  {
    "topic_id": "88561dd8-7654-4376-aed3-60d97d1d306e",
    "title": "Powerful El Nino to intensify heat on \u2018a planet already on fire\u2019: UN - Al Jazeera",
    "category": "lifestyle-health",
    "coverage": "new",
    "llm_score": 5,
    "source_urls": [
      "https://news.google.com/rss/articles/CBMiV0FVX3lxTE9qdkFCb0JpM2FFR0Y0cUpSYV92Q05pWWU1WDRSWE9kWGlLdXpIRDhRQkFFcGVFZFpBa2xqazZJbmhvdVVRb1lwOVhQTnR6TUM0bmxYZDAzSQ?oc=5"
    ],
    "signals": [
      {
        "title": "Strong El Ni\u00f1o ahead, UN weather agency warns",
        "source": "UN News"
      }
    ]
  },
  {
    "topic_id": "d68e8218-302b-4dde-a8b3-5bf1457714bd",
    "title": "Cam Young reveals what disappointed him despite shooting 61 on Friday at the Rocket Classic - hitc.com",
    "category": "sports",
    "coverage": "new",
    "llm_score": 5,
    "source_urls": [
      "https://news.google.com/rss/articles/CBMipwFBVV95cUxOc2N2MDNMZWwxVHpUZjJWMG5tZ1h3QUh1WWNEYkk1NXNJQjVOZmN1UjFyOTZMNmxVTWduQ2I2Nkg5TTlJdldhTVl2WUhrS2FxVlBSNWZUYTVtZi02QzJ1UUllSk1ZQzZTLV9YaGU4cUdxNEFMMnk4bFBsbFBKWDBlNlRqRXh3MjlCV0RrUDlMVWp4TzRlYTJqcUh3ck5Db0h1c1dHUEtwcw?oc=5"
    ],
    "signals": [
      {
        "title": "Cameron Young seizes share of lead after shooting 61 at Rocket Classic",
        "source": "ESPN"
      }
    ]
  },
  {
    "topic_id": "bfe481ad-8662-4b42-bf53-4a3772a85439",
    "title": "Chipotle CEO says chain is making \u2018meaningful progress\u2019 on a major customer concern - New York Post",
    "category": "food",
    "coverage": "new",
    "llm_score": 5,
    "source_urls": [
      "https://news.google.com/rss/articles/CBMihwFBVV95cUxQb2NydFlJSUF6dGlVczFhUjlpWi1TS1lDQVJfdlQ3UlIwZ1ZtRmVGWnNNXzVIc0RwQlBDWjBEVEZFSm1qOUxWS2FUem1kRElqRmhMT3lOdFJHTWlKd2Vudm0xaExXR2JSVC12M2Z1WXFsWjQ3U0JTUG1GM3pIUnJHbmFLSlNFd1k?oc=5"
    ],
    "signals": [
      {
        "title": "Chipotle stock jumps as chain hikes same-store sales forecast, says cyclospora fears hit sales in late July",
        "source": "CNBC"
      }
    ]
  },
  {
    "topic_id": "87ff4710-2546-4e29-832b-bf4730da69ba",
    "title": "Air India upgrades Canada operations with brand-new Boeing 787-9s; Announces a new Mumbai-Toronto Seasonal route",
    "category": "travel",
    "coverage": "new",
    "llm_score": 4,
    "source_urls": [
      "https://livefromalounge.com/air-india-upgrades-canada-operations-with-brand-new-boeing-787-9s-announces-a-new-mumbai-toronto-seasonal-route/"
    ],
    "signals": [
      {
        "title": "Air India upgrades Canada operations with brand-new Boeing 787-9s; Announces a new Mumbai-Toronto Seasonal route",
        "source": null
      }
    ]
  },
  {
    "topic_id": "4d3eb752-0bc6-4d23-b8be-abb6fe4a9889",
    "title": "IndiGo collaborates with Incredible India to reimagine India\u2019s tourism story",
    "category": "travel",
    "coverage": "new",
    "llm_score": 4,
    "source_urls": [
      "https://www.thehindu.com/life-and-style/indigo-collaborates-with-incredible-india-to-reimagine-indias-tourism-story/article71293922.ece"
    ],
    "signals": [
      {
        "title": "IndiGo collaborates with Incredible India to reimagine India\u2019s tourism story",
        "source": null
      },
      {
        "title": "IndiGo collaborates with Incredible India to reimagine India\u2019s tourism story",
        "source": null
      }
    ]
  },
  {
    "topic_id": "4c8f4ed7-8b88-45d5-b732-3fffab531299",
    "title": "She closed her Pilates studio to chase a mountaineering dream, then tragedy struck - CNN",
    "category": "lifestyle-health",
    "coverage": "new",
    "llm_score": 4,
    "source_urls": [
      "https://news.google.com/rss/articles/CBMisgFBVV95cUxOWnZ1cmFyaVluTEJtaEJIVnc4WHlScFRZd3FwNWpWTUxLNVh0ckNnb241LS1uTXF3aG11bGRqb0h0alZWMlY0WmpzMUdCci1FNFVCRlc0dkE1RW9ZWldBenNxMEJlajdIRUZfNE5YbEVNS05LLUJ5bzR2T2JLRXhnZUlJRHE1VnBQa25WOWNzR2lJbHNyT1BQNkVEZDBrdmoxb21vVVBCaXdZVjR3NGhfcG53?oc=5",
      "https://news.google.com/rss/articles/CBMilgFBVV95cUxOaFNmOVlKRFU4T09HUjB6SjNrQmdjWkFRdHZxZ2J4cnRab3dzZnZ6blNNblp5WlMwTkZ4WFJvQlNyZzR4anZoVVBzQWNSLURwSlVWMUcwTlRlWUFWM0I1YXNMakxTT0VFdS1WdnczX1pncnBqa0NTWE1zN2tMYVpWX1ByWWlKV2lna2JkRkZ1aEQ5aVdVQUE?oc=5",
      "https://news.google.com/rss/articles/CBMiWkFVX3lxTFA4Rk9IU0VCZUY4dC05SWFtb0dXRWdTZGM0aVZ5R1lJbDF3YlcyNFZENEpkLXI0WkJCdHM2UGN2LXhDLUFaYlM4QlRfSDlOdl9KeV85d01Jc0xwdw?oc=5"
    ],
    "signals": [
      {
        "title": "Search resumes for missing climbers after avalanche on Pakistan\u2019s Broad Peak",
        "source": "NBC News"
      },
      {
        "title": "She closed her Pilates studio to chase a mountaineering dream, then tragedy struck - CNN",
        "source": "CNN"
      },
      {
        "title": "Mountaineer Nirmal Purja killed in Pakistan avalanche, his company says",
        "source": "BBC"
      },
      {
        "title": "She closed her Pilates studio to chase a mountaineering dream, then tragedy struck - CNN",
        "source": "CNN"
      },
      {
        "title": "Mountaineer Nirmal Purja killed in Pakistan avalanche, his company says",
        "source": "BBC"
      }
    ]
  },
  {
    "topic_id": "4e416090-0db7-483e-b5b3-cc4db7cc5f51",
    "title": "All Eyes On Yash\u2019s Toxic Trailer - Gulte",
    "category": "entertainment",
    "coverage": "new",
    "llm_score": 4,
    "source_urls": [
      "https://news.google.com/rss/articles/CBMioAJBVV95cUxOOGM2NHRUR3BmNDFEZ1BVZXJwQTFQaWtkSHdkWVJDWkxhamxSR3k2TVNkejZEbVNIVDdVYU1QWk5SUEVUaVpmVnp2cE0tR09lUlNIVURYWlc3ZUVkbjAzaVFKd1MtSXFOWkhuTXJfLTRHNE9OeTYxUk8wM3FUZ3lvZnJiMjdJRHAyOE16bU03V1FGeFN4SFoydUpxcFgyUlc0TkNlSnhjSEM1TmJ3TjJlT1N5SzJaVGZSMnVOQXZQTG4wX0oyc1NnX0JvNDVLYXBpdWIxWm1zeHF6bkJSWFBhaGk1Xzh1OUtDcUpOSW5PWTg0Z014ZVBhRVltNl96bXgzT3JxUGN1bnl1WVptYy1PMW9HTFk1QnB0bjVmZlFrSFU?oc=5",
      "https://news.google.com/rss/articles/CBMiekFVX3lxTE1XenpxLW1pV3Bwbi1yUThFdkJXNGhOeEh1MUh3RVRJN3hORWFmRFRkc0cxT3JMQUpqaS01U19lMlUxeU9FcDRRZnN6Y2xSQ3JOQXFOOW85S1FCaHlYUlh0Y1h4NEtwSW5NSG1ocFRwaDhUZXhSamo1VlRn0gF_QVVfeXFMUGtMYUxLMHJneDRqNjlPU28yMnFrOXNvSWQxai0zV1ZUTEdvR29aMFcxeDJqVGxLQTNOU25VRE5NMldvNFl4Wkw3UEFJZDhzbENVbFZLaERRVldtd3I1dncyODY5TVdaeHF2ZGRFX0RIQWlyZE54RlVhNzVkOFZiSQ?oc=5",
      "https://news.google.com/rss/articles/CBMikAJBVV95cUxONjVQYV9RX3FxaUtsNkNGbUdzOUlwYjg2UDhRcWk5dTJyRmgxcDZ4SkVHVjlRZzJrLU5WaThjMHdKWlNEODhaWVVzSFM3YmVITUpYejZSb2VxcExadF9UR1NrMm84UlZ1ZzR0d0JaSHdqX0VyUEZmTXZTYV90dDQ5akk1U2dDQ05PV0ozTHNqSUM1SjJtSUk5enQxMGJFOElWb1hPUzJnTGxycklUTkpwMW5WMkxLaTR6MGpNRGdSWG1zYklHTTAyVUpPb1JEbmFRb3oxYTYzdFJDTVlKT2NheldTU3pmMXNIc1Zkd1dGMVNUTV8wcnlidmZIU0p4TTlLZ19iMHpIS1VZbHREekZBUNIBlgJBVV95cUxPZFlMcm9WR1cxZXBPaHNRdXNFZVZWdVVyYmpPRTRfRDhWbWFkWmZWRVVSRWtoc3BLS2FpcFRIbXNWTVQ1YW5vTWRsMXdIMEhQTVpGemd1ZDMweTdpZkFfZERXLXNLcVdqRUwzRlB0TC00OXROcm80d2NsQ2dLYURFT3FVOFdGMWlxbnc0UWdmN0dHUmMzcll3VDRZZzNmSHE5WVM0Yy0wMEN5SVN0X1hfSDVaVjFkX3pQSS1ZSkVrdVBPaV90TlZnZDhyQTdDRzFLOXZBeFJpRWU1WUJEcU8zLUhpMEN6ZW9nYzR1UEt4dmlmeWlsaXE2cTRtTHVhUG5UY1FWaHBDanVmMTZmVllIWXFIMHRTZw?oc=5",
      "https://news.google.com/rss/articles/CBMirgFBVV95cUxNR25aVl9zenczQkhqYlNuWHRPX2F3eWRzM1dfa0hrclc4TkpDbXRRNm1BeVF1LTZNaS16bjBUbm5CX3ozOHNMSnJZRlRaV0NjUXg5WTdlNlcxZ0h6QXNDbm9KTm44ME1HT3M0LUk5TTBpUTJkYU1CVzlLclhPV0t3aGZhWnpBQW1CV2c3WDVUa0JMQ1V1c0pkQ0pvdWZJWDRPOXZTd1p1S09pQThSTXfSAbYBQVVfeXFMTXhULU5TejhnLTlWcUViZUlWOEFGVkFodmY4azFqRE9VeU5RRzFCN3FaQ2lGOTJ3clNGeVMzUFAwZUYtSFctTzRzMTVObk1LZlAzSEx1NlpMMmN5VmlXSVdvRmh1S1F4VTdpc2ZfQnVVcDBGRktlblVLSDJhenJOcDhnelVsMHdEeHpmSWN3dzJONmpkaFZJMGc3a2pfS1FLVTVUREZnN2F1TXpGS0p2cVRYTGlBVVE?oc=5"
    ],
    "signals": [
      {
        "title": "Yash and Geetu Mohandas' 'Toxic' trailer to release on August 8 ahead of theatrical debut on August 26",
        "source": "timesofindia.indiatimes.com"
      },
      {
        "title": "All Eyes On Yash\u2019s Toxic Trailer - Gulte",
        "source": "Gulte"
      },
      {
        "title": "Yash's Toxic trailer to release on August 8, striking new poster teases Raya's mysterious world: 'The...",
        "source": "Moneycontrol.com"
      },
      {
        "title": "Toxic Trailer To Release On August 8, New Posters Of Yash And Kiara Advani Out",
        "source": "NDTV"
      },
      {
        "title": "Yash's Toxic trailer to be out soon: Makers plan grand Bengaluru trailer event",
        "source": "India Today"
      }
    ]
  },
  {
    "topic_id": "ea78bbe4-b19e-411c-b943-9d3adbbd1b29",
    "title": "#Chiru158 BTS: Bobby, The Master Of Mass Entertainment - Gulte",
    "category": "entertainment",
    "coverage": "new",
    "llm_score": 4,
    "source_urls": [
      "https://news.google.com/rss/articles/CBMimwFBVV95cUxNUE5wZFBKQ3lhMVZxVHdwd0xxRmxXa1Y1RmxuQmhReThCbWEtWFd1Q0RZeVBQYlppQ2J5QmdFaGNxakVIU2NFQzFzYktvX3M2UDVza1NscldYc09yTERSSFVYdFpIUkdNX0wzZ1V2S01JOEZwVlhNTkc1MER5ektfcV9ubUQ0QjJYUXFwV0dMRWJGcDJ0ZHVlTG11ONIBoAFBVV95cUxPalJnX0hGT2lmX3lodmZ2RjNoRW5XV0hhdkVJWmRDMlZSQmJSVjZGSUdtOFBiOU9kT1Y5UVNHQk5CbDZnTk0zRHEtV1ZpVUNjaHFfd1ZrdVJRMWYyT0haeEtfR2JNeFg2enc1MFdHUzcxUDh0a2VMRFVzMXptWDFNamt5MGxjZ1drM2F6a2JLbWE1RFFJcFpDc2JaNllCZlp6?oc=5",
      "https://news.google.com/rss/articles/CBMioAFBVV95cUxOWmg0VmJJQk5XZG5QLWt6Qm9ockZKbWVONmtpYzhxTFd5M0lEcWNQVmZ3Q2NWemxzWUtRRHN3NmhYNE1tcTBtWUJ5aFBjZUYxZnBQN3BVRHYtNXRzWWFQQTN3Ry03MUNEbExURUlrNk5CaU4yaDQ4ZndNMlY0NGpvS0c4clNNRW95bmFtODMzWElTTEJHQ0VvenE5Wk5Rdmxk0gGmAUFVX3lxTE80SmRYWGM0Zm5EMHFoVGlUcmVCbng0NTlkbzJNelZSWkMxaTNhUjg0dzBjbWJ1SHR6am5Bd2JmUDNDQzYtclhLMkZDZ0c0NUxHOFBpMHBWQmY2VVJfcEZXMXpHeXd4TWd0WndGT1pGaU5WbzBOTFMwR19mY2dORGJJcmFOWWJlbUpTWWZoamhrdm9NaHRnLUFhVXNPUW9teXVtdlFmdEE?oc=5",
      "https://news.google.com/rss/articles/CBMihAFBVV95cUxPeE9JbElKZ0VOTkNkSGVOeDc1WnBnSWxzQUlrWmZrRExDT0hPd3pvTXFFQWJxSnFhRUNCYlRiWlFHNXhWX0FUMFJRRVlic3BsQ2s3SFlUZ0xJbVpmTGpfUTc1RzJZQUJ2RFNGc3VjU1RtMGgxcmJ1cjRnWkNiYlE5YUw0R3k?oc=5",
      "https://news.google.com/rss/articles/CBMilAFBVV95cUxPd0hLOU04ZXQzcWt6MFYwYll5ZzNCd1NfTzNDcVRVRWplV1RKZ2tnQnJPM0tNOUJOTDZodl9WWnYwdzk4dW14cGpMUHJKWkxfM3UtTEZGTzRoTXFlUWNuZDhreEd2a2pBekpfekZyOWhtZkJmSEpqc1hjM1l2LUFUSHQ1bTBHdG5zbTdmMXd4VGVYb1M40gGaAUFVX3lxTFBoMi1mREtBRzF3MERNM09taDQySEdDc1FJV2NOS3pMNXBoNktOYWRGdk40bENlVHJmOGZRWm0yNWZkN1BROEdDMXZPUGlPcXFEWGo3NTFEWDZDRURadjhma1F5ZmxYNEdZV3BhakJYR2prUFk2YXVqM0ZnVkg1bE14aEN3QXI3NnRPYk1tcXJrNjlRZUlRaUF5cFE?oc=5"
    ],
    "signals": [
      {
        "title": "Mega158 BTS: Bobby Kolli is crafting an epic",
        "source": "Tupaki English"
      },
      {
        "title": "Mega158: Chiranjeevi's title and glimpse to be unveiled on his birthday - Telugu Cinema | News,",
        "source": "telugucinema.com"
      },
      {
        "title": "Mega158 BTS Video: Bobby Kolli\u2019s admirable dedication",
        "source": "Telugu360"
      },
      {
        "title": "#Chiru158 BTS: Bobby, The Master Of Mass Entertainment - Gulte",
        "source": "Gulte"
      }
    ]
  },
  {
    "topic_id": "30ba2558-d82f-4b00-853c-6fae2af12663",
    "title": "Thousands take to Kyiv's main street, firm on calls for defence minister's return - Reuters",
    "category": "nri-world",
    "coverage": "new",
    "llm_score": 4,
    "source_urls": [
      "https://news.google.com/rss/articles/CBMiYEFVX3lxTE5UNHBOWlo0aXh3cVVEMmFOYTVNZ1dQaXpJQ2hlU0FMSHAyTDA0eXNZZnJuajk0MmFSbFN3VHRGSjlVNERNNWxENUlOUVlUQXdPR09fZnZPbUg5ZFZ2Nl9kSA?oc=5",
      "https://news.google.com/rss/articles/CBMixgFBVV95cUxNZW1mMFBqTUpOUDRUdXJKaEhpVDJMWXNKRmh2MFRsZUFOZkVDOUxSdXBKdGRuLW1FdlNZVzdiR1h1Z2FCbmc5R2ItelZ5a2Q1bUVxRjBWNjNQNEVmT1d0OWU0elctclhJdWdvUmRMNDZWT09zdzNPX3hPV0hVYU5oVlA2NF92c2RxRTRUTGRKTTE1Q0tWQVNvSG8tNUZBdktPaEFpWW1GaG5kWkp3Y3lpWlJWX1BXV0JUVjF5QmRZMVZmQXVhbWc?oc=5",
      "https://news.google.com/rss/articles/CBMivwFBVV95cUxNV2hkMEFrSXJHOV9TV3liakRCbm9aWWExUWhTUVFfMjR2OE9ET2JnemdjMUItYVRBQUhzWnM3T19JMUhPUXdnY2FKZFVybVlaTndraDFaRzdaWmZKTjVYRW5NaHdVY3NRYi16b2RXa01UN0Q5VVBzQUE0TFBCZTU2T3BrUUMxaEd6clpRSDhHVS05Rm1mMk9CbWJlY0dEdHRBak5nRlZHZVRqcXJqcnVoeHRlRXowX1RHd1psNFVSSQ?oc=5"
    ],
    "signals": [
      {
        "title": "Ukrainian Military Leadership Changes",
        "source": "Every CRS Report"
      },
      {
        "title": "Ukraine\u2019s Former Defense Minister Links His Dismissal to Defense Procurement Reforms",
        "source": "Bloomberg.com"
      },
      {
        "title": "Thousands rally in Kyiv, renew calls for defense minister's return",
        "source": "news.cgtn.com"
      },
      {
        "title": "Ukrainian Military Leadership Changes",
        "source": "Every CRS Report"
      },
      {
        "title": "Ukraine\u2019s Former Defense Minister Links His Dismissal to Defense Procurement Reforms",
        "source": "Bloomberg.com"
      }
    ]
  },
  {
    "topic_id": "c961b7b7-67a2-4684-a65a-cca240affbc0",
    "title": "Nenu Local, Cinema Choopistha & Nenu Ready: VV Vinayak - Gulte",
    "category": "entertainment",
    "coverage": "new",
    "llm_score": 4,
    "source_urls": [
      "https://news.google.com/rss/articles/CBMiowFBVV95cUxNQjlPQ19lTGRnSG5nM1dQSnhZMTFoaENVMnBaanVRMmlEM3k5SEd4LWdlU3QwZ0xDcmRiV0pseUlIQXd0dlNpN1U0c0Q2MTRFZkZsbFBFeVl2b1Z4a1kxUlBnRWRaN2VrR3BoMTNTVmx1M1h3VU9URC16bVY4UklnOGlid0xvMmh4M0k3T0x2a2pPM2tjVVF3M182Y2ZLbXg2YUZR?oc=5",
      "https://news.google.com/rss/articles/CBMifkFVX3lxTE5pcURobDlaaC1ReDdpeDFGdWJhRXp2TEhIYV95aXdPSURCM1E5eXZkcWFTU3U5N2I4cDY1R2t1b1FEQ1d5b3BUdHJGVVZVeG9UWDRHNmVHQXM2dmxNMm0zMUNtNFR1cG5STTZjZjVweTBXQzFreGhyRWFxU19sUQ?oc=5",
      "https://news.google.com/rss/articles/CBMiggJBVV95cUxNNlRmd0V4cU9BdnUycTYwWGdLYUhLYlZXYktOY1FSMl80Sl9sR0sweGM3ck5sUFk1aFdIbXJrTFlpcTdNTDFpWHZLMDRxRnI2bS1TbUp4eW9PeUtpUjF5c3ZTS2habk5OaFppUGVYUXdiTjNLd3lDdS1qS0RWWXFPenpCWVIwRHlTRkdsSzN4OVlWYXdnT0lmVTlEbGhRSm5KZ2pKbm9IUFBRQTRuTzBWdzVaSEc2Z1FFUzh2NlBuaVZMb19ickJ2ZTd2bEZ6enBPYkxSaDZSTnBSR2d3MmNpX3Z0Q2Y4QV9VRGVGSFhsZ3pndU00VDFYNGFBXzUyX2JpM1E?oc=5",
      "https://news.google.com/rss/articles/CBMi0wFBVV95cUxPWkMzUnJ6aFNlXzBXcDJyLUpFTldTQW5VcWE0MnZXMmhObkRSNDdJNVFYRlV6R3pfWXkxVmVvZWhSaW1BdTZmU3dhb1VLQUtyckpmNnhHQXZQZ0daSS10X1Q4Sk1pNDVOdlVndldWSWNhWFdPdzA0LXBzcnRFUnBFZDFmR2VLbl9VZDRkWFFoY1ZiWV9iLXNEZDlzSlVhYnM2VWdSNXhqZzR0NjdvZ0VnLVR4RUhSMzlwTmtBa0FERG9MVllLUkI0b0NocXlWYjZUQ2VZ0gHbAUFVX3lxTE80ZWlmOFZialhva1RhejZFX1MtRllTQ1k4WkstVktNVHJiMG02SnZ3TjhzZ0xMT2RxMDY4OGZ6UEFYdlRiSDZvb1JwR1FRakFFZGVJdDlpcGNLUUdOSnJaVUpnb1NLM1RCMnlRTENQcmdiRVF5OFExdG9sYldPVndVNzNubk8xUGhVYl9oM0o4emVkaFBDLXdkd3MxbmhKd0haRkFCcjRFR0dKcGI3OW9GSHlBc2E3d2tPd19vRS1ocmFqM19vUkpnb25UOFlGUHd2dUxTdnh1OUpVNA?oc=5"
    ],
    "signals": [
      {
        "title": "Nenu Ready's Merupule Song impresses with vibrance",
        "source": "TeluguOne.com"
      },
      {
        "title": "Nenu Ready is a complete hilarious ride \u2013 Havish",
        "source": "Telugu360"
      },
      {
        "title": "Konchem Konchem From Nenu Ready Turns Up The Heat",
        "source": "Telugu Times"
      },
      {
        "title": "Nargis Fakhri Makes Tollywood Debut With Nenu Ready, Director Explains Why He Chose Her",
        "source": "NDTV"
      },
      {
        "title": "Nenu Local, Cinema Choopistha & Nenu Ready: VV Vinayak - Gulte",
        "source": "Gulte"
      }
    ]
  },
  {
    "topic_id": "db236108-8846-4ee2-99fb-6da1493eec61",
    "title": "Game Devs Put Together An Itch.io Bundle Of Over 100 Games With Proceeds Going To Help Laid-Off Colleagues - Kotaku",
    "category": "nri-world",
    "coverage": "new",
    "llm_score": 4,
    "source_urls": [
      "https://news.google.com/rss/articles/CBMiwgFBVV95cUxQWWFzbEVfaFBnUnpLNGdIUmlON3ZiV1NGQkxjNUVRdmszbHhzSzNBdkJ6RW9UdEFzeURtYnVyNFgwWGROeThCb1Z0RWljNTFUdVBVaGJQNjd4QUJjYXFBLUJ1VTlsemozdlBvb2I1Ti1iTjNkMUZNRzFNZ0V3UG9EZVBaMzhHbXM1Yk1xRkJKWk0wbVVjSlhUa2dvazhKMWR1OE9lc3NEWElZeGM5LTV5dUx1OVBpUEJJd2JJdDdWVXZQQQ?oc=5"
    ],
    "signals": [
      {
        "title": "Truck chaos, climbing with dual-mouse controls and other new indie games worth checking out",
        "source": "Engadget"
      },
      {
        "title": "Truck chaos, climbing with dual-mouse controls and other new indie games worth checking out",
        "source": "Engadget"
      },
      {
        "title": "Truck chaos, climbing with dual-mouse controls and other new indie games worth checking out",
        "source": "Engadget"
      }
    ]
  },
  {
    "topic_id": "c4791d07-fc0b-4034-8f41-abf3bc3dc76e",
    "title": "Thanks to India, U.S. & China Remain Neck-and-Neck in Global Popularity. 1.4B People Keep The Balance Even - EurAsian Times",
    "category": "nri-world",
    "coverage": "new",
    "llm_score": 4,
    "source_urls": [
      "https://news.google.com/rss/articles/CBMifEFVX3lxTFBDWGRtRzloc1pud3pqSm5XQXhaWWtIUHlrbEE3eGM3aEFLVm85R1ZwMkNpS3NiSVNOSlJ0bDJlM3VDZ0p0dlpBSnZzWENBcmlIZElkbVMtMVFzdlF2VmRJYjV0YS04OF9RUlp0MWpzZzA4bTMwMC03TWk3amw?oc=5",
      "https://news.google.com/rss/articles/CBMilAFBVV95cUxNbUJScUZYeWxGTnVkYTVXdllranBmZmFSdVZrcGZ6UDFGMjRDX3UtRGp2YjQyLWNHUDRReVI5ekxISi1VSG5VOHhBeU9ESHhBS3JBNmtFMjdFZm9FLXpaVzhHcjZrREtQY3F6WWtBVmJ3dTh3VndUU1h3cC15NUV0eDFFM2V6anhqYjJ3UnZNckNtTzdW?oc=5"
    ],
    "signals": [
      {
        "title": "China outranks the U.S. in global favorability. What happened?",
        "source": "CCTV.com English"
      },
      {
        "title": "How public opinion of US fell in two years, while China held firm",
        "source": "Asia News Network"
      }
    ]
  },
  {
    "topic_id": "33b3ebac-8ee8-4217-a264-d31380fffa87",
    "title": "Karnataka exports first air shipment of Totapuri and Neelam mangoes from Kolar to Maldives",
    "category": "food",
    "coverage": "new",
    "llm_score": 3,
    "source_urls": [
      "https://www.thehindu.com/news/national/karnataka/karnataka-exports-first-air-shipment-of-totapuri-and-neelam-mangoes-from-kolar-to-maldives/article71294103.ece"
    ],
    "signals": [
      {
        "title": "Karnataka exports first air shipment of Totapuri and Neelam mangoes from Kolar to Maldives",
        "source": null
      },
      {
        "title": "Karnataka exports first air shipment of Totapuri and Neelam mangoes from Kolar to Maldives",
        "source": null
      }
    ]
  }
];

log("Loaded " + candidates.length + " candidates");

phase("write");

function buildPrompt(c) {
  var sigs = (c.signals || []).map(function(s) {
    return '  - "' + s.title + '" (' + (s.source || "unknown") + ')';
  }).join("\n");
  var topicShort = c.topic_id.substring(0, 8);

  return 'Write ONE professional news article for The Videshi (Indian diaspora publication) and publish it to the database.\n\n' +
    'ENV SETUP (use in every exec call): set -a; source ~/workspace/.env.supabase; source ~/workspace/.env.openai; source ~/workspace/.env.pexels 2>/dev/null; set +a\n\n' +
    'CANDIDATE:\n' +
    '- topic_id: ' + c.topic_id + '\n' +
    '- title: ' + c.title + '\n' +
    '- category: ' + c.category + '\n' +
    '- coverage: ' + c.coverage + '\n' +
    '- source_urls: ' + JSON.stringify(c.source_urls) + '\n' +
    '- signals:\n' + sigs + '\n\n' +
    'STEP 1 — RESEARCH\n' +
    'Use browser_search to find 2-3 actual news articles about this topic. Read at least 2 via browser_open to get facts, quotes, numbers, and context. Cross-reference sources.\n\n' +
    'STEP 2 — WRITE THE ARTICLE\n' +
    'Write like a senior Reuters/Bloomberg journalist.\n\n' +
    'HEADLINE: 8-14 words. Clear, informative. No clickbait.\n' +
    'SUBHEADLINE: 1-2 sentence summary for card display.\n' +
    'SLUG: URL-friendly from headline (lowercase, hyphens, max 8 words).\n\n' +
    'HTML BODY (500-800 words):\n' +
    '1. Key takeaways FIRST (REQUIRED, NO heading tag inside):\n' +
    '   <div class="key-takeaways"><ul><li>Bullet 1</li><li>Bullet 2</li><li>Bullet 3</li></ul></div>\n' +
    '2. Opening paragraph — the news lead (what happened, who, why it matters)\n' +
    '3. <h2> section — Context & Background\n' +
    '4. <h2> section — Impact & Analysis\n' +
    '5. Diaspora angle paragraph (only if natural for ' + c.category + ' — never force it)\n' +
    '6. <h2> section — What\'s Next\n\n' +
    'Pull quotes (1-2 max for impactful quotes):\n' +
    '<blockquote class="pull-quote"><p>"quote text"</p><cite>— Name, Title</cite></blockquote>\n\n' +
    'WRITING RULES:\n' +
    '- Write from source material only — no fabrication\n' +
    '- Cite sources naturally: "according to Reuters", "the ministry announced"\n' +
    '- Use specific numbers, dates, names — concrete details\n' +
    '- NO filler: "In a significant development", "It is worth noting"\n' +
    '- NO qualifiers: "importantly", "notably", "interestingly"\n' +
    '- Vary sentence length. Short punchy + longer analytical.\n' +
    '- For markets-finance: straight financial journalism, no forced NRI framing\n' +
    '- For entertainment: depth, not gossip\n\n' +
    'STEP 3 — INSERT INTO DATABASE\n' +
    'Create a Python script to build the JSON (handles HTML escaping properly):\n\n' +
    'import json, subprocess, datetime\n\n' +
    'article = {\n' +
    '    "headline": "YOUR HEADLINE",\n' +
    '    "subheadline": "YOUR SUBHEADLINE",\n' +
    '    "body": YOUR_HTML_BODY_STRING,\n' +
    '    "slug": "your-slug",\n' +
    '    "category": "' + c.category + '",\n' +
    '    "vertical": "' + c.category + '",\n' +
    '    "tags": ["tag1", "tag2", "tag3"],\n' +
    '    "sources": ["source_url_1", "source_url_2"],\n' +
    '    "image_url": None,\n' +
    '    "image_caption": None,\n' +
    '    "image_attribution": None,\n' +
    '    "word_count": WORD_COUNT,\n' +
    '    "diaspora_angle": "One sentence summary",\n' +
    '    "topic_id": "' + c.topic_id + '",\n' +
    '    "llm_score": ' + c.llm_score + ',\n' +
    '    "published_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),\n' +
    '    "article_type": "breaking",\n' +
    '    "status": "published"\n' +
    '}\n' +
    'with open("/tmp/article_' + topicShort + '.json", "w") as f:\n' +
    '    json.dump(article, f)\n\n' +
    'Then insert via curl:\n' +
    'set -a; source ~/workspace/.env.supabase; set +a\n' +
    'curl -sS "$SUPABASE_URL/rest/v1/p2_articles" -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" -H "Content-Type: application/json" -H "Prefer: return=representation" -d @/tmp/article_' + topicShort + '.json\n\n' +
    'Extract the "id" UUID from the response.\n\n' +
    'STEP 4 — IMAGE SOURCING\n' +
    'set -a; source ~/workspace/.env.supabase; source ~/workspace/.env.pexels 2>/dev/null; set +a\n' +
    'cd ~/workspace/the-videshi-news/pipeline && python3 -u image_sourcer.py --slug YOUR_SLUG --apply\n\n' +
    'STEP 5 — POLISH\n' +
    'set -a; source ~/workspace/.env.supabase; source ~/workspace/.env.openai; set +a\n' +
    'cd ~/workspace/the-videshi-news/pipeline && python3 -u article-polish.py --article-id ARTICLE_UUID\n\n' +
    'STEP 6 — UPDATE TOPIC STATUS\n' +
    'set -a; source ~/workspace/.env.supabase; set +a\n' +
    'curl -sS "$SUPABASE_URL/rest/v1/p2_topics?id=eq.' + c.topic_id + '" -X PATCH -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" -H "Content-Type: application/json" -d \'{"status":"published","last_article_id":"ARTICLE_UUID"}\'\n\n' +
    'If image or polish fails, continue — the article is published and readable.\n' +
    'Return the article_id (UUID), slug, headline, and category.';
}

var writeResults = await parallel(
  candidates.map(function(c, i) {
    return function() {
      return agent(buildPrompt(c), {
        key: "art-" + i,
        label: c.category + ": " + c.title.substring(0, 45),
        phase: "write",
        timeoutMs: 720000,
        schema: {
          type: "object",
          properties: {
            article_id: { type: "string" },
            slug: { type: "string" },
            headline: { type: "string" },
            category: { type: "string" },
            error: { type: "string" }
          },
          required: ["headline"]
        }
      });
    };
  }),
  { concurrency: 5 }
);

var published = writeResults.filter(function(r) { return r !== null && r.article_id; });
var failed = writeResults.filter(function(r) { return r === null || !r.article_id; });
log("Write phase: " + published.length + " published, " + failed.length + " failed/null");

phase("enrich");

var pubInfo = JSON.stringify(published.map(function(p) {
  return { headline: p.headline, article_id: p.article_id, slug: p.slug, category: p.category };
}));

await agent(
  'Run post-processing for The Videshi. Continue even if individual scripts fail.\n\n' +
  'Published articles:\n' + pubInfo + '\n\n' +
  '1. Social enrichment:\n' +
  'set -a; source ~/workspace/.env.supabase; source ~/workspace/.env.openai; source ~/workspace/.env.google-ai 2>/dev/null; source ~/workspace/.env.pexels 2>/dev/null; source ~/workspace/.env.twitterapi-io; source ~/workspace/.env.apify; source ~/workspace/.env.youtube; set +a\n' +
  'cd ~/workspace/the-videshi-news/pipeline\n' +
  'timeout 180 python3 -u enrich-on-publish.py --hours 3 --apply\n' +
  'timeout 600 python3 -u enrich-articles.py --hours 3 --apply\n\n' +
  '2. Image backfill:\n' +
  'set -a; source ~/workspace/.env.supabase; source ~/workspace/.env.pexels 2>/dev/null; set +a\n' +
  'cd ~/workspace/the-videshi-news/pipeline\n' +
  'python3 -u image_sourcer.py --backfill --hours 3 --apply\n\n' +
  '3. Storyline linking:\n' +
  'set -a; source ~/workspace/.env.supabase; set +a\n' +
  'curl -sS "$SUPABASE_URL/rest/v1/storylines?select=id,title,slug,status,article_count&status=in.(active,emerging)" -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY"\n' +
  'For each published article, if it matches an active storyline, insert into storyline_articles and update the storyline article_count and last_article_at.\n\n' +
  'Report enrichment summary and storyline links.',
  {
    key: "enrich",
    label: "Enrichment + storylines",
    phase: "enrich",
    timeoutMs: 900000
  }
);

phase("publish");

await agent(
  'Rebuild feeds and deploy:\n' +
  'cd ~/workspace/the-videshi-news\n' +
  'set -a; source ~/workspace/.env.supabase; set +a\n' +
  'python3 -u pipeline/prebuild-feeds.py\n' +
  'git add -A public/data/ && git commit -m "feeds: v3 writer aug-1" && git push origin main\n' +
  'Report success or failure.',
  {
    key: "deploy",
    label: "Rebuild feeds + deploy",
    phase: "publish",
    timeoutMs: 300000
  }
);

return {
  message: "V3 pipeline: " + published.length + "/" + candidates.length + " articles published",
  articles: published.map(function(r) { return { headline: r.headline, category: r.category, slug: r.slug }; }),
  failed_count: failed.length
};
