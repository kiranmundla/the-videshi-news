#!/usr/bin/env python3
"""Seed spiritual_teachers table and link daily_wisdom entries."""
import json, os, subprocess, urllib.parse

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

TEACHERS = [
    {
        "slug": "sadhguru",
        "name": "Sadhguru",
        "tradition": "Hindu / Yoga",
        "bio": "Sadhguru Jaggi Vasudev is an Indian yogi, mystic, and founder of the Isha Foundation. A bestselling author and influential speaker, he has addressed the United Nations, World Economic Forum, and TED. He is known for making ancient yogic science accessible to modern audiences worldwide.",
        "journey": "Born in Mysore, India, Sadhguru had a spontaneous spiritual experience at age 25 while sitting on Chamundi Hill — a moment of overwhelming, boundless consciousness that lasted hours. This experience transformed him completely. He spent the next years deepening his inner work before beginning to teach yoga. In 1992, he founded the Isha Foundation near Coimbatore, building it into one of India's largest volunteer-run spiritual organizations. He consecrated the Dhyanalinga, a powerful meditative space, in 1999.",
        "youtube_url": "https://www.youtube.com/@sadhguru",
        "website_url": "https://isha.sadhguru.org",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Sadhguru-Jaggi-Vasudev.jpg/330px-Sadhguru-Jaggi-Vasudev.jpg",
        "org_name": "Isha Foundation",
        "born": "1957",
        "origin": "Mysore, India",
        "key_teachings": "Inner Engineering, yoga and meditation as tools for inner transformation, consecrated spaces (Dhyanalinga), ecological activism (Rally for Rivers, Save Soil)",
        "followers_desc": "Over 11 million YouTube subscribers, Isha Foundation operates in 300+ cities across 60+ countries"
    },
    {
        "slug": "sri-sri-ravi-shankar",
        "name": "Sri Sri Ravi Shankar",
        "tradition": "Hindu / Yoga",
        "bio": "Sri Sri Ravi Shankar is an Indian spiritual leader, humanitarian, and founder of the Art of Living Foundation. His breathing technique, Sudarshan Kriya, is practiced by millions worldwide. He has led peace negotiations and conflict resolution efforts in multiple countries.",
        "journey": "Born in Papanasam, Tamil Nadu, Sri Sri showed an early affinity for spirituality — reportedly reciting parts of the Bhagavad Gita by age four. He studied with Maharishi Mahesh Yogi before embarking on his own path. In 1981, after a period of ten days of silence on the banks of the Bhadra River in Shimoga, he emerged with Sudarshan Kriya, a rhythmic breathing technique. He founded the Art of Living Foundation in 1981 and the International Association for Human Values in 1997.",
        "youtube_url": "https://www.youtube.com/@ArtOfLiving",
        "website_url": "https://www.artofliving.org",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/Sri_Sri_Ravi_Shankar_-_new.jpg/330px-Sri_Sri_Ravi_Shankar_-_new.jpg",
        "org_name": "Art of Living Foundation",
        "born": "1956",
        "origin": "Papanasam, Tamil Nadu, India",
        "key_teachings": "Sudarshan Kriya, breath-based meditation, stress elimination, service and compassion, conflict resolution",
        "followers_desc": "Art of Living programs in 180+ countries, over 500 million people reached"
    },
    {
        "slug": "mooji",
        "name": "Mooji",
        "tradition": "Hindu / Yoga",
        "bio": "Mooji (Anthony Paul Moo-Young) is a Jamaican-born British spiritual teacher rooted in Advaita Vedanta. Known for his warm, direct pointing to the Self, he guides seekers through self-inquiry in the tradition of Ramana Maharshi. His satsangs draw thousands from around the world.",
        "journey": "Born in Port Antonio, Jamaica, Mooji moved to London as a teenager. He worked as a street portrait artist and teacher before a chance encounter with a Christian mystic in 1987 opened him to a deeper spiritual calling. In 1993, he met his guru, Papaji (H.W.L. Poonja), a direct disciple of Ramana Maharshi, in Lucknow, India. Under Papaji's guidance, Mooji experienced a profound recognition of the Self. He began holding satsangs in London and eventually established Monte Sahaja, a retreat center in Portugal.",
        "youtube_url": "https://www.youtube.com/@moaboreal",
        "website_url": "https://mooji.org",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Mooji_Wikipedia_Photo.jpg/330px-Mooji_Wikipedia_Photo.jpg",
        "org_name": "Mooji Foundation",
        "born": "1954",
        "origin": "Port Antonio, Jamaica",
        "key_teachings": "Self-inquiry in the Advaita tradition, direct pointing to awareness, satsang as spiritual practice",
        "followers_desc": "Over 2 million YouTube subscribers, Monte Sahaja retreat center in Portugal"
    },
    {
        "slug": "dalai-lama",
        "name": "Dalai Lama",
        "tradition": "Buddhist",
        "bio": "Tenzin Gyatso, the 14th Dalai Lama, is the spiritual leader of Tibetan Buddhism and a Nobel Peace Prize laureate. He has spent over six decades advocating for Tibetan autonomy, interfaith dialogue, and compassion as a foundation for world peace.",
        "journey": "Born in 1935 in Taktser, a small village in northeastern Tibet, he was recognized at age two as the reincarnation of the 13th Dalai Lama. He was enthroned in Lhasa at age four and began rigorous monastic education. After the Chinese invasion of Tibet, he assumed full political power at age 15. Following the failed 1959 Tibetan uprising, he escaped to India, where he established the Tibetan government-in-exile in Dharamsala. He was awarded the Nobel Peace Prize in 1989 for his nonviolent struggle for Tibet's freedom.",
        "youtube_url": "https://www.youtube.com/@DalaiLama",
        "website_url": "https://www.dalailama.com",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fb/The_Dalai_Lama_in_2012.jpg/330px-The_Dalai_Lama_in_2012.jpg",
        "org_name": "Office of His Holiness the Dalai Lama",
        "born": "1935",
        "origin": "Taktser, Tibet",
        "key_teachings": "Compassion as universal ethic, mindfulness, interdependence, nonviolence, secular ethics for the modern world",
        "followers_desc": "Nobel Peace Prize 1989, spiritual leader to millions of Tibetan Buddhists worldwide"
    },
    {
        "slug": "thich-nhat-hanh",
        "name": "Thich Nhat Hanh",
        "tradition": "Buddhist",
        "bio": "Thich Nhat Hanh (1926–2022) was a Vietnamese Zen Buddhist monk, peace activist, and one of the most influential spiritual teachers of the 20th century. He coined the term 'engaged Buddhism' and founded the Plum Village tradition. Martin Luther King Jr. nominated him for the Nobel Peace Prize in 1967.",
        "journey": "Born in central Vietnam in 1926, he was ordained as a monk at age 16. During the Vietnam War, he chose to engage directly with the suffering around him rather than retreat to the monastery — founding schools, training social workers, and rebuilding bombed villages. His peace advocacy led to exile from Vietnam in 1966. He settled in France and founded Plum Village, a mindfulness practice center in the Dordogne. He continued teaching worldwide until a stroke in 2014, returning to Vietnam in 2018 to spend his final years at the temple where he was ordained. He passed away in January 2022.",
        "youtube_url": "https://www.youtube.com/@plumvillage",
        "website_url": "https://plumvillage.org",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Thich_Nhat_Hanh_12_%28cropped%29.jpg/330px-Thich_Nhat_Hanh_12_%28cropped%29.jpg",
        "org_name": "Plum Village Community of Engaged Buddhism",
        "born": "1926",
        "origin": "Thừa Thiên, Vietnam",
        "key_teachings": "Mindfulness in daily life, engaged Buddhism, interbeing, walking meditation, deep listening and loving speech",
        "followers_desc": "Founded Plum Village with 10+ monasteries worldwide, bestselling author of 100+ books"
    },
    {
        "slug": "deepak-chopra",
        "name": "Deepak Chopra",
        "tradition": "Interfaith / Modern",
        "bio": "Deepak Chopra is an Indian-American author, physician, and alternative medicine advocate. One of the best-known figures in mind-body wellness, he has written over 90 books translated into 43 languages, blending Ayurveda, quantum physics concepts, and meditation into an accessible wellness framework.",
        "journey": "Born in New Delhi, Chopra trained as an endocrinologist in the United States. In the 1980s, a meeting with Maharishi Mahesh Yogi drew him toward Transcendental Meditation and Ayurvedic medicine. He left conventional medical practice to found the Chopra Center for Wellbeing in 1996. His 1994 bestseller 'Ageless Body, Timeless Mind' brought him mainstream fame. He went on to develop a global wellness brand spanning books, apps, retreats, and digital health platforms, reaching millions seeking the intersection of science and spirituality.",
        "youtube_url": "https://www.youtube.com/@DeepakChopra",
        "website_url": "https://www.deepakchopra.com",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/Deepak_Chopra_by_Gage_Skidmore.jpg/330px-Deepak_Chopra_by_Gage_Skidmore.jpg",
        "org_name": "Chopra Global",
        "born": "1946",
        "origin": "New Delhi, India",
        "key_teachings": "Mind-body healing, Ayurveda, meditation for wellness, quantum consciousness, total well-being",
        "followers_desc": "90+ books, 43 languages, millions of followers across digital platforms"
    },
    {
        "slug": "jay-shetty",
        "name": "Jay Shetty",
        "tradition": "Interfaith / Modern",
        "bio": "Jay Shetty is a British-Indian author, former monk, and purpose coach who spent three years as a Vedic monk in India before becoming one of the most popular wellness voices online. His podcast 'On Purpose' is one of the world's top health podcasts.",
        "journey": "Born in London to Indian parents, Shetty was drawn to meditation and service during college at Cass Business School. At 22, he left behind a corporate path to live as a monk in Mumbai, sleeping on the floor, meditating for hours, and studying ancient Vedic philosophy. After three years, his teachers encouraged him to share what he'd learned with the wider world. He returned to London and began creating viral videos on wisdom and purpose. His 2020 book 'Think Like a Monk' became a #1 New York Times bestseller.",
        "youtube_url": "https://www.youtube.com/@JayShettyPodcast",
        "website_url": "https://jayshetty.me",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/Jay_Shetty_Headshot_2021.jpg/330px-Jay_Shetty_Headshot_2021.jpg",
        "org_name": None,
        "born": "1987",
        "origin": "London, England (Indian heritage)",
        "key_teachings": "Purpose-driven living, monk mindset in modern life, intentional relationships, daily meditation and gratitude",
        "followers_desc": "50+ million followers across platforms, #1 NYT bestselling author, host of 'On Purpose' podcast"
    },
    {
        "slug": "eckhart-tolle",
        "name": "Eckhart Tolle",
        "tradition": "Interfaith / Modern",
        "bio": "Eckhart Tolle is a German-born spiritual teacher and author of 'The Power of Now' and 'A New Earth,' two of the most influential spiritual books of the 21st century. Oprah Winfrey called 'A New Earth' the most important book she has ever recommended. His teachings focus on transcending the ego and living in present-moment awareness.",
        "journey": "Born in Germany in 1948, Tolle suffered from severe depression and anxiety through his twenties. One night at age 29, in a state of near-suicidal despair, he experienced a profound inner transformation. The thought 'I cannot live with myself any longer' split into two — the 'I' and the 'self' — and he realized he was the awareness behind thought, not the thoughts themselves. He awoke the next morning in deep peace. He spent the next several years sitting on park benches in a state of bliss, integrating the experience before he began teaching. 'The Power of Now,' published in 1997, became a global phenomenon after Oprah's endorsement.",
        "youtube_url": "https://www.youtube.com/@EckhartTolle",
        "website_url": "https://eckharttolle.com",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/af/Eckhart_Tolle_front.jpg/330px-Eckhart_Tolle_front.jpg",
        "org_name": "Eckhart Teachings",
        "born": "1948",
        "origin": "Lünen, Germany",
        "key_teachings": "Present-moment awareness, ego transcendence, the pain-body, stillness and inner space, consciousness evolution",
        "followers_desc": "'The Power of Now' translated into 52 languages, 'A New Earth' sold 5+ million copies, Oprah's #1 book pick"
    },
    {
        "slug": "amma",
        "name": "Amma",
        "tradition": "Hindu / Yoga",
        "bio": "Mata Amritanandamayi, known worldwide as Amma ('Mother'), is an Indian spiritual leader and humanitarian renowned for her embrace — she has hugged over 40 million people around the world. Her charitable network has donated over $4.6 billion to causes including disaster relief, housing, healthcare, and education.",
        "journey": "Born in 1953 in a small fishing village in Kerala, India, Amma displayed deep compassion from childhood, giving away food and clothing to the poor despite her own family's poverty. She began spontaneously embracing people who came to her with suffering — a practice unheard of in Indian tradition. By her teens, she was entering ecstatic devotional states (bhava samadhi). Her ashram in Amritapuri, Kerala, grew from a small hut into a global spiritual organization. She established Amrita University, hospitals, and the Embracing the World humanitarian network. She has addressed the United Nations and Parliament of World Religions multiple times.",
        "youtube_url": "https://www.youtube.com/@AmmaAmritanandamayi",
        "website_url": "https://amma.org",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/M%C4%81t%C4%81_Amrit%C4%81nandamay%C4%AB_Dev%C4%AB.jpg/330px-M%C4%81t%C4%81_Amrit%C4%81nandamay%C4%AB_Dev%C4%AB.jpg",
        "org_name": "Mata Amritanandamayi Math (Embracing the World)",
        "born": "1953",
        "origin": "Parayakadavu, Kerala, India",
        "key_teachings": "Selfless love and compassion, the embrace (darshan), devotional practice (bhakti), humanitarian service as spiritual practice",
        "followers_desc": "Hugged 40+ million people, $4.6 billion in charitable giving, ashrams and centers in 40+ countries"
    },
    {
        "slug": "pema-chodron",
        "name": "Pema Chödrön",
        "tradition": "Buddhist",
        "bio": "Pema Chödrön is an American Tibetan Buddhist nun and one of the most beloved Western Buddhist teachers. A bestselling author of 'When Things Fall Apart,' she is known for her accessible, warm teachings on working with difficult emotions, uncertainty, and compassion.",
        "journey": "Born Deirdre Blomfield-Brown in New York City in 1936, she worked as an elementary school teacher and mother of two before her life shifted. After her second marriage ended, she encountered the teachings of Chögyam Trungpa Rinpoche, one of the first Tibetan masters to teach extensively in the West. She was ordained as a Buddhist nun in 1974 and became one of Trungpa's closest students. In 1984, she became the director of Gampo Abbey in Nova Scotia — the first Tibetan Buddhist monastery in North America for Westerners. Her books, drawn from her own struggles and breakthroughs, have reached millions.",
        "youtube_url": "https://www.youtube.com/@PemaChodronFoundation",
        "website_url": "https://pemachodronfoundation.org",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/Pema_chodron_2007_cropped.jpg/330px-Pema_chodron_2007_cropped.jpg",
        "org_name": "Gampo Abbey / Pema Chödrön Foundation",
        "born": "1936",
        "origin": "New York City, USA",
        "key_teachings": "Embracing groundlessness, tonglen (compassion practice), working with fear and uncertainty, the wisdom of no escape",
        "followers_desc": "Bestselling author, director of first Western Tibetan Buddhist monastery in North America"
    },
    {
        "slug": "bk-shivani",
        "name": "BK Shivani",
        "tradition": "Hindu / Yoga",
        "bio": "BK Shivani (Shivani Verma) is a senior Rajyoga meditation teacher with the Brahma Kumaris and one of India's most popular motivational speakers. Her TV show 'Awakening with Brahma Kumaris' ran for over 700 episodes, reaching millions of households across India.",
        "journey": "Born in Pune, India, Shivani was an electronics engineer before her spiritual path called. She encountered the Brahma Kumaris in her twenties and began practicing Rajyoga meditation. Her clarity and relatability led to the TV series 'Awakening with Brahma Kumaris' on Aastha TV, co-hosted with BK Suraj Bhai. The show made Rajyoga meditation accessible to everyday families dealing with relationships, anger, stress, and parenting. She was awarded the Nari Shakti Puraskar (Woman Power Award) by the President of India in 2019.",
        "youtube_url": "https://www.youtube.com/@bkshivani",
        "website_url": "https://www.brahmakumaris.org",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/BK_Shivani.jpg/330px-BK_Shivani.jpg",
        "org_name": "Brahma Kumaris",
        "born": "1972",
        "origin": "Pune, India",
        "key_teachings": "Rajyoga meditation, emotional intelligence, conscious relationships, positive thinking, soul consciousness",
        "followers_desc": "700+ TV episodes, millions of views on YouTube, Nari Shakti Puraskar awardee"
    },
    {
        "slug": "gaur-gopal-das",
        "name": "Gaur Gopal Das",
        "tradition": "Hindu / Yoga",
        "bio": "Gaur Gopal Das is an Indian monk, motivational speaker, and author associated with ISKCON (International Society for Krishna Consciousness). Known for his storytelling ability and humor, his talks on purpose, relationships, and happiness have been viewed hundreds of millions of times online.",
        "journey": "Born in Maharashtra, India, Gaur Gopal Das studied electrical engineering at the College of Engineering Pune and briefly worked at Hewlett-Packard. But a growing spiritual calling drew him to ISKCON. At 22, he made the unusual decision to renounce his corporate career and become a full-time monk. He has lived as a monk at ISKCON's Radha Gopinath temple in Mumbai for over two decades, balancing deep devotional practice with a global speaking ministry. His 2020 book 'Life's Amazing Secrets' became an international bestseller.",
        "youtube_url": "https://www.youtube.com/@gaaboreal",
        "website_url": "https://www.gaurgopaldas.com",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/GaurGopal_Das.jpg/330px-GaurGopal_Das.jpg",
        "org_name": "ISKCON (International Society for Krishna Consciousness)",
        "born": "1973",
        "origin": "Maharashtra, India",
        "key_teachings": "Purpose-driven living, Bhagavad Gita wisdom, relationships and gratitude, happiness through service",
        "followers_desc": "8+ million social media followers, bestselling author, one of the most-watched monks online"
    },
    {
        "slug": "omar-suleiman",
        "name": "Omar Suleiman",
        "tradition": "Islamic",
        "bio": "Omar Suleiman is an American Muslim scholar, author, and founder of the Yaqeen Institute for Islamic Research. He is one of the most influential Muslim voices in America, known for bridging Islamic scholarship with social justice advocacy.",
        "journey": "Born and raised in Louisiana to Palestinian parents, Suleiman began studying Islam as a teenager, traveling to study with scholars in the Middle East and Southeast Asia. He founded the Yaqeen Institute in 2016 to produce rigorous, peer-reviewed Islamic research accessible to everyday Muslims. He has served as an imam, led interfaith vigils, opened the US House of Representatives with a prayer, and advocates for civil rights. His book 'Allah Loves' and the Yaqeen video series have reached millions seeking to deepen their faith.",
        "youtube_url": "https://www.youtube.com/@YaqeenInstitute",
        "website_url": "https://yaqeeninstitute.org",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d1/ImamOmarSuleiman2.jpg/330px-ImamOmarSuleiman2.jpg",
        "org_name": "Yaqeen Institute for Islamic Research",
        "born": "1986",
        "origin": "New Orleans, Louisiana, USA (Palestinian heritage)",
        "key_teachings": "Islamic spirituality and social justice, building faith through knowledge, patience and gratitude in Islam, community service",
        "followers_desc": "10+ million followers, opened US House of Representatives with prayer, Yaqeen reaches millions"
    },
    {
        "slug": "basics-of-sikhi",
        "name": "Basics of Sikhi",
        "tradition": "Sikh",
        "bio": "Basics of Sikhi is a global Sikh education platform founded by Jagraj Singh (1982–2017), dedicated to making Sikh philosophy accessible to everyone. Through street interviews, lectures, and animated explainers, the platform has become the largest English-language Sikh education channel.",
        "journey": "Jagraj Singh, a British Sikh from London, started Basics of Sikhi as a grassroots project to share the teachings of the Sikh Gurus in plain English. He would set up a table on London's streets with a sign saying 'Ask a Sikh anything' and engage passersby in deep conversations about life, purpose, and spirituality. These interactions went viral. Jagraj passed away in 2017 from cancer at age 35, but the organization he built continues his mission. The team produces content on Gurbani, Sikh history, and spiritual practice, carrying forward Jagraj's vision of an accessible, open-door Sikhi.",
        "youtube_url": "https://www.youtube.com/@basicsofsikhi",
        "website_url": "https://www.basicsofsikhi.com",
        "image_url": None,
        "org_name": "Basics of Sikhi",
        "is_org": True,
        "born": None,
        "origin": "London, United Kingdom",
        "key_teachings": "Sikh philosophy made accessible, Gurbani education, interfaith dialogue, living the Guru's teachings daily",
        "followers_desc": "Largest English-language Sikh education platform, 500K+ YouTube subscribers"
    },
    {
        "slug": "nanak-naam",
        "name": "Nanak Naam",
        "tradition": "Sikh",
        "bio": "Nanak Naam is a meditation and spiritual education platform rooted in Sikh teachings, offering guided meditations and talks on the wisdom of the Sikh Gurus. Founded by Bhai Satpal Singh, it makes Sikh meditation practices accessible worldwide.",
        "journey": "Bhai Satpal Singh grew up immersed in Sikh spiritual tradition and dedicated his life to sharing the meditative practices embedded in Gurbani. He founded Nanak Naam to help people experience the transformative power of Naam Simran (meditation on the Divine Name) — the core spiritual practice in Sikhism. Through online classes, retreats, and YouTube teachings, Nanak Naam has introduced thousands of people worldwide to Sikh meditation, often drawing connections between Sikh wisdom and universal spiritual principles.",
        "youtube_url": "https://www.youtube.com/@NanakNaam",
        "website_url": "https://nanaknaam.org",
        "image_url": None,
        "org_name": "Nanak Naam",
        "is_org": True,
        "born": None,
        "origin": "United Kingdom",
        "key_teachings": "Naam Simran (meditation on the Divine Name), Gurbani wisdom, inner peace through Sikh practice",
        "followers_desc": "800K+ YouTube subscribers, global meditation community"
    },
    {
        "slug": "byron-katie",
        "name": "Byron Katie",
        "tradition": "Interfaith / Modern",
        "bio": "Byron Katie is an American speaker and author who teaches 'The Work,' a method of self-inquiry using four questions to examine stressful thoughts. Time magazine called her 'a spiritual innovator for the new millennium.' Her approach has helped millions worldwide find freedom from suffering through questioning their own beliefs.",
        "journey": "Born in Breckenridge, Texas in 1942, Katie spent her thirties spiraling into a decade of severe depression, paranoia, rage, and self-loathing. For the last two years she was often unable to leave her bedroom. Then one morning in February 1986, while in a halfway house, she experienced a life-changing realization. She discovered that when she believed her thoughts, she suffered, but when she questioned them, she didn't. 'Freedom is as simple as that,' she says. People began seeking her out, and she developed The Work — four questions and a turnaround — as a way to share what she'd found. She has since brought The Work to prisons, hospitals, corporations, universities, and millions worldwide.",
        "youtube_url": "https://www.youtube.com/@theworkofbk",
        "website_url": "https://thework.com",
        "image_url": None,
        "org_name": "Byron Katie International",
        "born": "1942",
        "origin": "Breckenridge, Texas, USA",
        "key_teachings": "The Work (four questions and turnaround), questioning stressful beliefs, loving what is, freedom from suffering through self-inquiry",
        "followers_desc": "Bestselling author of 'Loving What Is,' taught The Work to millions in 30+ years"
    },
    {
        "slug": "sn-goenka",
        "name": "S.N. Goenka",
        "tradition": "Buddhist",
        "bio": "Satya Narayan Goenka (1924–2013) was an Indian-Burmese teacher who revived the ancient practice of Vipassana meditation and made it available worldwide through free 10-day residential courses. There are now 300+ Vipassana centers across the globe, all operating on a donation basis with no fees charged.",
        "journey": "Born into a wealthy Indian business family in Burma (Myanmar), Goenka suffered from severe migraines that no doctor could cure. In 1955, he reluctantly attended a Vipassana meditation course with Sayagyi U Ba Khin, a Burmese government official and meditation master in the lineage of Ledi Sayadaw. The practice not only cured his migraines but transformed his life entirely. After 14 years of training under U Ba Khin, Goenka moved to India in 1969 and began teaching Vipassana. His first course in Mumbai attracted both Hindus and Buddhists. He established the first Vipassana center, Dhamma Giri, in Igatpuri in 1976. By the time of his death in 2013, his organization had grown to 300+ centers worldwide, all run entirely by volunteers with no fees — only donations from grateful students.",
        "youtube_url": "https://www.youtube.com/@VipassanaOrg",
        "website_url": "https://www.dhamma.org",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/The_Kalyanmitra_Satyanarayan_Goenka_who_brought_Vipassana_Meditation_technique_to_India_after_2500_years_is_seen_with_his_wife_while_speaking_at_a_talk_on_%22Values_in_Education_-_Good_Governance_through_Vipassana_Meditation%22_in.jpg/330px-thumbnail.jpg",
        "org_name": "Vipassana International Academy (Dhamma.org)",
        "born": "1924",
        "origin": "Mandalay, Burma (Indian heritage)",
        "key_teachings": "Vipassana meditation (observation of bodily sensations), impermanence (anicca), equanimity, the art of living, non-sectarian practice",
        "followers_desc": "300+ Vipassana centers worldwide, all free of charge, millions of students across 94 countries"
    },
    {
        "slug": "sri-m",
        "name": "Sri M",
        "tradition": "Hindu / Yoga",
        "bio": "Sri M (Mumtaz Ali Khan) is an Indian spiritual teacher, author, and social reformer whose unique journey spans Hindu, Sufi, and Buddhist traditions. Born a Muslim, he was drawn to the Himalayas and Vedantic philosophy from childhood. His Walk of Hope — a 7,500 km walk from Kanyakumari to Kashmir in 2015-16 — was a powerful statement for peace and interfaith harmony.",
        "journey": "Born as Mumtaz Ali Khan in Trivandrum, Kerala, Sri M showed deep spiritual inclinations from early childhood, drawn to the Upanishads and Hindu philosophy despite his Muslim upbringing. At age 19, he traveled to the Himalayas where he met his master, Maheshwarnath Babaji, a mysterious yogi he describes in his autobiography 'Apprenticed to a Himalayan Master.' He spent three and a half years in the Himalayas, living in caves and undergoing intense spiritual training. He later studied Sufi mysticism and Buddhist meditation, forging a unique path that honors multiple traditions. His Walk of Hope in 2015-16, covering 7,500 km across India over 15 months, brought together communities of all faiths.",
        "youtube_url": "https://www.youtube.com/@SriMSatsang",
        "website_url": "https://www.srim.org",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/Sri_M.jpg/330px-Sri_M.jpg",
        "org_name": "The Satsang Foundation",
        "born": "1949",
        "origin": "Trivandrum, Kerala, India",
        "key_teachings": "Interfaith harmony, Kriya Yoga, Vedantic self-inquiry, walking as spiritual practice, bridging traditions",
        "followers_desc": "Walk of Hope covered 7,500 km across India, bestselling author, Padma Bhushan nominee"
    },
]

