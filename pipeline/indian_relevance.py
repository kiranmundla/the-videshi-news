"""
Indian/South Asian business relevance detector.
Word-boundary matching + prefix matching for compound words.
Used by expand-directory.py and cleanup-directory.py.
"""
import re

# ~200+ common Indian/South Asian surnames + distinctly Indian first names
INDIAN_SURNAMES = {
    "acharya","agarwal","aggarwal","agrawal","ahuja","anand","arora","bajaj","bajpai",
    "bala","balakrishnan","banerjee","bansal","bapat","basu","bedi","bhat","bhatia",
    "bhatt","bhattacharya","bhattacharyya","bose","chakraborty","chand","chandra",
    "chandrasekhar","chatterjee","chaudhary","chaudhry","chauhan","chopra","choudhury",
    "dalal","das","dasgupta","deshpande","desai","deshmukh","devi","dhawan","dixit",
    "doshi","dube","dubey","dutta","dwivedi","gajjar","gandhi","ganguly","garg",
    "ghosh","gill","gopal","goswami","goyal","grover","gulati","gupta","hegde",
    "hussain","iyer","jagdish","jain","jaiswal","jha","jog","joshi","kadam","kalra",
    "kamat","kapoor","kapil","kar","kaur","kaushal","khanna","khatri","kohli","krishna",
    "krishnamurthy","kulkarni","kumar","kumari","lal","mahajan","maheshwari","malhotra",
    "malik","manchanda","mani","mathur","mazumdar","mehra","mehrotra","mehta","menon",
    "mishra","misra","mitra","modi","mohan","mukherjee","mundla","murthy","murty",
    "naidu","nair","nanda","narang","narayan","natarajan","nayak","nayar","oberoi",
    "padmanabhan","pal","pandey","pandit","pant","parekh","parikh","parmar","patel",
    "pathak","patil","pillai","prasad","purohit","raghavan","rai","raj","rajan",
    "rajput","ram","ramachandran","raman","ramaswamy","rana","ranga","rani","rao",
    "rastogi","rathore","rattan","ravindran","rawat","ray","reddy","sachdev","saha",
    "sahni","saluja","sanghvi","sapra","saraf","sarkar","saxena","sen","sengupta",
    "sethi","shah","shankar","sharma","shekhawat","shenoy","sheth","shinde","shivaji",
    "shukla","sidhu","singh","sinha","sodhi","soni","sood","sreenivasan","sridhar",
    "srinivas","srinivasan","srivastava","subramanian","subramaniam","sundaram",
    "suresh","swami","swaminathan","talwar","tandon","taneja","tewari","thakkar",
    "thakur","tiwari","trehan","tripathi","trivedi","upadhyay","vaidya","varma",
    "varghese","venkatesh","venkatraman","verma","vij","vohra","walia","yadav",
    # Common first names that are distinctly Indian (used as business names)
    "rashmi","priya","pooja","neha","nisha","anita","sunita","deepa","meena","rekha",
    "ravi","sanjay","rajesh","suresh","ramesh","ganesh","dinesh","mahesh","naresh",
    "ashok","vinod","anil","sunil","manoj","pramod","satish","girish","harish",
}

# Indian food / restaurant keywords
INDIAN_FOOD_WORDS = {
    "masala","tandoori","tandoor","biryani","dosa","chai","thali","dhaba","naan",
    "samosa","chaat","paneer","korma","vindaloo","tikka","roti","paratha","lassi",
    "chutney","pakora","idli","uttapam","rajma","kebab","kabab","curry",
    "mughlai","chettinad","hyderabadi","madras","bombay","calcutta","kolkata",
    "delhi","mumbai","lucknow","jaipur","kerala","malabar","udupi","momos",
    "rasam","pongal","haleem","nihari","mithai","laddu","gulab","jalebi",
    "pav","bhaji","vada","dahi","raita","kulfi","kheer",
    "indian restaurant","indian grocery","indian food","indian cuisine",
    "indian kitchen","indian grill","indian cafe","indian sweets",
    "south indian","north indian",
}

# Indian cultural / business keywords
INDIAN_CULTURAL_WORDS = {
    "mandir","gurudwara","gurdwara","kovil","ashram","vedic","vedanta",
    "hindu","sikh","jain","swaminarayan","iskcon",
    "ganesh","ganesha","lakshmi","durga","shiva","vishnu","hanuman",
    "saraswati","pooja","puja","aarti","kirtan","satsang","bhajan",
    "diwali","navratri","dussehra",
    "bollywood","mehndi","mehendi","rangoli","sangeet",
    "shaadi","lehenga","saree","sari","salwar","kurta","sherwani","dupatta",
    "ayurveda","ayurvedic","panchkarma","panchakarma",
    "bharat","hindustan","swadeshi",
    "tamil","telugu","kannada","malayalam","bengali","marathi","gujarati",
    "punjabi","rajasthani","sindhi","nepali",
    "indian immigration","indian law","indian cpa","indian tax",
    "indian beauty","indian salon","desi",
    "bharatanatyam","kathak","kuchipudi","odissi","carnatic","hindustani",
    "tabla","sitar","veena","harmonium",
    "henna","threading",
}

