# RSS Feed Validation Report — July 16, 2026

## FAILED FEEDS (tried, could not get working RSS)

These either return empty (exit 28 = connection timeout through proxy), 
block bot user agents, or have no RSS feed at all:

### Food
| Name | URLs Tried | Result |
|---|---|---|
| Bon Appétit | /feed/rss, /feed | Timeout (Condé Nast blocks) |
| Serious Eats | /feed, /feed/rss, discovered API URL | All timeout or empty |
| Food52 | /blog.rss, /feed | Returns HTML, no RSS link |
| The Infatuation | /feed | Timeout |
| Epicurious | /feed/rss | Timeout (Condé Nast blocks) |
| Saveur | /feed/ | Timeout |
| Veg Recipes of India | /feed/ | Timeout |
| Cook With Manali | /feed/ | Returns HTML |
| Food Network | /fn-dish/feed | Returns HTML |

### Travel  
| Name | URLs Tried | Result |
|---|---|---|
| Condé Nast Traveler | /feed/rss | Timeout (Condé Nast blocks) |
| Travel + Leisure | /feeds/all, /feed/rss | Timeout |
| Lonely Planet | /feed.xml, /blog/feed | Not RSS |
| Atlas Obscura | /feeds/latest | Timeout |
| Condé Nast Traveller India | /feed/ | Timeout |
| View from the Wing | /feed/ | Timeout |
| India Today Travel | /travel/rss | Not RSS |
| Outlook Traveller | /rss | Not RSS |

### Lifestyle & Health
| Name | URLs Tried | Result |
|---|---|---|
| Well+Good | /feed/ | Timeout |
| Healthline | /rss/health-news, /feed | Timeout/empty |
| Vogue India | /feed/, /rss | Timeout (Condé Nast) |
| Yoga Journal | /feed/ | Timeout |
| Mint Lounge | /rss/feed, /rss/all | Timeout/not RSS |
| WebMD | rssfeeds URL | Empty |
| India Today Lifestyle | /lifestyle/rss | Not RSS |
| MensXP | /rss | Not RSS |

### Entertainment
| Name | URLs Tried | Result |
|---|---|---|
| Screen Rant | /feed/ | Timeout |
| Collider | /feed/ | Timeout |
| IndieWire | /feed/ | Timeout |
| BollywoodLife | /feed/, /rss.xml | Timeout/not RSS |
| FilmiBeat | /rss/*.xml | Not RSS |

## Notes
- Many "timeout" failures (exit 28) are likely the egress proxy being blocked
  by Cloudflare or similar CDN protections. These feeds may work fine from 
  a different server/IP.
- Condé Nast properties (Bon Appétit, Epicurious, CNT, Vogue) all block.
- Dotdash Meredith properties (Serious Eats discovered URL) also block.