def upsert_teacher(t):
    """Upsert a single teacher via REST API."""
    payload = {
        "slug": t["slug"],
        "name": t["name"],
        "tradition": t["tradition"],
        "bio": t.get("bio"),
        "journey": t.get("journey"),
        "youtube_url": t.get("youtube_url"),
        "website_url": t.get("website_url"),
        "image_url": t.get("image_url"),
        "org_name": t.get("org_name"),
        "is_org": t.get("is_org", False),
        "born": t.get("born"),
        "origin": t.get("origin"),
        "key_teachings": t.get("key_teachings"),
        "followers_desc": t.get("followers_desc"),
    }
    data = json.dumps(payload)
    result = subprocess.run([
        "curl", "-s", "-X", "POST",
        f"{SUPABASE_URL}/rest/v1/spiritual_teachers",
        "-H", f"apikey: {SUPABASE_KEY}",
        "-H", f"Authorization: Bearer {SUPABASE_KEY}",
        "-H", "Content-Type: application/json",
        "-H", "Prefer: resolution=merge-duplicates",
        data
    ], capture_output=True, text=True)
    if result.returncode != 0 or "error" in result.stdout.lower():
        print(f"  ERROR: {result.stdout[:200]}")
        return False
    print(f"  ✓ {t['name']}")
    return True

