INSERT INTO story_queue (status, story_brief, priority, category, diaspora_relevance, raw_article_ids)
VALUES
('pending', '{
  "headline": "Vijay Fails Majority Test: No Swearing-In Tomorrow as IUML Withholds Support",
  "why_it_matters": "Major setback for Vijay TVK government formation in Tamil Nadu",
  "key_facts": [
    "Vijay not invited to take oath despite earlier reports",
    "TVK failed to produce letter of support from VCK and IUML",
    "IUML says it has not decided to back TVK",
    "This is Vijays third meeting with Governor Arlekar",
    "TVK needs 118 MLAs but cannot prove majority"
  ],
  "category": "news",
  "diaspora_relevance": "high",
  "suggested_search_queries": [
    "Vijay TVK oath ceremony Tamil Nadu May 2026",
    "IUML TVK support Tamil Nadu government",
    "Tamil Nadu Governor Arlekar TVK majority proof"
  ],
  "sources": ["The Federal", "ANI"]
}'::jsonb, 1, 'news', 'high', '{}'),
('pending', '{
  "headline": "Suvendu Adhikari Elected BJP Legislature Leader in West Bengal After Historic Win",
  "why_it_matters": "BJP consolidates power in Bengal with Adhikari as legislative leader",
  "key_facts": [
    "Suvendu Adhikari elected leader of BJP legislative party in West Bengal",
    "Adhikari thanked PM Modi and Amit Shah after election",
    "He received support of all BJP MLAs in the state",
    "BJP won 206 of 294 seats in historic Bengal victory"
  ],
  "category": "news",
  "diaspora_relevance": "high",
  "suggested_search_queries": [
    "Suvendu Adhikari BJP legislature leader West Bengal 2026",
    "West Bengal BJP chief minister selection",
    "Bengal BJP government formation 2026"
  ],
  "sources": ["ANI", "The Federal"]
}'::jsonb, 1, 'news', 'high', '{}');