ALL_KEYWORDS = INDIAN_FOOD_WORDS | INDIAN_CULTURAL_WORDS

# Pre-compile word-boundary regex for each keyword
_KW_PATTERNS = {kw: re.compile(r'\b' + re.escape(kw) + r'\b', re.IGNORECASE) for kw in ALL_KEYWORDS}

# For compound-word prefix matching: keywords >= 5 chars
_PREFIX_KEYWORDS = sorted([kw for kw in ALL_KEYWORDS if len(kw) >= 5 and ' ' not in kw], key=len, reverse=True)


def _has_indian_surname(words):
    """Check if any word in the name matches a known Indian surname."""
    for w in words:
        clean = w.rstrip(".,;:()").lstrip("(")
        if clean in INDIAN_SURNAMES:
            return True
    return False


def _has_indian_keyword(name_lower, words):
    """Check if name contains any Indian keyword via word-boundary OR prefix match."""
    # 1. Word-boundary match (handles multi-word keywords and exact matches)
    for kw, pat in _KW_PATTERNS.items():
        if pat.search(name_lower):
            return True

    # 2. Prefix match for compound words (e.g. "ayurvedashram", "tandoorilicious")
    #    Only for single-word keywords >= 5 chars to avoid false positives
    for w in words:
        clean = w.rstrip(".,;:()").lstrip("(")
        if len(clean) < 5:
            continue
        for kw in _PREFIX_KEYWORDS:
            if clean.startswith(kw) and len(clean) > len(kw):
                return True

    return False


def is_indian_business(name, category):
    """
    Returns (is_relevant, skip_quality_check)
    - is_relevant: True if this appears to be an Indian/South Asian business
    - skip_quality_check: True if we should skip rating/review thresholds
    """
    if not name:
        return False, False

    name_lower = name.lower().strip()
    words = [w.lower().rstrip(".,;:()").lstrip("(") for w in name.split()]

    has_surname = _has_indian_surname(words)
    has_keyword = _has_indian_keyword(name_lower, words)

    if category == "Doctors & Healthcare":
        # Indian doctor = include, skip quality check
        if has_surname or has_keyword:
            return True, True
        return False, False

    if category == "Religious Services":
        # Temples, gurudwaras = include, skip quality check
        if has_keyword or has_surname:
            return True, True
        return False, False

    # Everything else: must be Indian, quality check applies
    if has_surname or has_keyword:
        return True, False

    return False, False


if __name__ == "__main__":
    tests = [
        ("Dr. Suresh Patel", "Doctors & Healthcare"),
        ("A Plus Dentistry LA", "Doctors & Healthcare"),
        ("Houstonian Dental", "Doctors & Healthcare"),
        ("Bombay Nights Ballroom", "Event Venues"),
        ("Temple Nightclub San Francisco", "Event Venues"),
        ("Hari Om Mandir", "Religious Services"),
        ("Bollywood Salon", "Beauty & Grooming"),
        ("Great Tutoring LLC", "Education & Tutoring"),
        ("Shaadi 'R' Us", "Event Venues"),
        ("Bagichaa", "Catering & Food"),
        ("SOL Yoga Fort Lauderdale", "Yoga & Wellness"),
        ("Ayurvedashram", "Doctors & Healthcare"),
        ("Rashmi Satyadeo, CPA", "Tax & Accounting"),
        ("CORE954 Lagree Fitness", "Yoga & Wellness"),
        ("Momo and Curry Kitchen", "Catering & Food"),
        ("Indigenous Hair Designs", "Beauty & Grooming"),
        ("Curry Leaf Indian Restaurant", "Catering & Food"),
        ("Desi Spice House", "Catering & Food"),
        ("Dr. Shashank Sinha", "Doctors & Healthcare"),
        ("Voyage Healthcare - Plymouth", "Doctors & Healthcare"),
        ("Indian Health Board Medical", "Doctors & Healthcare"),
        ("Tandoorilicious Grill", "Catering & Food"),
        ("Bharatanatyam Academy of Dance", "Education & Tutoring"),
    ]
    for name, cat in tests:
        rel, skip = is_indian_business(name, cat)
        tag = "✅" if rel else "❌"
        skip_tag = " (skip quality)" if skip else ""
        print(f"  {tag} {name} [{cat}]{skip_tag}")