def link_wisdom_entries(teacher_name, slug):
    """Update daily_wisdom entries to link to teacher slug."""
    encoded_name = urllib.parse.quote(teacher_name, safe='')
    result = subprocess.run([
        "curl", "-s", "-X", "PATCH",
        f"{SUPABASE_URL}/rest/v1/daily_wisdom?teacher_name=eq.{encoded_name}",
        "-H", f"apikey: {SUPABASE_KEY}",
        "-H", f"Authorization: Bearer {SUPABASE_KEY}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({"teacher_slug": slug})
    ], capture_output=True, text=True)
    return result.returncode == 0

# New quotes for Byron Katie, S.N. Goenka, Sri M
NEW_QUOTES = [
    {
        "teacher_name": "Byron Katie",
        "tradition": "Interfaith / Modern",
        "quote": "I discovered that when I believed my thoughts, I suffered, but that when I didn't believe them, I didn't suffer, and that this is true for every human being. Freedom is as simple as that.",
        "source_title": "Loving What Is",
        "source_url": "https://thework.com",
        "source_type": "book",
        "teacher_image_url": None,
        "teacher_slug": "byron-katie",
        "featured_date": "2026-08-14",
    },
    {
        "teacher_name": "Byron Katie",
        "tradition": "Interfaith / Modern",
        "quote": "It's not your job to like me — it's mine. Placing the job of liking me in your hands is setting myself up for suffering.",
        "source_title": "The Work of Byron Katie",
        "source_url": "https://www.youtube.com/@theworkofbk",
        "source_type": "curated",
        "teacher_image_url": None,
        "teacher_slug": "byron-katie",
        "featured_date": "2026-08-22",
    },
    {
        "teacher_name": "S.N. Goenka",
        "tradition": "Buddhist",
        "quote": "The art of living is the art of living in the present moment. The past is gone. The future is not yet. One who lives in the present moment lives in freedom.",
        "source_title": "The Art of Living: Vipassana Meditation",
        "source_url": "https://www.dhamma.org",
        "source_type": "discourse",
        "teacher_image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/The_Kalyanmitra_Satyanarayan_Goenka_who_brought_Vipassana_Meditation_technique_to_India_after_2500_years_is_seen_with_his_wife_while_speaking_at_a_talk_on_%22Values_in_Education_-_Good_Governance_through_Vipassana_Meditation%22_in.jpg/330px-thumbnail.jpg",
        "teacher_slug": "sn-goenka",
        "featured_date": "2026-08-15",
    },
    {
        "teacher_name": "S.N. Goenka",
        "tradition": "Buddhist",
        "quote": "Observe the reality as it is. As it is, not as you wish it to be. Perhaps your breath is deep. Perhaps your breath is shallow. It doesn't matter. The fact is that you are breathing deep or shallow. Observe.",
        "source_title": "Vipassana 10-Day Course Discourse",
        "source_url": "https://www.dhamma.org",
        "source_type": "discourse",
        "teacher_image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/The_Kalyanmitra_Satyanarayan_Goenka_who_brought_Vipassana_Meditation_technique_to_India_after_2500_years_is_seen_with_his_wife_while_speaking_at_a_talk_on_%22Values_in_Education_-_Good_Governance_through_Vipassana_Meditation%22_in.jpg/330px-thumbnail.jpg",
        "teacher_slug": "sn-goenka",
        "featured_date": "2026-08-23",
    },
    {
        "teacher_name": "Sri M",
        "tradition": "Hindu / Yoga",
        "quote": "Walk together, in spite of all our differences, for the well-being of humanity and for peace. The essence of all religions is one — only their approaches are different.",
        "source_title": "Walk of Hope 2015-16",
        "source_url": "https://www.srim.org",
        "source_type": "speech",
        "teacher_image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/Sri_M.jpg/330px-Sri_M.jpg",
        "teacher_slug": "sri-m",
        "featured_date": "2026-08-16",
    },
    {
        "teacher_name": "Sri M",
        "tradition": "Hindu / Yoga",
        "quote": "The Truth is beyond all religions. When you go deep enough, all paths merge into one. The Himalayan masters taught me this — that the inner journey is universal.",
        "source_title": "Apprenticed to a Himalayan Master",
        "source_url": "https://www.youtube.com/@SriMSatsang",
        "source_type": "book",
        "teacher_image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/Sri_M.jpg/330px-Sri_M.jpg",
        "teacher_slug": "sri-m",
        "featured_date": "2026-08-24",
    },
]

if __name__ == "__main__":
    print("=== Seeding spiritual_teachers ===")
    for t in TEACHERS:
        upsert_teacher(t)

    print("\n=== Linking existing daily_wisdom entries ===")
    for t in TEACHERS:
        link_wisdom_entries(t["name"], t["slug"])
        print(f"  Linked: {t['name']} -> {t['slug']}")

    print("\n=== Adding new quotes ===")
    for q in NEW_QUOTES:
        data = json.dumps(q)
        result = subprocess.run([
            "curl", "-s", "-X", "POST",
            f"{SUPABASE_URL}/rest/v1/daily_wisdom",
            "-H", f"apikey: {SUPABASE_KEY}",
            "-H", f"Authorization: Bearer {SUPABASE_KEY}",
            "-H", "Content-Type: application/json",
            "-H", "Prefer: resolution=merge-duplicates",
            data
        ], capture_output=True, text=True)
        if "error" in result.stdout.lower():
            print(f"  ERROR {q['teacher_name']}: {result.stdout[:200]}")
        else:
            print(f"  ✓ {q['teacher_name']}: {q['quote'][:50]}...")

    print("\nDone!")
