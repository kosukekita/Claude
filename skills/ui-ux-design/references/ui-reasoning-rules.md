# UI Reasoning Rules

This file maps each UI category to a concrete reasoning bundle: recommended page pattern, style priority, color/typography mood, key effects, machine-readable decision rules (JSON), and anti-patterns to avoid. Use it after product routing to lock in style + color + motion + guardrails for a specific product category. The `Decision_Rules` JSON is meant to be parsed programmatically: each key is a conditional flag (e.g. `if_ux_focused`, `must_have`, `if_luxury`) and each value is the action to apply when that condition holds. `Severity` marks how strictly the anti-patterns should be treated (HIGH = do not ship if violated).

## Quick Lookup Table

| # | UI Category | Recommended Pattern | Style Priority | Color Mood | Typography Mood | Key Effects | Severity |
|---|---|---|---|---|---|---|---|
| 1 | SaaS (General) | Hero + Features + CTA | Glassmorphism + Flat Design | Trust blue + Accent contrast | Professional + Hierarchy | Subtle hover (200-250ms) + Smooth transitions | HIGH |
| 2 | Micro SaaS | Hero-Centric + Trust | Motion-Driven + Vibrant & Block | Bold primaries + Accent contrast | Modern + Energetic typography | Scroll-triggered animations + Parallax | HIGH |
| 3 | E-commerce | Feature-Rich Showcase | Vibrant & Block-based | Brand primary + Success green | Engaging + Clear hierarchy | Card hover lift (200ms) + Scale effect | HIGH |
| 4 | E-commerce Luxury | Feature-Rich Showcase | Liquid Glass + Glassmorphism | Premium colors + Minimal accent | Elegant + Refined typography | Chromatic aberration + Fluid animations (400-600ms) | HIGH |
| 5 | B2B Service | Feature-Rich Showcase + Trust | Trust & Authority + Minimalism | Professional blue + Neutral grey | Formal + Clear typography | Section transitions + Feature reveals | HIGH |
| 6 | Financial Dashboard | Data-Dense Dashboard | Dark Mode (OLED) + Data-Dense | Dark bg + Red/Green alerts + Trust blue | Clear + Readable typography | Real-time number animations + Alert pulse | HIGH |
| 7 | Analytics Dashboard | Data-Dense + Drill-Down | Data-Dense + Heat Map | Cool→Hot gradients + Neutral grey | Clear + Functional typography | Hover tooltips + Chart zoom + Filter animations | HIGH |
| 8 | Healthcare App | Social Proof-Focused | Neumorphism + Accessible & Ethical | Calm blue + Health green | Readable + Large type (16px+) | Soft box-shadow + Smooth press (150ms) | HIGH |
| 9 | Educational App | Feature-Rich Showcase | Claymorphism + Micro-interactions | Playful colors + Clear hierarchy | Friendly + Engaging typography | Soft press (200ms) + Fluffy elements | MEDIUM |
| 10 | Creative Agency | Storytelling-Driven | Brutalism + Motion-Driven | Bold primaries + Artistic freedom | Bold + Expressive typography | CRT scanlines + Neon glow + Glitch effects | HIGH |
| 11 | Portfolio/Personal | Storytelling-Driven | Motion-Driven + Minimalism | Brand primary + Artistic | Expressive + Variable typography | Parallax (3-5 layers) + Scroll-triggered reveals | MEDIUM |
| 12 | Gaming | Feature-Rich Showcase | 3D & Hyperrealism + Retro-Futurism | Vibrant + Neon + Immersive | Bold + Impactful typography | WebGL 3D rendering + Glitch effects | HIGH |
| 13 | Government/Public Service | Minimal & Direct | Accessible & Ethical + Minimalism | Professional blue + High contrast | Clear + Large typography | Clear focus rings (3-4px) + Skip links | HIGH |
| 14 | Fintech/Crypto | Trust & Authority | Minimalism + Accessible & Ethical | Navy + Trust Blue + Gold | Professional + Trustworthy | Smooth state transitions + Number animations | HIGH |
| 15 | Social Media App | Feature-Rich Showcase | Vibrant & Block-based + Motion-Driven | Vibrant + Engagement colors | Modern + Bold typography | Large scroll animations + Icon animations | MEDIUM |
| 16 | Productivity Tool | Interactive Demo + Feature-Rich | Flat Design + Micro-interactions | Clear hierarchy + Functional colors | Clean + Efficient typography | Quick actions (150ms) + Task animations | HIGH |
| 17 | Design System/Component Library | Feature-Rich + Documentation | Minimalism + Accessible & Ethical | Clear hierarchy + Code-like structure | Monospace + Clear typography | Code copy animations + Component previews | HIGH |
| 18 | AI/Chatbot Platform | Interactive Demo + Minimal | AI-Native UI + Minimalism | Neutral + AI Purple (#6366F1) | Modern + Clear typography | Streaming text + Typing indicators + Fade-in | HIGH |
| 19 | NFT/Web3 Platform | Feature-Rich Showcase | Cyberpunk UI + Glassmorphism | Dark + Neon + Gold (#FFD700) | Bold + Modern typography | Wallet connect animations + Transaction feedback | HIGH |
| 20 | Creator Economy Platform | Social Proof + Feature-Rich | Vibrant & Block-based + Bento Box Grid | Vibrant + Brand colors | Modern + Bold typography | Engagement counter animations + Profile reveals | MEDIUM |
| 21 | Remote Work/Collaboration Tool | Feature-Rich + Real-Time | Soft UI Evolution + Minimalism | Calm Blue + Neutral grey | Clean + Readable typography | Real-time presence indicators + Notification badges | HIGH |
| 22 | Mental Health App | Social Proof-Focused | Neumorphism + Accessible & Ethical | Calm Pastels + Trust colors | Calming + Readable typography | Soft press + Breathing animations | HIGH |
| 23 | Pet Tech App | Storytelling + Feature-Rich | Claymorphism + Vibrant & Block-based | Playful + Warm colors | Friendly + Playful typography | Pet profile animations + Health tracking charts | MEDIUM |
| 24 | Smart Home/IoT Dashboard | Real-Time Monitoring | Glassmorphism + Dark Mode (OLED) | Dark + Status indicator colors | Clear + Functional typography | Device status pulse + Quick action animations | HIGH |
| 25 | EV/Charging Ecosystem | Hero-Centric + Feature-Rich | Minimalism + Aurora UI | Electric Blue (#009CD1) + Green | Modern + Clear typography | Range estimation animations + Map interactions | HIGH |
| 26 | Subscription Box Service | Feature-Rich + Conversion | Vibrant & Block-based + Motion-Driven | Brand + Excitement colors | Engaging + Clear typography | Unboxing reveal animations + Product carousel | HIGH |
| 27 | Podcast Platform | Storytelling + Feature-Rich | Dark Mode (OLED) + Minimalism | Dark + Audio waveform accents | Modern + Clear typography | Waveform visualizations + Episode transitions | HIGH |
| 28 | Dating App | Social Proof + Feature-Rich | Vibrant & Block-based + Motion-Driven | Warm + Romantic (Pink/Red gradients) | Modern + Friendly typography | Profile card swipe + Match animations | HIGH |
| 29 | Micro-Credentials/Badges Platform | Trust & Authority + Feature | Minimalism + Flat Design | Trust Blue + Gold (#FFD700) | Professional + Clear typography | Badge reveal animations + Progress tracking | MEDIUM |
| 30 | Knowledge Base/Documentation | FAQ + Minimal | Minimalism + Accessible & Ethical | Clean hierarchy + Minimal color | Clear + Readable typography | Search highlight + Smooth scrolling | HIGH |
| 31 | Hyperlocal Services | Conversion + Feature-Rich | Minimalism + Vibrant & Block-based | Location markers + Trust colors | Clear + Functional typography | Map hover + Provider card reveals | HIGH |
| 32 | Beauty/Spa/Wellness Service | Hero-Centric + Social Proof | Soft UI Evolution + Neumorphism | Soft pastels (Pink Sage Cream) + Gold accents | Elegant + Calming typography | Soft shadows + Smooth transitions (200-300ms) + Gentle hover | HIGH |
| 33 | Luxury/Premium Brand | Storytelling + Feature-Rich | Liquid Glass + Glassmorphism | Black + Gold (#FFD700) + White | Elegant + Refined typography | Slow parallax + Premium reveals (400-600ms) | HIGH |
| 34 | Restaurant/Food Service | Hero-Centric + Conversion | Vibrant & Block-based + Motion-Driven | Warm colors (Orange Red Brown) | Appetizing + Clear typography | Food image reveal + Menu hover effects | HIGH |
| 35 | Fitness/Gym App | Feature-Rich + Data | Vibrant & Block-based + Dark Mode (OLED) | Energetic (Orange #FF6B35) + Dark bg | Bold + Motivational typography | Progress ring animations + Achievement unlocks | HIGH |
| 36 | Real Estate/Property | Hero-Centric + Feature-Rich | Glassmorphism + Minimalism | Trust Blue + Gold + White | Professional + Confident | 3D property tour zoom + Map hover | HIGH |
| 37 | Travel/Tourism Agency | Storytelling-Driven + Hero | Aurora UI + Motion-Driven | Vibrant destination + Sky Blue | Inspirational + Engaging | Destination parallax + Itinerary animations | HIGH |
| 38 | Hotel/Hospitality | Hero-Centric + Social Proof | Liquid Glass + Minimalism | Warm neutrals + Gold (#D4AF37) | Elegant + Welcoming typography | Room gallery + Amenity reveals | HIGH |
| 39 | Wedding/Event Planning | Storytelling + Social Proof | Soft UI Evolution + Aurora UI | Soft Pink (#FFD6E0) + Gold + Cream | Elegant + Romantic typography | Gallery reveals + Timeline animations | HIGH |
| 40 | Legal Services | Trust & Authority + Minimal | Trust & Authority + Minimalism | Navy Blue (#1E3A5F) + Gold + White | Professional + Authoritative typography | Practice area reveal + Attorney profile animations | HIGH |
| 41 | Insurance Platform | Conversion + Trust | Trust & Authority + Flat Design | Trust Blue (#0066CC) + Green + Neutral | Clear + Professional typography | Quote calculator animations + Policy comparison | HIGH |
| 42 | Banking/Traditional Finance | Trust & Authority + Feature | Minimalism + Accessible & Ethical | Navy (#0A1628) + Trust Blue + Gold | Professional + Trustworthy typography | Smooth number animations + Security indicators | HIGH |
| 43 | Online Course/E-learning | Feature-Rich + Social Proof | Claymorphism + Vibrant & Block-based | Vibrant learning colors + Progress green | Friendly + Engaging typography | Progress bar animations + Certificate reveals | HIGH |
| 44 | Non-profit/Charity | Storytelling + Trust | Accessible & Ethical + Organic Biophilic | Cause-related colors + Trust + Warm | Heartfelt + Readable typography | Impact counter animations + Story reveals | HIGH |
| 45 | Music Streaming | Feature-Rich Showcase | Dark Mode (OLED) + Vibrant & Block-based | Dark (#121212) + Vibrant accents + Album art colors | Modern + Bold typography | Waveform visualization + Playlist animations | HIGH |
| 46 | Video Streaming/OTT | Hero-Centric + Feature-Rich | Dark Mode (OLED) + Motion-Driven | Dark bg + Poster colors + Brand accent | Bold + Engaging typography | Video player animations + Content carousel (parallax) | HIGH |
| 47 | Job Board/Recruitment | Conversion-Optimized + Feature-Rich | Flat Design + Minimalism | Professional Blue + Success Green + Neutral | Clear + Professional typography | Search/filter animations + Application flow | HIGH |
| 48 | Marketplace (P2P) | Feature-Rich Showcase + Social Proof | Vibrant & Block-based + Flat Design | Trust colors + Category colors + Success green | Modern + Engaging typography | Review star animations + Listing hover effects | HIGH |
| 49 | Logistics/Delivery | Feature-Rich Showcase + Real-Time | Minimalism + Flat Design | Blue (#2563EB) + Orange (tracking) + Green | Clear + Functional typography | Real-time tracking animation + Status pulse | HIGH |
| 50 | Agriculture/Farm Tech | Feature-Rich Showcase | Organic Biophilic + Flat Design | Earth Green (#4A7C23) + Brown + Sky Blue | Clear + Informative typography | Data visualization + Weather animations | MEDIUM |
| 51 | Construction/Architecture | Hero-Centric + Feature-Rich | Minimalism + 3D & Hyperrealism | Grey (#4A4A4A) + Orange (safety) + Blueprint Blue | Professional + Bold typography | 3D model viewer + Timeline animations | HIGH |
| 52 | Automotive/Car Dealership | Hero-Centric + Feature-Rich | Motion-Driven + 3D & Hyperrealism | Brand colors + Metallic + Dark/Light | Bold + Confident typography | 360 product view + Configurator animations | HIGH |
| 53 | Photography Studio | Storytelling-Driven + Hero-Centric | Motion-Driven + Minimalism | Black + White + Minimal accent | Elegant + Minimal typography | Full-bleed gallery + Before/after reveal | HIGH |
| 54 | Coworking Space | Hero-Centric + Feature-Rich | Vibrant & Block-based + Glassmorphism | Energetic colors + Wood tones + Brand | Modern + Engaging typography | Space tour video + Amenity reveal animations | MEDIUM |
| 55 | Home Services (Plumber/Electrician) | Conversion-Optimized + Trust | Flat Design + Trust & Authority | Trust Blue + Safety Orange + Grey | Professional + Clear typography | Emergency contact highlight + Service menu animations | HIGH |
| 56 | Childcare/Daycare | Social Proof-Focused + Trust | Claymorphism + Vibrant & Block-based | Playful pastels + Safe colors + Warm | Friendly + Playful typography | Parent portal animations + Activity gallery reveal | HIGH |
| 57 | Senior Care/Elderly | Trust & Authority + Accessible | Accessible & Ethical + Soft UI Evolution | Calm Blue + Warm neutrals + Large text | Large + Clear typography (18px+) | Large touch targets + Clear navigation | HIGH |
| 58 | Medical Clinic | Trust & Authority + Conversion | Accessible & Ethical + Minimalism | Medical Blue (#0077B6) + Trust White | Professional + Readable typography | Online booking flow + Doctor profile reveals | HIGH |
| 59 | Pharmacy/Drug Store | Conversion-Optimized + Trust | Flat Design + Accessible & Ethical | Pharmacy Green + Trust Blue + Clean White | Clear + Functional typography | Prescription upload flow + Refill reminders | HIGH |
| 60 | Dental Practice | Social Proof-Focused + Conversion | Soft UI Evolution + Minimalism | Fresh Blue + White + Smile Yellow | Friendly + Professional typography | Before/after gallery + Patient testimonial carousel | HIGH |
| 61 | Veterinary Clinic | Social Proof-Focused + Trust | Claymorphism + Accessible & Ethical | Caring Blue + Pet colors + Warm | Friendly + Welcoming typography | Pet profile management + Service animations | MEDIUM |
| 62 | Florist/Plant Shop | Hero-Centric + Conversion | Organic Biophilic + Vibrant & Block-based | Natural Green + Floral pinks/purples | Elegant + Natural typography | Product reveal + Seasonal transitions | MEDIUM |
| 63 | Bakery/Cafe | Hero-Centric + Conversion | Vibrant & Block-based + Soft UI Evolution | Warm Brown + Cream + Appetizing accents | Warm + Inviting typography | Menu hover + Order animations | HIGH |
| 64 | Brewery/Winery | Storytelling + Hero-Centric | Motion-Driven + Storytelling-Driven | Deep amber/burgundy + Gold + Craft | Artisanal + Heritage typography | Tasting note reveals + Heritage timeline | HIGH |
| 65 | Airline | Conversion + Feature-Rich | Minimalism + Glassmorphism | Sky Blue + Brand colors + Trust | Clear + Professional typography | Flight search animations + Boarding pass reveals | HIGH |
| 66 | News/Media Platform | Hero-Centric + Feature-Rich | Minimalism + Flat Design | Brand colors + High contrast | Clear + Readable typography | Breaking news badge + Article reveal animations | HIGH |
| 67 | Magazine/Blog | Storytelling + Hero-Centric | Swiss Modernism 2.0 + Motion-Driven | Editorial colors + Brand + Clean white | Editorial + Elegant typography | Article transitions + Category reveals | HIGH |
| 68 | Freelancer Platform | Feature-Rich + Conversion | Flat Design + Minimalism | Professional Blue + Success Green | Clear + Professional typography | Skill match animations + Review reveals | HIGH |
| 69 | Marketing Agency | Storytelling + Feature-Rich | Brutalism + Motion-Driven | Bold brand colors + Creative freedom | Bold + Expressive typography | Portfolio reveals + Results animations | HIGH |
| 70 | Event Management | Hero-Centric + Feature-Rich | Vibrant & Block-based + Motion-Driven | Event theme colors + Excitement accents | Bold + Engaging typography | Countdown timer + Registration flow | HIGH |
| 71 | Membership/Community | Social Proof + Conversion | Vibrant & Block-based + Soft UI Evolution | Community brand colors + Engagement | Friendly + Engaging typography | Member counter + Benefit reveals | HIGH |
| 72 | Newsletter Platform | Minimal + Conversion | Minimalism + Flat Design | Brand primary + Clean white + CTA | Clean + Readable typography | Subscribe form + Archive reveals | MEDIUM |
| 73 | Digital Products/Downloads | Feature-Rich + Conversion | Vibrant & Block-based + Motion-Driven | Product colors + Brand + Success green | Modern + Clear typography | Product preview + Instant delivery animations | HIGH |
| 74 | Church/Religious Organization | Hero-Centric + Social Proof | Accessible & Ethical + Soft UI Evolution | Warm Gold + Deep Purple/Blue + White | Welcoming + Clear typography | Service time highlights + Event calendar | MEDIUM |
| 75 | Sports Team/Club | Hero-Centric + Feature-Rich | Vibrant & Block-based + Motion-Driven | Team colors + Energetic accents | Bold + Impactful typography | Score animations + Schedule reveals | HIGH |
| 76 | Museum/Gallery | Storytelling + Feature-Rich | Minimalism + Motion-Driven | Art-appropriate neutrals + Exhibition accents | Elegant + Minimal typography | Virtual tour + Collection reveals | HIGH |
| 77 | Theater/Cinema | Hero-Centric + Conversion | Dark Mode (OLED) + Motion-Driven | Dark + Spotlight accents + Gold | Dramatic + Bold typography | Seat selection + Trailer reveals | HIGH |
| 78 | Language Learning App | Feature-Rich + Social Proof | Claymorphism + Vibrant & Block-based | Playful colors + Progress indicators | Friendly + Clear typography | Progress animations + Achievement unlocks | HIGH |
| 79 | Coding Bootcamp | Feature-Rich + Social Proof | Dark Mode (OLED) + Minimalism | Code editor colors + Brand + Success | Technical + Clear typography | Terminal animations + Career outcome reveals | HIGH |
| 80 | Cybersecurity Platform | Trust & Authority + Real-Time | Cyberpunk UI + Dark Mode (OLED) | Matrix Green (#00FF00) + Deep Black | Technical + Clear typography | Threat visualization + Alert animations | HIGH |
| 81 | Developer Tool / IDE | Minimal + Documentation | Dark Mode (OLED) + Minimalism | Dark syntax theme + Blue focus | Monospace + Functional typography | Syntax highlighting + Command palette | HIGH |
| 82 | Biotech / Life Sciences | Storytelling + Data | Glassmorphism + Clean Science | Sterile White + DNA Blue + Life Green | Scientific + Clear typography | Data visualization + Research reveals | HIGH |
| 83 | Space Tech / Aerospace | Immersive + Feature-Rich | Holographic/HUD + Dark Mode | Deep Space Black + Star White + Metallic | Futuristic + Precise typography | Telemetry animations + 3D renders | HIGH |
| 84 | Architecture / Interior | Portfolio + Hero-Centric | Exaggerated Minimalism + High Imagery | Monochrome + Gold Accent + High Imagery | Architectural + Elegant typography | Project gallery + Blueprint reveals | HIGH |
| 85 | Quantum Computing Interface | Immersive + Interactive | Holographic/HUD + Dark Mode | Quantum Blue (#00FFFF) + Deep Black | Futuristic + Scientific typography | Probability visualizations + Qubit state animations | HIGH |
| 86 | Biohacking / Longevity App | Data-Dense + Storytelling | Biomimetic/Organic 2.0 + Minimalism | Cellular Pink/Red + DNA Blue + White | Scientific + Clear typography | Biological data viz + Progress animations | HIGH |
| 87 | Autonomous Drone Fleet Manager | Real-Time + Feature-Rich | HUD/Sci-Fi FUI + Real-Time | Tactical Green + Alert Red + Map Dark | Technical + Functional typography | Telemetry animations + 3D spatial awareness | HIGH |
| 88 | Generative Art Platform | Showcase + Feature-Rich | Minimalism + Gen Z Chaos | Neutral (#F5F5F5) + User Content | Minimal + Content-focused typography | Gallery masonry + Minting animations | HIGH |
| 89 | Spatial Computing OS / App | Immersive + Interactive | Spatial UI (VisionOS) + Glassmorphism | Frosted Glass + System Colors + Depth | Spatial + Readable typography | Depth hierarchy + Gaze interactions | HIGH |
| 90 | Sustainable Energy / Climate Tech | Data + Trust | Organic Biophilic + E-Ink/Paper | Earth Green + Sky Blue + Solar Yellow | Clear + Informative typography | Impact viz + Progress animations | HIGH |
| 91 | Personal Finance Tracker | Interactive Product Demo | Glassmorphism + Dark Mode (OLED) | Calm blue + success green + alert red + chart accents | Modern + Clear hierarchy | Backdrop blur (10-20px) + Translucent overlays | HIGH |
| 92 | Chat & Messaging App | Feature-Rich Showcase + Demo | Minimalism + Micro-interactions | Brand primary + bubble contrast (sender/receiver) + typing grey | Professional + Clean hierarchy | Subtle hover 200ms + Smooth transitions + Clean | HIGH |
| 93 | Notes & Writing App | Minimal & Direct | Minimalism + Flat Design | Clean white/cream + minimal accent + editor syntax colors | Professional + Clean hierarchy | Color shift hover + Fast 150ms transitions + No shadows | HIGH |
| 94 | Habit Tracker | Social Proof-Focused + Demo | Claymorphism + Vibrant & Block-based | Streak warm (amber/orange) + progress green + motivational accents | Playful + Rounded + Friendly | Multi-layer shadows + Spring bounce + Soft press 200ms | HIGH |
| 95 | Food Delivery / On-Demand | Hero-Centric Design + Feature-Rich | Vibrant & Block-based + Motion-Driven | Appetizing warm (orange/red) + trust blue + map accent | Energetic + Bold + Large | Scroll animations + Parallax + Page transitions | HIGH |
| 96 | Ride Hailing / Transportation | Conversion-Optimized + Demo | Minimalism + Glassmorphism | Brand primary + map neutral + status indicator colors | Professional + Clean hierarchy | Backdrop blur (10-20px) + Translucent overlays | HIGH |
| 97 | Recipe & Cooking App | Hero-Centric Design + Feature-Rich | Claymorphism + Vibrant & Block-based | Warm food tones (terracotta/sage/cream) + appetizing imagery | Playful + Rounded + Friendly | Multi-layer shadows + Spring bounce + Soft press 200ms | HIGH |
| 98 | Meditation & Mindfulness | Storytelling-Driven + Social Proof | Neumorphism + Soft UI Evolution | Ultra-calm pastels (lavender/sage/sky) + breathing animation gradient | Subtle + Soft + Monochromatic | Dual shadows (light+dark) + Soft press 150ms | HIGH |
| 99 | Weather App | Hero-Centric Design | Glassmorphism + Aurora UI | Atmospheric gradients (sky blue → sunset → storm grey) + temp scale | Modern + Clear hierarchy | Backdrop blur (10-20px) + Translucent overlays | HIGH |
| 100 | Diary & Journal App | Storytelling-Driven | Soft UI Evolution + Minimalism | Warm paper tones (cream/linen) + muted ink + mood-coded accents | Professional + Clean hierarchy | Subtle hover 200ms + Smooth transitions + Clean | HIGH |
| 101 | CRM & Client Management | Feature-Rich Showcase + Demo | Flat Design + Minimalism | Professional blue + pipeline stage colors + closed-won green | Professional + Clean hierarchy | Color shift hover + Fast 150ms transitions + No shadows | HIGH |
| 102 | Inventory & Stock Management | Feature-Rich Showcase | Flat Design + Minimalism | Functional neutral + status traffic-light (green/amber/red) + scanner accent | Professional + Clean hierarchy | Color shift hover + Fast 150ms transitions + No shadows | HIGH |
| 103 | Flashcard & Study Tool | Feature-Rich Showcase + Demo | Claymorphism + Micro-interactions | Playful primary + correct green + incorrect red + progress blue | Playful + Rounded + Friendly | Multi-layer shadows + Spring bounce + Soft press 200ms | HIGH |
| 104 | Booking & Appointment App | Conversion-Optimized | Soft UI Evolution + Flat Design | Trust blue + available green + booked grey + confirm accent | Bold + Clean + Sans-serif | Color shift hover + Fast 150ms transitions + No shadows | HIGH |
| 105 | Invoice & Billing Tool | Conversion-Optimized + Trust | Minimalism + Flat Design | Professional navy + paid green + overdue red + neutral grey | Professional + Clean hierarchy | Color shift hover + Fast 150ms transitions + No shadows | HIGH |
| 106 | Grocery & Shopping List | Minimal & Direct + Demo | Flat Design + Vibrant & Block-based | Fresh green + food-category colors + checkmark accent | Bold + Clean + Sans-serif | Color shift hover + Fast 150ms transitions + No shadows | HIGH |
| 107 | Timer & Pomodoro | Minimal & Direct | Minimalism + Neumorphism | High-contrast on dark + focus red/amber + break green | Professional + Clean hierarchy | Dual shadows (light+dark) + Soft press 150ms | HIGH |
| 108 | Parenting & Baby Tracker | Social Proof-Focused + Trust | Claymorphism + Soft UI Evolution | Soft pastels (baby pink/sky blue/mint/peach) + warm accents | Playful + Rounded + Friendly | Multi-layer shadows + Spring bounce + Soft press 200ms | HIGH |
| 109 | Scanner & Document Manager | Feature-Rich Showcase + Demo | Minimalism + Flat Design | Clean white + camera viewfinder accent + file-type color coding | Professional + Clean hierarchy | Color shift hover + Fast 150ms transitions + No shadows | HIGH |
| 110 | Calendar & Scheduling App | Feature-Rich Showcase + Demo | Flat Design + Micro-interactions | Clean blue + event category accent colors + success green | Bold + Clean + Sans-serif | Color shift hover + Fast 150ms transitions + No shadows | HIGH |
| 111 | Password Manager | Trust & Authority + Feature-Rich | Minimalism + Accessible & Ethical | Trust blue + security green + dark neutral | Professional + Clean hierarchy | Subtle hover 200ms + Smooth transitions + Clean | HIGH |
| 112 | Expense Splitter / Bill Split | Minimal & Direct + Demo | Flat Design + Vibrant & Block-based | Success green + alert red + neutral grey + avatar accent colors | Bold + Clean + Sans-serif | Color shift hover + Fast 150ms transitions + No shadows | HIGH |
| 113 | Voice Recorder & Memo | Interactive Product Demo + Minimal | Minimalism + AI-Native UI | Clean white + recording red + waveform accent | Professional + Clean hierarchy | Subtle hover 200ms + Smooth transitions + Clean | HIGH |
| 114 | Bookmark & Read-Later | Minimal & Direct + Demo | Minimalism + Flat Design | Paper warm white + ink neutral + minimal accent + tag colors | Professional + Clean hierarchy | Color shift hover + Fast 150ms transitions + No shadows | HIGH |
| 115 | Translator App | Feature-Rich Showcase + Interactive Demo | Flat Design + AI-Native UI | Global blue + neutral grey + language flag accent | Bold + Clean + Sans-serif | Color shift hover + Fast 150ms transitions + No shadows | HIGH |
| 116 | Calculator & Unit Converter | Minimal & Direct | Neumorphism + Minimalism | Dark functional + orange operation keys + clear button hierarchy | Professional + Clean hierarchy | Dual shadows (light+dark) + Soft press 150ms | HIGH |
| 117 | Alarm & World Clock | Minimal & Direct | Dark Mode (OLED) + Minimalism | Deep dark + ambient glow accent + timezone gradient | Professional + Clean hierarchy | Subtle glow + Neon accents + High contrast | HIGH |
| 118 | File Manager & Transfer | Feature-Rich Showcase + Demo | Flat Design + Minimalism | Functional neutral + file type color coding (PDF orange, doc blue, image purple) | Professional + Clean hierarchy | Color shift hover + Fast 150ms transitions + No shadows | HIGH |
| 119 | Email Client | Feature-Rich Showcase + Demo | Flat Design + Minimalism | Clean white + brand primary + priority red + snooze amber | Professional + Clean hierarchy | Color shift hover + Fast 150ms transitions + No shadows | HIGH |
| 120 | Casual Puzzle Game | Feature-Rich Showcase + Social Proof | Claymorphism + Vibrant & Block-based | Cheerful pastels + progression gradient + reward gold + bright accent | Playful + Rounded + Friendly | Multi-layer shadows + Spring bounce + Soft press 200ms | HIGH |
| 121 | Trivia & Quiz Game | Feature-Rich Showcase + Social Proof | Vibrant & Block-based + Micro-interactions | Energetic blue + correct green + incorrect red + leaderboard gold | Energetic + Bold + Large | Haptic feedback + Small 50-100ms animations | HIGH |
| 122 | Card & Board Game | Feature-Rich Showcase | 3D & Hyperrealism + Flat Design | Game-theme felt green + dark wood + card back patterns | Bold + Clean + Sans-serif | Color shift hover + Fast 150ms transitions + No shadows | HIGH |
| 123 | Idle & Clicker Game | Feature-Rich Showcase | Vibrant & Block-based + Motion-Driven | Coin gold + upgrade blue + prestige purple + progress green | Energetic + Bold + Large | Scroll animations + Parallax + Page transitions | HIGH |
| 124 | Word & Crossword Game | Minimal & Direct + Demo | Minimalism + Flat Design | Clean white + warm letter tiles + success green + shake red | Professional + Clean hierarchy | Color shift hover + Fast 150ms transitions + No shadows | HIGH |
| 125 | Arcade & Retro Game | Feature-Rich Showcase + Hero-Centric | Pixel Art + Retro-Futurism | Neon on black + pixel palette + score gold + danger red | Nostalgic + Monospace + Neon | Subtle hover (200ms) + Smooth transitions | HIGH |
| 126 | Photo Editor & Filters | Feature-Rich Showcase + Interactive Demo | Minimalism + Dark Mode (OLED) | Dark editor background + vibrant filter preview strip + tool icon accent | Professional + Clean hierarchy | Subtle glow + Neon accents + High contrast | HIGH |
| 127 | Short Video Editor | Feature-Rich Showcase + Hero-Centric | Dark Mode (OLED) + Motion-Driven | Dark background + timeline track accent colors + effect preview vivid | High contrast + Light on dark | Subtle glow + Neon accents + High contrast | HIGH |
| 128 | Drawing & Sketching Canvas | Interactive Product Demo + Storytelling | Minimalism + Dark Mode (OLED) | Neutral canvas + full-spectrum color picker + tool panel dark | Professional + Clean hierarchy | Subtle glow + Neon accents + High contrast | HIGH |
| 129 | Music Creation & Beat Maker | Interactive Product Demo + Storytelling | Dark Mode (OLED) + Motion-Driven | Dark studio background + track colors rainbow + waveform accent + BPM pulse | High contrast + Light on dark | Subtle glow + Neon accents + High contrast | HIGH |
| 130 | Meme & Sticker Maker | Feature-Rich Showcase + Social Proof | Vibrant & Block-based + Flat Design | Bold primary + comedic yellow + viral red + high saturation accent | Bold + Clean + Sans-serif | Color shift hover + Fast 150ms transitions + No shadows | HIGH |
| 131 | AI Photo & Avatar Generator | Feature-Rich Showcase + Social Proof | AI-Native UI + Aurora UI | AI purple + aurora gradients + before/after neutral | Elegant + Gradient-friendly | Flowing gradients 8-12s + Color morphing | HIGH |
| 132 | Link-in-Bio Page Builder | Conversion-Optimized + Social Proof | Vibrant & Block-based + Bento Box Grid | Brand-customizable + accent link color + clean white canvas | Energetic + Bold + Large | Large section gaps 48px+ + Color shift hover + Scroll-snap | HIGH |
| 133 | Wardrobe & Outfit Planner | Storytelling-Driven + Feature-Rich | Minimalism + Motion-Driven | Clean fashion neutral + full clothes color palette + accent | Professional + Clean hierarchy | Subtle hover 200ms + Smooth transitions + Clean | HIGH |
| 134 | Plant Care Tracker | Storytelling-Driven + Social Proof | Organic Biophilic + Soft UI Evolution | Nature greens + earth brown + sunny yellow reminder + water blue | Warm + Humanist + Natural | Rounded 16-24px + Natural shadows + Flowing SVG | HIGH |
| 135 | Book & Reading Tracker | Social Proof-Focused + Feature-Rich | Swiss Modernism 2.0 + Minimalism | Warm paper white + ink brown + reading progress green + book cover colors | Professional + Clean hierarchy | Subtle hover 200ms + Smooth transitions + Clean | HIGH |
| 136 | Couple & Relationship App | Storytelling-Driven + Social Proof | Aurora UI + Soft UI Evolution | Warm romantic pink/rose + soft gradient + memory photo tones | Elegant + Gradient-friendly | Flowing gradients 8-12s + Color morphing | HIGH |
| 137 | Family Calendar & Chores | Feature-Rich Showcase + Social Proof | Flat Design + Claymorphism | Warm playful + member color coding + chore completion green | Playful + Rounded + Friendly | Multi-layer shadows + Spring bounce + Soft press 200ms | HIGH |
| 138 | Mood Tracker | Storytelling-Driven + Social Proof | Soft UI Evolution + Minimalism | Emotion gradient (blue sad to yellow happy) + pastel per mood + insight accent | Professional + Clean hierarchy | Subtle hover 200ms + Smooth transitions + Clean | HIGH |
| 139 | Gift & Wishlist | Minimal & Direct + Conversion | Vibrant & Block-based + Soft UI Evolution | Celebration warm pink/gold/red + category colors + surprise accent | Energetic + Bold + Large | Large section gaps 48px+ + Color shift hover + Scroll-snap | HIGH |
| 140 | Running & Cycling GPS | Feature-Rich Showcase + Social Proof | Dark Mode (OLED) + Vibrant & Block-based | Energetic orange + map accent + pace zones (green/yellow/red) | High contrast + Light on dark | Subtle glow + Neon accents + High contrast | HIGH |
| 141 | Yoga & Stretching Guide | Storytelling-Driven + Social Proof | Organic Biophilic + Soft UI Evolution | Earth calming sage/terracotta/cream + breathing gradient + warm accent | Warm + Humanist + Natural | Rounded 16-24px + Natural shadows + Flowing SVG | HIGH |
| 142 | Sleep Tracker | Feature-Rich Showcase + Social Proof | Dark Mode (OLED) + Neumorphism | Deep midnight blue + stars/moon accent + sleep quality gradient (poor red to great green) | High contrast + Light on dark | Dual shadows (light+dark) + Soft press 150ms | HIGH |
| 143 | Calorie & Nutrition Counter | Feature-Rich Showcase + Social Proof | Flat Design + Vibrant & Block-based | Healthy green + macro colors (protein blue, carb orange, fat yellow) + progress circle | Bold + Clean + Sans-serif | Color shift hover + Fast 150ms transitions + No shadows | HIGH |
| 144 | Period & Cycle Tracker | Social Proof-Focused + Trust | Soft UI Evolution + Aurora UI | Rose/blush + lavender + fertility green + soft calendar tones | Elegant + Gradient-friendly | Flowing gradients 8-12s + Color morphing | HIGH |
| 145 | Medication & Pill Reminder | Trust & Authority + Feature-Rich | Accessible & Ethical + Flat Design | Medical trust blue + missed alert red + taken green + clean white | Bold + Clean + Sans-serif | Color shift hover + Fast 150ms transitions + No shadows | HIGH |
| 146 | Water & Hydration Reminder | Minimal & Direct + Demo | Claymorphism + Vibrant & Block-based | Refreshing blue + water wave animation + goal progress accent | Playful + Rounded + Friendly | Multi-layer shadows + Spring bounce + Soft press 200ms | HIGH |
| 147 | Fasting & Intermittent Timer | Feature-Rich Showcase + Social Proof | Minimalism + Dark Mode (OLED) | Fasting deep blue/purple + eating window green + timeline neutral | Professional + Clean hierarchy | Subtle glow + Neon accents + High contrast | HIGH |
| 148 | Anonymous Community / Confession | Social Proof-Focused + Feature-Rich | Dark Mode (OLED) + Minimalism | Dark protective + subtle gradient + upvote green + empathy warm accent | Professional + Clean hierarchy | Subtle glow + Neon accents + High contrast | HIGH |
| 149 | Local Events & Discovery | Hero-Centric Design + Feature-Rich | Vibrant & Block-based + Motion-Driven | City vibrant + event category colors + map accent + date highlight | Energetic + Bold + Large | Scroll animations + Parallax + Page transitions | HIGH |
| 150 | Study Together / Virtual Coworking | Social Proof-Focused + Feature-Rich | Minimalism + Soft UI Evolution | Calm focus blue + session progress indicator + ambient warm neutrals | Professional + Clean hierarchy | Subtle hover 200ms + Smooth transitions + Clean | HIGH |
| 151 | Coding Challenge & Practice | Feature-Rich Showcase + Social Proof | Dark Mode (OLED) + Cyberpunk UI | Code editor dark + success green + difficulty gradient (easy green / medium amber / hard red) | High contrast + Light on dark | Subtle glow + Neon accents + High contrast | HIGH |
| 152 | Kids Learning (ABC & Math) | Social Proof-Focused + Trust | Claymorphism + Vibrant & Block-based | Bright primary + child-safe pastels + reward gold + interactive accent | Playful + Rounded + Friendly | Multi-layer shadows + Spring bounce + Soft press 200ms | HIGH |
| 153 | Music Instrument Learning | Interactive Product Demo + Social Proof | Vibrant & Block-based + Motion-Driven | Musical warm deep red/brown + note color system + skill progress bar | Energetic + Bold + Large | Scroll animations + Parallax + Page transitions | HIGH |
| 154 | Parking Finder | Conversion-Optimized + Feature-Rich | Minimalism + Glassmorphism | Trust blue + available green + occupied red + map neutral | Professional + Clean hierarchy | Backdrop blur (10-20px) + Translucent overlays | HIGH |
| 155 | Public Transit Guide | Feature-Rich Showcase + Interactive Demo | Flat Design + Accessible & Ethical | Transit brand line colors + real-time indicator green/red + map neutral | Bold + Clean + Sans-serif | Color shift hover + Fast 150ms transitions + No shadows | HIGH |
| 156 | Road Trip Planner | Storytelling-Driven + Hero-Centric | Aurora UI + Organic Biophilic | Adventure warm sunset orange + map teal + stop markers + road neutral | Elegant + Gradient-friendly | Flowing gradients 8-12s + Color morphing | HIGH |
| 157 | VPN & Privacy Tool | Trust & Authority + Conversion-Optimized | Minimalism + Dark Mode (OLED) | Dark shield blue + connected green + disconnected red + trust accent | Professional + Clean hierarchy | Subtle glow + Neon accents + High contrast | HIGH |
| 158 | Emergency SOS & Safety | Trust & Authority + Social Proof | Accessible & Ethical + Flat Design | Alert red + safety blue + location green + high contrast critical | Bold + Clean + Sans-serif | Color shift hover + Fast 150ms transitions + No shadows | HIGH |
| 159 | Wallpaper & Theme App | Feature-Rich Showcase + Social Proof | Vibrant & Block-based + Aurora UI | Content-driven + trending aesthetic palettes + download accent | Energetic + Bold + Large | Large section gaps 48px+ + Color shift hover + Scroll-snap | HIGH |
| 160 | White Noise & Ambient Sound | Minimal & Direct + Social Proof | Minimalism + Dark Mode (OLED) | Calming dark + ambient texture visual + subtle sound wave + sleep blue | Professional + Clean hierarchy | Subtle glow + Neon accents + High contrast | HIGH |
| 161 | Home Decoration & Interior Design | Storytelling-Driven + Feature-Rich | Minimalism + 3D Product Preview | Neutral interior palette + material texture accent + AR blue | Professional + Clean hierarchy | Subtle hover 200ms + Smooth transitions + Clean | HIGH |

## Per-Category Rules

### 1. SaaS (General)

| Field | Value |
|---|---|
| Recommended pattern | Hero + Features + CTA |
| Style priority | Glassmorphism + Flat Design |
| Color mood | Trust blue + Accent contrast |
| Typography mood | Professional + Hierarchy |
| Key effects | Subtle hover (200-250ms) + Smooth transitions |
| Anti-patterns | Excessive animation + Dark mode by default |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_ux_focused": "prioritize-minimalism", "if_data_heavy": "add-glassmorphism"}
```

### 2. Micro SaaS

| Field | Value |
|---|---|
| Recommended pattern | Hero-Centric + Trust |
| Style priority | Motion-Driven + Vibrant & Block |
| Color mood | Bold primaries + Accent contrast |
| Typography mood | Modern + Energetic typography |
| Key effects | Scroll-triggered animations + Parallax |
| Anti-patterns | Static design + No video + Poor mobile |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_pre_launch": "use-waitlist-pattern", "if_video_ready": "add-hero-video"}
```

### 3. E-commerce

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich Showcase |
| Style priority | Vibrant & Block-based |
| Color mood | Brand primary + Success green |
| Typography mood | Engaging + Clear hierarchy |
| Key effects | Card hover lift (200ms) + Scale effect |
| Anti-patterns | Flat design without depth + Text-heavy pages |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_luxury": "switch-to-liquid-glass", "if_conversion_focused": "add-urgency-colors"}
```

### 4. E-commerce Luxury

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich Showcase |
| Style priority | Liquid Glass + Glassmorphism |
| Color mood | Premium colors + Minimal accent |
| Typography mood | Elegant + Refined typography |
| Key effects | Chromatic aberration + Fluid animations (400-600ms) |
| Anti-patterns | Vibrant & Block-based + Playful colors |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_checkout": "emphasize-trust", "if_hero_needed": "use-3d-hyperrealism"}
```

### 5. B2B Service

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich Showcase + Trust |
| Style priority | Trust & Authority + Minimalism |
| Color mood | Professional blue + Neutral grey |
| Typography mood | Formal + Clear typography |
| Key effects | Section transitions + Feature reveals |
| Anti-patterns | Playful design + Hidden credentials + AI purple/pink gradients |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "case-studies", "must_have": "roi-messaging"}
```

### 6. Financial Dashboard

| Field | Value |
|---|---|
| Recommended pattern | Data-Dense Dashboard |
| Style priority | Dark Mode (OLED) + Data-Dense |
| Color mood | Dark bg + Red/Green alerts + Trust blue |
| Typography mood | Clear + Readable typography |
| Key effects | Real-time number animations + Alert pulse |
| Anti-patterns | Light mode default + Slow rendering |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "real-time-updates", "must_have": "high-contrast"}
```

### 7. Analytics Dashboard

| Field | Value |
|---|---|
| Recommended pattern | Data-Dense + Drill-Down |
| Style priority | Data-Dense + Heat Map |
| Color mood | Cool→Hot gradients + Neutral grey |
| Typography mood | Clear + Functional typography |
| Key effects | Hover tooltips + Chart zoom + Filter animations |
| Anti-patterns | Ornate design + No filtering |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "data-export", "if_large_dataset": "virtualize-lists"}
```

### 8. Healthcare App

| Field | Value |
|---|---|
| Recommended pattern | Social Proof-Focused |
| Style priority | Neumorphism + Accessible & Ethical |
| Color mood | Calm blue + Health green |
| Typography mood | Readable + Large type (16px+) |
| Key effects | Soft box-shadow + Smooth press (150ms) |
| Anti-patterns | Bright neon colors + Motion-heavy animations + AI purple/pink gradients |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "wcag-aaa-compliance", "if_medication": "red-alert-colors"}
```

### 9. Educational App

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich Showcase |
| Style priority | Claymorphism + Micro-interactions |
| Color mood | Playful colors + Clear hierarchy |
| Typography mood | Friendly + Engaging typography |
| Key effects | Soft press (200ms) + Fluffy elements |
| Anti-patterns | Dark modes + Complex jargon |
| Severity | MEDIUM |

Decision rules (JSON):

```json
{"if_gamification": "add-progress-animation", "if_children": "increase-playfulness"}
```

### 10. Creative Agency

| Field | Value |
|---|---|
| Recommended pattern | Storytelling-Driven |
| Style priority | Brutalism + Motion-Driven |
| Color mood | Bold primaries + Artistic freedom |
| Typography mood | Bold + Expressive typography |
| Key effects | CRT scanlines + Neon glow + Glitch effects |
| Anti-patterns | Corporate minimalism + Hidden portfolio |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "case-studies", "if_boutique": "increase-artistic-freedom"}
```

### 11. Portfolio/Personal

| Field | Value |
|---|---|
| Recommended pattern | Storytelling-Driven |
| Style priority | Motion-Driven + Minimalism |
| Color mood | Brand primary + Artistic |
| Typography mood | Expressive + Variable typography |
| Key effects | Parallax (3-5 layers) + Scroll-triggered reveals |
| Anti-patterns | Corporate templates + Generic layouts |
| Severity | MEDIUM |

Decision rules (JSON):

```json
{"if_creative_field": "add-brutalism", "if_minimal_portfolio": "reduce-motion"}
```

### 12. Gaming

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich Showcase |
| Style priority | 3D & Hyperrealism + Retro-Futurism |
| Color mood | Vibrant + Neon + Immersive |
| Typography mood | Bold + Impactful typography |
| Key effects | WebGL 3D rendering + Glitch effects |
| Anti-patterns | Minimalist design + Static assets |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_competitive": "add-real-time-stats", "if_casual": "increase-playfulness"}
```

### 13. Government/Public Service

| Field | Value |
|---|---|
| Recommended pattern | Minimal & Direct |
| Style priority | Accessible & Ethical + Minimalism |
| Color mood | Professional blue + High contrast |
| Typography mood | Clear + Large typography |
| Key effects | Clear focus rings (3-4px) + Skip links |
| Anti-patterns | Ornate design + Low contrast + Motion effects + AI purple/pink gradients |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "wcag-aaa", "must_have": "keyboard-navigation"}
```

### 14. Fintech/Crypto

| Field | Value |
|---|---|
| Recommended pattern | Trust & Authority |
| Style priority | Minimalism + Accessible & Ethical |
| Color mood | Navy + Trust Blue + Gold |
| Typography mood | Professional + Trustworthy |
| Key effects | Smooth state transitions + Number animations |
| Anti-patterns | Playful design + Unclear fees + AI purple/pink gradients |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "security-first", "if_dashboard": "use-dark-mode"}
```

### 15. Social Media App

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich Showcase |
| Style priority | Vibrant & Block-based + Motion-Driven |
| Color mood | Vibrant + Engagement colors |
| Typography mood | Modern + Bold typography |
| Key effects | Large scroll animations + Icon animations |
| Anti-patterns | Heavy skeuomorphism + Accessibility ignored |
| Severity | MEDIUM |

Decision rules (JSON):

```json
{"if_engagement_metric": "add-motion", "if_content_focused": "minimize-chrome"}
```

### 16. Productivity Tool

| Field | Value |
|---|---|
| Recommended pattern | Interactive Demo + Feature-Rich |
| Style priority | Flat Design + Micro-interactions |
| Color mood | Clear hierarchy + Functional colors |
| Typography mood | Clean + Efficient typography |
| Key effects | Quick actions (150ms) + Task animations |
| Anti-patterns | Complex onboarding + Slow performance |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "keyboard-shortcuts", "if_collaboration": "add-real-time-cursors"}
```

### 17. Design System/Component Library

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich + Documentation |
| Style priority | Minimalism + Accessible & Ethical |
| Color mood | Clear hierarchy + Code-like structure |
| Typography mood | Monospace + Clear typography |
| Key effects | Code copy animations + Component previews |
| Anti-patterns | Poor documentation + No live preview |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "search", "must_have": "code-examples"}
```

### 18. AI/Chatbot Platform

| Field | Value |
|---|---|
| Recommended pattern | Interactive Demo + Minimal |
| Style priority | AI-Native UI + Minimalism |
| Color mood | Neutral + AI Purple (#6366F1) |
| Typography mood | Modern + Clear typography |
| Key effects | Streaming text + Typing indicators + Fade-in |
| Anti-patterns | Heavy chrome + Slow response feedback |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "conversational-ui", "must_have": "context-awareness"}
```

### 19. NFT/Web3 Platform

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich Showcase |
| Style priority | Cyberpunk UI + Glassmorphism |
| Color mood | Dark + Neon + Gold (#FFD700) |
| Typography mood | Bold + Modern typography |
| Key effects | Wallet connect animations + Transaction feedback |
| Anti-patterns | Light mode default + No transaction status |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "wallet-integration", "must_have": "gas-fees-display"}
```

### 20. Creator Economy Platform

| Field | Value |
|---|---|
| Recommended pattern | Social Proof + Feature-Rich |
| Style priority | Vibrant & Block-based + Bento Box Grid |
| Color mood | Vibrant + Brand colors |
| Typography mood | Modern + Bold typography |
| Key effects | Engagement counter animations + Profile reveals |
| Anti-patterns | Generic layout + Hidden earnings |
| Severity | MEDIUM |

Decision rules (JSON):

```json
{"must_have": "creator-profiles", "must_have": "monetization-display"}
```

### 21. Remote Work/Collaboration Tool

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich + Real-Time |
| Style priority | Soft UI Evolution + Minimalism |
| Color mood | Calm Blue + Neutral grey |
| Typography mood | Clean + Readable typography |
| Key effects | Real-time presence indicators + Notification badges |
| Anti-patterns | Cluttered interface + No presence |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "status-indicators", "must_have": "video-integration"}
```

### 22. Mental Health App

| Field | Value |
|---|---|
| Recommended pattern | Social Proof-Focused |
| Style priority | Neumorphism + Accessible & Ethical |
| Color mood | Calm Pastels + Trust colors |
| Typography mood | Calming + Readable typography |
| Key effects | Soft press + Breathing animations |
| Anti-patterns | Bright neon + Motion overload |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "privacy-first", "if_meditation": "add-breathing-animation"}
```

### 23. Pet Tech App

| Field | Value |
|---|---|
| Recommended pattern | Storytelling + Feature-Rich |
| Style priority | Claymorphism + Vibrant & Block-based |
| Color mood | Playful + Warm colors |
| Typography mood | Friendly + Playful typography |
| Key effects | Pet profile animations + Health tracking charts |
| Anti-patterns | Generic design + No personality |
| Severity | MEDIUM |

Decision rules (JSON):

```json
{"must_have": "pet-profiles", "if_health": "add-vet-integration"}
```

### 24. Smart Home/IoT Dashboard

| Field | Value |
|---|---|
| Recommended pattern | Real-Time Monitoring |
| Style priority | Glassmorphism + Dark Mode (OLED) |
| Color mood | Dark + Status indicator colors |
| Typography mood | Clear + Functional typography |
| Key effects | Device status pulse + Quick action animations |
| Anti-patterns | Slow updates + No automation |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "real-time-controls", "must_have": "energy-monitoring"}
```

### 25. EV/Charging Ecosystem

| Field | Value |
|---|---|
| Recommended pattern | Hero-Centric + Feature-Rich |
| Style priority | Minimalism + Aurora UI |
| Color mood | Electric Blue (#009CD1) + Green |
| Typography mood | Modern + Clear typography |
| Key effects | Range estimation animations + Map interactions |
| Anti-patterns | Poor map UX + Hidden costs |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "charging-map", "must_have": "range-calculator"}
```

### 26. Subscription Box Service

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich + Conversion |
| Style priority | Vibrant & Block-based + Motion-Driven |
| Color mood | Brand + Excitement colors |
| Typography mood | Engaging + Clear typography |
| Key effects | Unboxing reveal animations + Product carousel |
| Anti-patterns | Confusing pricing + No unboxing preview |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "personalization-quiz", "must_have": "subscription-management"}
```

### 27. Podcast Platform

| Field | Value |
|---|---|
| Recommended pattern | Storytelling + Feature-Rich |
| Style priority | Dark Mode (OLED) + Minimalism |
| Color mood | Dark + Audio waveform accents |
| Typography mood | Modern + Clear typography |
| Key effects | Waveform visualizations + Episode transitions |
| Anti-patterns | Poor audio player + Cluttered layout |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "audio-player-ux", "must_have": "episode-discovery"}
```

### 28. Dating App

| Field | Value |
|---|---|
| Recommended pattern | Social Proof + Feature-Rich |
| Style priority | Vibrant & Block-based + Motion-Driven |
| Color mood | Warm + Romantic (Pink/Red gradients) |
| Typography mood | Modern + Friendly typography |
| Key effects | Profile card swipe + Match animations |
| Anti-patterns | Generic profiles + No safety |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "profile-cards", "must_have": "safety-features"}
```

### 29. Micro-Credentials/Badges Platform

| Field | Value |
|---|---|
| Recommended pattern | Trust & Authority + Feature |
| Style priority | Minimalism + Flat Design |
| Color mood | Trust Blue + Gold (#FFD700) |
| Typography mood | Professional + Clear typography |
| Key effects | Badge reveal animations + Progress tracking |
| Anti-patterns | No verification + Hidden progress |
| Severity | MEDIUM |

Decision rules (JSON):

```json
{"must_have": "credential-verification", "must_have": "progress-display"}
```

### 30. Knowledge Base/Documentation

| Field | Value |
|---|---|
| Recommended pattern | FAQ + Minimal |
| Style priority | Minimalism + Accessible & Ethical |
| Color mood | Clean hierarchy + Minimal color |
| Typography mood | Clear + Readable typography |
| Key effects | Search highlight + Smooth scrolling |
| Anti-patterns | Poor navigation + No search |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "search-first", "must_have": "version-switching"}
```

### 31. Hyperlocal Services

| Field | Value |
|---|---|
| Recommended pattern | Conversion + Feature-Rich |
| Style priority | Minimalism + Vibrant & Block-based |
| Color mood | Location markers + Trust colors |
| Typography mood | Clear + Functional typography |
| Key effects | Map hover + Provider card reveals |
| Anti-patterns | No map + Hidden reviews |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "map-integration", "must_have": "booking-system"}
```

### 32. Beauty/Spa/Wellness Service

| Field | Value |
|---|---|
| Recommended pattern | Hero-Centric + Social Proof |
| Style priority | Soft UI Evolution + Neumorphism |
| Color mood | Soft pastels (Pink Sage Cream) + Gold accents |
| Typography mood | Elegant + Calming typography |
| Key effects | Soft shadows + Smooth transitions (200-300ms) + Gentle hover |
| Anti-patterns | Bright neon colors + Harsh animations + Dark mode |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "booking-system", "must_have": "before-after-gallery", "if_luxury": "add-gold-accents"}
```

### 33. Luxury/Premium Brand

| Field | Value |
|---|---|
| Recommended pattern | Storytelling + Feature-Rich |
| Style priority | Liquid Glass + Glassmorphism |
| Color mood | Black + Gold (#FFD700) + White |
| Typography mood | Elegant + Refined typography |
| Key effects | Slow parallax + Premium reveals (400-600ms) |
| Anti-patterns | Cheap visuals + Fast animations |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "high-quality-imagery", "must_have": "storytelling"}
```

### 34. Restaurant/Food Service

| Field | Value |
|---|---|
| Recommended pattern | Hero-Centric + Conversion |
| Style priority | Vibrant & Block-based + Motion-Driven |
| Color mood | Warm colors (Orange Red Brown) |
| Typography mood | Appetizing + Clear typography |
| Key effects | Food image reveal + Menu hover effects |
| Anti-patterns | Low-quality imagery + Outdated hours |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "high_quality_images", "if_delivery": "emphasize-speed"}
```

### 35. Fitness/Gym App

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich + Data |
| Style priority | Vibrant & Block-based + Dark Mode (OLED) |
| Color mood | Energetic (Orange #FF6B35) + Dark bg |
| Typography mood | Bold + Motivational typography |
| Key effects | Progress ring animations + Achievement unlocks |
| Anti-patterns | Static design + No gamification |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "progress-tracking", "must_have": "workout-plans"}
```

### 36. Real Estate/Property

| Field | Value |
|---|---|
| Recommended pattern | Hero-Centric + Feature-Rich |
| Style priority | Glassmorphism + Minimalism |
| Color mood | Trust Blue + Gold + White |
| Typography mood | Professional + Confident |
| Key effects | 3D property tour zoom + Map hover |
| Anti-patterns | Poor photos + No virtual tours |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_luxury": "add-3d-models", "must_have": "map-integration"}
```

### 37. Travel/Tourism Agency

| Field | Value |
|---|---|
| Recommended pattern | Storytelling-Driven + Hero |
| Style priority | Aurora UI + Motion-Driven |
| Color mood | Vibrant destination + Sky Blue |
| Typography mood | Inspirational + Engaging |
| Key effects | Destination parallax + Itinerary animations |
| Anti-patterns | Generic photos + Complex booking |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_experience_focused": "use-storytelling", "must_have": "mobile-booking"}
```

### 38. Hotel/Hospitality

| Field | Value |
|---|---|
| Recommended pattern | Hero-Centric + Social Proof |
| Style priority | Liquid Glass + Minimalism |
| Color mood | Warm neutrals + Gold (#D4AF37) |
| Typography mood | Elegant + Welcoming typography |
| Key effects | Room gallery + Amenity reveals |
| Anti-patterns | Poor photos + Complex booking |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "room-booking", "must_have": "virtual-tour"}
```

### 39. Wedding/Event Planning

| Field | Value |
|---|---|
| Recommended pattern | Storytelling + Social Proof |
| Style priority | Soft UI Evolution + Aurora UI |
| Color mood | Soft Pink (#FFD6E0) + Gold + Cream |
| Typography mood | Elegant + Romantic typography |
| Key effects | Gallery reveals + Timeline animations |
| Anti-patterns | Generic templates + No portfolio |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "portfolio-gallery", "must_have": "planning-tools"}
```

### 40. Legal Services

| Field | Value |
|---|---|
| Recommended pattern | Trust & Authority + Minimal |
| Style priority | Trust & Authority + Minimalism |
| Color mood | Navy Blue (#1E3A5F) + Gold + White |
| Typography mood | Professional + Authoritative typography |
| Key effects | Practice area reveal + Attorney profile animations |
| Anti-patterns | Outdated design + Hidden credentials + AI purple/pink gradients |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "case-results", "must_have": "credential-display"}
```

### 41. Insurance Platform

| Field | Value |
|---|---|
| Recommended pattern | Conversion + Trust |
| Style priority | Trust & Authority + Flat Design |
| Color mood | Trust Blue (#0066CC) + Green + Neutral |
| Typography mood | Clear + Professional typography |
| Key effects | Quote calculator animations + Policy comparison |
| Anti-patterns | Confusing pricing + No trust signals + AI purple/pink gradients |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "quote-calculator", "must_have": "policy-comparison"}
```

### 42. Banking/Traditional Finance

| Field | Value |
|---|---|
| Recommended pattern | Trust & Authority + Feature |
| Style priority | Minimalism + Accessible & Ethical |
| Color mood | Navy (#0A1628) + Trust Blue + Gold |
| Typography mood | Professional + Trustworthy typography |
| Key effects | Smooth number animations + Security indicators |
| Anti-patterns | Playful design + Poor security UX + AI purple/pink gradients |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "security-first", "must_have": "accessibility"}
```

### 43. Online Course/E-learning

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich + Social Proof |
| Style priority | Claymorphism + Vibrant & Block-based |
| Color mood | Vibrant learning colors + Progress green |
| Typography mood | Friendly + Engaging typography |
| Key effects | Progress bar animations + Certificate reveals |
| Anti-patterns | Boring design + No gamification |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "progress-tracking", "must_have": "video-player"}
```

### 44. Non-profit/Charity

| Field | Value |
|---|---|
| Recommended pattern | Storytelling + Trust |
| Style priority | Accessible & Ethical + Organic Biophilic |
| Color mood | Cause-related colors + Trust + Warm |
| Typography mood | Heartfelt + Readable typography |
| Key effects | Impact counter animations + Story reveals |
| Anti-patterns | No impact data + Hidden financials |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "impact-stories", "must_have": "donation-transparency"}
```

### 45. Music Streaming

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich Showcase |
| Style priority | Dark Mode (OLED) + Vibrant & Block-based |
| Color mood | Dark (#121212) + Vibrant accents + Album art colors |
| Typography mood | Modern + Bold typography |
| Key effects | Waveform visualization + Playlist animations |
| Anti-patterns | Cluttered layout + Poor audio player UX |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "audio-player-ux", "if_discovery_focused": "add-playlist-recommendations"}
```

### 46. Video Streaming/OTT

| Field | Value |
|---|---|
| Recommended pattern | Hero-Centric + Feature-Rich |
| Style priority | Dark Mode (OLED) + Motion-Driven |
| Color mood | Dark bg + Poster colors + Brand accent |
| Typography mood | Bold + Engaging typography |
| Key effects | Video player animations + Content carousel (parallax) |
| Anti-patterns | Static layout + Slow video player |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "continue-watching", "if_personalized": "add-recommendations"}
```

### 47. Job Board/Recruitment

| Field | Value |
|---|---|
| Recommended pattern | Conversion-Optimized + Feature-Rich |
| Style priority | Flat Design + Minimalism |
| Color mood | Professional Blue + Success Green + Neutral |
| Typography mood | Clear + Professional typography |
| Key effects | Search/filter animations + Application flow |
| Anti-patterns | Outdated forms + Hidden filters |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "advanced-search", "if_salary_focused": "highlight-compensation"}
```

### 48. Marketplace (P2P)

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich Showcase + Social Proof |
| Style priority | Vibrant & Block-based + Flat Design |
| Color mood | Trust colors + Category colors + Success green |
| Typography mood | Modern + Engaging typography |
| Key effects | Review star animations + Listing hover effects |
| Anti-patterns | Low trust signals + Confusing layout |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "seller-profiles", "must_have": "secure-payment"}
```

### 49. Logistics/Delivery

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich Showcase + Real-Time |
| Style priority | Minimalism + Flat Design |
| Color mood | Blue (#2563EB) + Orange (tracking) + Green |
| Typography mood | Clear + Functional typography |
| Key effects | Real-time tracking animation + Status pulse |
| Anti-patterns | Static tracking + No map integration + AI purple/pink gradients |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "tracking-map", "must_have": "delivery-updates"}
```

### 50. Agriculture/Farm Tech

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich Showcase |
| Style priority | Organic Biophilic + Flat Design |
| Color mood | Earth Green (#4A7C23) + Brown + Sky Blue |
| Typography mood | Clear + Informative typography |
| Key effects | Data visualization + Weather animations |
| Anti-patterns | Generic design + Ignored accessibility + AI purple/pink gradients |
| Severity | MEDIUM |

Decision rules (JSON):

```json
{"must_have": "sensor-dashboard", "if_crop_focused": "add-health-indicators"}
```

### 51. Construction/Architecture

| Field | Value |
|---|---|
| Recommended pattern | Hero-Centric + Feature-Rich |
| Style priority | Minimalism + 3D & Hyperrealism |
| Color mood | Grey (#4A4A4A) + Orange (safety) + Blueprint Blue |
| Typography mood | Professional + Bold typography |
| Key effects | 3D model viewer + Timeline animations |
| Anti-patterns | 2D-only layouts + Poor image quality + AI purple/pink gradients |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "project-portfolio", "if_team_collaboration": "add-real-time-updates"}
```

### 52. Automotive/Car Dealership

| Field | Value |
|---|---|
| Recommended pattern | Hero-Centric + Feature-Rich |
| Style priority | Motion-Driven + 3D & Hyperrealism |
| Color mood | Brand colors + Metallic + Dark/Light |
| Typography mood | Bold + Confident typography |
| Key effects | 360 product view + Configurator animations |
| Anti-patterns | Static product pages + Poor UX |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "vehicle-comparison", "must_have": "financing-calculator"}
```

### 53. Photography Studio

| Field | Value |
|---|---|
| Recommended pattern | Storytelling-Driven + Hero-Centric |
| Style priority | Motion-Driven + Minimalism |
| Color mood | Black + White + Minimal accent |
| Typography mood | Elegant + Minimal typography |
| Key effects | Full-bleed gallery + Before/after reveal |
| Anti-patterns | Heavy text + Poor image showcase |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "portfolio-showcase", "if_booking": "add-calendar-system"}
```

### 54. Coworking Space

| Field | Value |
|---|---|
| Recommended pattern | Hero-Centric + Feature-Rich |
| Style priority | Vibrant & Block-based + Glassmorphism |
| Color mood | Energetic colors + Wood tones + Brand |
| Typography mood | Modern + Engaging typography |
| Key effects | Space tour video + Amenity reveal animations |
| Anti-patterns | Outdated photos + Confusing layout |
| Severity | MEDIUM |

Decision rules (JSON):

```json
{"must_have": "virtual-tour", "must_have": "booking-system"}
```

### 55. Home Services (Plumber/Electrician)

| Field | Value |
|---|---|
| Recommended pattern | Conversion-Optimized + Trust |
| Style priority | Flat Design + Trust & Authority |
| Color mood | Trust Blue + Safety Orange + Grey |
| Typography mood | Professional + Clear typography |
| Key effects | Emergency contact highlight + Service menu animations |
| Anti-patterns | Hidden contact info + No certifications |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "emergency-contact", "must_have": "certifications-display"}
```

### 56. Childcare/Daycare

| Field | Value |
|---|---|
| Recommended pattern | Social Proof-Focused + Trust |
| Style priority | Claymorphism + Vibrant & Block-based |
| Color mood | Playful pastels + Safe colors + Warm |
| Typography mood | Friendly + Playful typography |
| Key effects | Parent portal animations + Activity gallery reveal |
| Anti-patterns | Generic design + Hidden safety info |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "parent-communication", "must_have": "safety-certifications"}
```

### 57. Senior Care/Elderly

| Field | Value |
|---|---|
| Recommended pattern | Trust & Authority + Accessible |
| Style priority | Accessible & Ethical + Soft UI Evolution |
| Color mood | Calm Blue + Warm neutrals + Large text |
| Typography mood | Large + Clear typography (18px+) |
| Key effects | Large touch targets + Clear navigation |
| Anti-patterns | Small text + Complex navigation + AI purple/pink gradients |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "wcag-aaa", "must_have": "family-portal"}
```

### 58. Medical Clinic

| Field | Value |
|---|---|
| Recommended pattern | Trust & Authority + Conversion |
| Style priority | Accessible & Ethical + Minimalism |
| Color mood | Medical Blue (#0077B6) + Trust White |
| Typography mood | Professional + Readable typography |
| Key effects | Online booking flow + Doctor profile reveals |
| Anti-patterns | Outdated interface + Confusing booking + AI purple/pink gradients |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "appointment-booking", "must_have": "insurance-info"}
```

### 59. Pharmacy/Drug Store

| Field | Value |
|---|---|
| Recommended pattern | Conversion-Optimized + Trust |
| Style priority | Flat Design + Accessible & Ethical |
| Color mood | Pharmacy Green + Trust Blue + Clean White |
| Typography mood | Clear + Functional typography |
| Key effects | Prescription upload flow + Refill reminders |
| Anti-patterns | Confusing layout + Privacy concerns + AI purple/pink gradients |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "prescription-management", "must_have": "drug-interaction-warnings"}
```

### 60. Dental Practice

| Field | Value |
|---|---|
| Recommended pattern | Social Proof-Focused + Conversion |
| Style priority | Soft UI Evolution + Minimalism |
| Color mood | Fresh Blue + White + Smile Yellow |
| Typography mood | Friendly + Professional typography |
| Key effects | Before/after gallery + Patient testimonial carousel |
| Anti-patterns | Poor imagery + No testimonials |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "before-after-gallery", "must_have": "appointment-system"}
```

### 61. Veterinary Clinic

| Field | Value |
|---|---|
| Recommended pattern | Social Proof-Focused + Trust |
| Style priority | Claymorphism + Accessible & Ethical |
| Color mood | Caring Blue + Pet colors + Warm |
| Typography mood | Friendly + Welcoming typography |
| Key effects | Pet profile management + Service animations |
| Anti-patterns | Generic design + Hidden services |
| Severity | MEDIUM |

Decision rules (JSON):

```json
{"must_have": "pet-portal", "must_have": "emergency-contact"}
```

### 62. Florist/Plant Shop

| Field | Value |
|---|---|
| Recommended pattern | Hero-Centric + Conversion |
| Style priority | Organic Biophilic + Vibrant & Block-based |
| Color mood | Natural Green + Floral pinks/purples |
| Typography mood | Elegant + Natural typography |
| Key effects | Product reveal + Seasonal transitions |
| Anti-patterns | Poor imagery + No seasonal content |
| Severity | MEDIUM |

Decision rules (JSON):

```json
{"must_have": "delivery-scheduling", "must_have": "care-guides"}
```

### 63. Bakery/Cafe

| Field | Value |
|---|---|
| Recommended pattern | Hero-Centric + Conversion |
| Style priority | Vibrant & Block-based + Soft UI Evolution |
| Color mood | Warm Brown + Cream + Appetizing accents |
| Typography mood | Warm + Inviting typography |
| Key effects | Menu hover + Order animations |
| Anti-patterns | Poor food photos + Hidden hours |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "menu-display", "must_have": "online-ordering"}
```

### 64. Brewery/Winery

| Field | Value |
|---|---|
| Recommended pattern | Storytelling + Hero-Centric |
| Style priority | Motion-Driven + Storytelling-Driven |
| Color mood | Deep amber/burgundy + Gold + Craft |
| Typography mood | Artisanal + Heritage typography |
| Key effects | Tasting note reveals + Heritage timeline |
| Anti-patterns | Generic product pages + No story |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "product-showcase", "must_have": "story-heritage"}
```

### 65. Airline

| Field | Value |
|---|---|
| Recommended pattern | Conversion + Feature-Rich |
| Style priority | Minimalism + Glassmorphism |
| Color mood | Sky Blue + Brand colors + Trust |
| Typography mood | Clear + Professional typography |
| Key effects | Flight search animations + Boarding pass reveals |
| Anti-patterns | Complex booking + Poor mobile |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "flight-search", "must_have": "mobile-first"}
```

### 66. News/Media Platform

| Field | Value |
|---|---|
| Recommended pattern | Hero-Centric + Feature-Rich |
| Style priority | Minimalism + Flat Design |
| Color mood | Brand colors + High contrast |
| Typography mood | Clear + Readable typography |
| Key effects | Breaking news badge + Article reveal animations |
| Anti-patterns | Cluttered layout + Slow loading |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "mobile-first-reading", "must_have": "category-navigation"}
```

### 67. Magazine/Blog

| Field | Value |
|---|---|
| Recommended pattern | Storytelling + Hero-Centric |
| Style priority | Swiss Modernism 2.0 + Motion-Driven |
| Color mood | Editorial colors + Brand + Clean white |
| Typography mood | Editorial + Elegant typography |
| Key effects | Article transitions + Category reveals |
| Anti-patterns | Poor typography + Slow loading |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "article-showcase", "must_have": "newsletter-signup"}
```

### 68. Freelancer Platform

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich + Conversion |
| Style priority | Flat Design + Minimalism |
| Color mood | Professional Blue + Success Green |
| Typography mood | Clear + Professional typography |
| Key effects | Skill match animations + Review reveals |
| Anti-patterns | Poor profiles + No reviews |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "portfolio-display", "must_have": "skill-matching"}
```

### 69. Marketing Agency

| Field | Value |
|---|---|
| Recommended pattern | Storytelling + Feature-Rich |
| Style priority | Brutalism + Motion-Driven |
| Color mood | Bold brand colors + Creative freedom |
| Typography mood | Bold + Expressive typography |
| Key effects | Portfolio reveals + Results animations |
| Anti-patterns | Boring design + Hidden work |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "portfolio", "must_have": "results-metrics"}
```

### 70. Event Management

| Field | Value |
|---|---|
| Recommended pattern | Hero-Centric + Feature-Rich |
| Style priority | Vibrant & Block-based + Motion-Driven |
| Color mood | Event theme colors + Excitement accents |
| Typography mood | Bold + Engaging typography |
| Key effects | Countdown timer + Registration flow |
| Anti-patterns | Confusing registration + No countdown |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "registration", "must_have": "agenda-display"}
```

### 71. Membership/Community

| Field | Value |
|---|---|
| Recommended pattern | Social Proof + Conversion |
| Style priority | Vibrant & Block-based + Soft UI Evolution |
| Color mood | Community brand colors + Engagement |
| Typography mood | Friendly + Engaging typography |
| Key effects | Member counter + Benefit reveals |
| Anti-patterns | Hidden benefits + No community proof |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "member-benefits", "must_have": "pricing-tiers"}
```

### 72. Newsletter Platform

| Field | Value |
|---|---|
| Recommended pattern | Minimal + Conversion |
| Style priority | Minimalism + Flat Design |
| Color mood | Brand primary + Clean white + CTA |
| Typography mood | Clean + Readable typography |
| Key effects | Subscribe form + Archive reveals |
| Anti-patterns | Complex signup + No preview |
| Severity | MEDIUM |

Decision rules (JSON):

```json
{"must_have": "subscribe-form", "must_have": "sample-content"}
```

### 73. Digital Products/Downloads

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich + Conversion |
| Style priority | Vibrant & Block-based + Motion-Driven |
| Color mood | Product colors + Brand + Success green |
| Typography mood | Modern + Clear typography |
| Key effects | Product preview + Instant delivery animations |
| Anti-patterns | No preview + Slow delivery |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "product-preview", "must_have": "instant-delivery"}
```

### 74. Church/Religious Organization

| Field | Value |
|---|---|
| Recommended pattern | Hero-Centric + Social Proof |
| Style priority | Accessible & Ethical + Soft UI Evolution |
| Color mood | Warm Gold + Deep Purple/Blue + White |
| Typography mood | Welcoming + Clear typography |
| Key effects | Service time highlights + Event calendar |
| Anti-patterns | Outdated design + Hidden info |
| Severity | MEDIUM |

Decision rules (JSON):

```json
{"must_have": "service-times", "must_have": "community-events"}
```

### 75. Sports Team/Club

| Field | Value |
|---|---|
| Recommended pattern | Hero-Centric + Feature-Rich |
| Style priority | Vibrant & Block-based + Motion-Driven |
| Color mood | Team colors + Energetic accents |
| Typography mood | Bold + Impactful typography |
| Key effects | Score animations + Schedule reveals |
| Anti-patterns | Static content + Poor fan engagement |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "schedule", "must_have": "roster"}
```

### 76. Museum/Gallery

| Field | Value |
|---|---|
| Recommended pattern | Storytelling + Feature-Rich |
| Style priority | Minimalism + Motion-Driven |
| Color mood | Art-appropriate neutrals + Exhibition accents |
| Typography mood | Elegant + Minimal typography |
| Key effects | Virtual tour + Collection reveals |
| Anti-patterns | Cluttered layout + No online access |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "virtual-tour", "must_have": "exhibition-info"}
```

### 77. Theater/Cinema

| Field | Value |
|---|---|
| Recommended pattern | Hero-Centric + Conversion |
| Style priority | Dark Mode (OLED) + Motion-Driven |
| Color mood | Dark + Spotlight accents + Gold |
| Typography mood | Dramatic + Bold typography |
| Key effects | Seat selection + Trailer reveals |
| Anti-patterns | Poor booking UX + No trailers |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "showtimes", "must_have": "seat-selection"}
```

### 78. Language Learning App

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich + Social Proof |
| Style priority | Claymorphism + Vibrant & Block-based |
| Color mood | Playful colors + Progress indicators |
| Typography mood | Friendly + Clear typography |
| Key effects | Progress animations + Achievement unlocks |
| Anti-patterns | Boring design + No motivation |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "progress-tracking", "must_have": "gamification"}
```

### 79. Coding Bootcamp

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich + Social Proof |
| Style priority | Dark Mode (OLED) + Minimalism |
| Color mood | Code editor colors + Brand + Success |
| Typography mood | Technical + Clear typography |
| Key effects | Terminal animations + Career outcome reveals |
| Anti-patterns | Light mode only + Hidden results |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "curriculum", "must_have": "career-outcomes"}
```

### 80. Cybersecurity Platform

| Field | Value |
|---|---|
| Recommended pattern | Trust & Authority + Real-Time |
| Style priority | Cyberpunk UI + Dark Mode (OLED) |
| Color mood | Matrix Green (#00FF00) + Deep Black |
| Typography mood | Technical + Clear typography |
| Key effects | Threat visualization + Alert animations |
| Anti-patterns | Light mode + Poor data viz |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "real-time-monitoring", "must_have": "threat-display"}
```

### 81. Developer Tool / IDE

| Field | Value |
|---|---|
| Recommended pattern | Minimal + Documentation |
| Style priority | Dark Mode (OLED) + Minimalism |
| Color mood | Dark syntax theme + Blue focus |
| Typography mood | Monospace + Functional typography |
| Key effects | Syntax highlighting + Command palette |
| Anti-patterns | Light mode default + Slow performance |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "keyboard-shortcuts", "must_have": "documentation"}
```

### 82. Biotech / Life Sciences

| Field | Value |
|---|---|
| Recommended pattern | Storytelling + Data |
| Style priority | Glassmorphism + Clean Science |
| Color mood | Sterile White + DNA Blue + Life Green |
| Typography mood | Scientific + Clear typography |
| Key effects | Data visualization + Research reveals |
| Anti-patterns | Cluttered data + Poor credibility |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "data-accuracy", "must_have": "clean-aesthetic"}
```

### 83. Space Tech / Aerospace

| Field | Value |
|---|---|
| Recommended pattern | Immersive + Feature-Rich |
| Style priority | Holographic/HUD + Dark Mode |
| Color mood | Deep Space Black + Star White + Metallic |
| Typography mood | Futuristic + Precise typography |
| Key effects | Telemetry animations + 3D renders |
| Anti-patterns | Generic design + No immersion |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "high-tech-feel", "must_have": "precision-data"}
```

### 84. Architecture / Interior

| Field | Value |
|---|---|
| Recommended pattern | Portfolio + Hero-Centric |
| Style priority | Exaggerated Minimalism + High Imagery |
| Color mood | Monochrome + Gold Accent + High Imagery |
| Typography mood | Architectural + Elegant typography |
| Key effects | Project gallery + Blueprint reveals |
| Anti-patterns | Poor imagery + Cluttered layout |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "high-res-images", "must_have": "project-portfolio"}
```

### 85. Quantum Computing Interface

| Field | Value |
|---|---|
| Recommended pattern | Immersive + Interactive |
| Style priority | Holographic/HUD + Dark Mode |
| Color mood | Quantum Blue (#00FFFF) + Deep Black |
| Typography mood | Futuristic + Scientific typography |
| Key effects | Probability visualizations + Qubit state animations |
| Anti-patterns | Generic tech design + No viz |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "complexity-visualization", "must_have": "scientific-credibility"}
```

### 86. Biohacking / Longevity App

| Field | Value |
|---|---|
| Recommended pattern | Data-Dense + Storytelling |
| Style priority | Biomimetic/Organic 2.0 + Minimalism |
| Color mood | Cellular Pink/Red + DNA Blue + White |
| Typography mood | Scientific + Clear typography |
| Key effects | Biological data viz + Progress animations |
| Anti-patterns | Generic health app + No privacy |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "data-privacy", "must_have": "scientific-credibility"}
```

### 87. Autonomous Drone Fleet Manager

| Field | Value |
|---|---|
| Recommended pattern | Real-Time + Feature-Rich |
| Style priority | HUD/Sci-Fi FUI + Real-Time |
| Color mood | Tactical Green + Alert Red + Map Dark |
| Typography mood | Technical + Functional typography |
| Key effects | Telemetry animations + 3D spatial awareness |
| Anti-patterns | Slow updates + Poor spatial viz |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "real-time-telemetry", "must_have": "safety-alerts"}
```

### 88. Generative Art Platform

| Field | Value |
|---|---|
| Recommended pattern | Showcase + Feature-Rich |
| Style priority | Minimalism + Gen Z Chaos |
| Color mood | Neutral (#F5F5F5) + User Content |
| Typography mood | Minimal + Content-focused typography |
| Key effects | Gallery masonry + Minting animations |
| Anti-patterns | Heavy chrome + Slow loading |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "fast-loading", "must_have": "creator-attribution"}
```

### 89. Spatial Computing OS / App

| Field | Value |
|---|---|
| Recommended pattern | Immersive + Interactive |
| Style priority | Spatial UI (VisionOS) + Glassmorphism |
| Color mood | Frosted Glass + System Colors + Depth |
| Typography mood | Spatial + Readable typography |
| Key effects | Depth hierarchy + Gaze interactions |
| Anti-patterns | 2D design + No spatial depth |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "depth-hierarchy", "must_have": "environment-awareness"}
```

### 90. Sustainable Energy / Climate Tech

| Field | Value |
|---|---|
| Recommended pattern | Data + Trust |
| Style priority | Organic Biophilic + E-Ink/Paper |
| Color mood | Earth Green + Sky Blue + Solar Yellow |
| Typography mood | Clear + Informative typography |
| Key effects | Impact viz + Progress animations |
| Anti-patterns | Greenwashing + No real data |
| Severity | HIGH |

Decision rules (JSON):

```json
{"must_have": "data-transparency", "must_have": "impact-visualization"}
```

### 91. Personal Finance Tracker

| Field | Value |
|---|---|
| Recommended pattern | Interactive Product Demo |
| Style priority | Glassmorphism + Dark Mode (OLED) |
| Color mood | Calm blue + success green + alert red + chart accents |
| Typography mood | Modern + Clear hierarchy |
| Key effects | Backdrop blur (10-20px) + Translucent overlays |
| Anti-patterns | Pure white backgrounds |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_light_mode_needed": "provide-theme-toggle", "if_low_performance": "fallback-to-flat"}
```

### 92. Chat & Messaging App

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich Showcase + Demo |
| Style priority | Minimalism + Micro-interactions |
| Color mood | Brand primary + bubble contrast (sender/receiver) + typing grey |
| Typography mood | Professional + Clean hierarchy |
| Key effects | Subtle hover 200ms + Smooth transitions + Clean |
| Anti-patterns | Excessive decoration |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_ux_focused": "prioritize-clarity", "if_mobile": "optimize-touch-targets"}
```

### 93. Notes & Writing App

| Field | Value |
|---|---|
| Recommended pattern | Minimal & Direct |
| Style priority | Minimalism + Flat Design |
| Color mood | Clean white/cream + minimal accent + editor syntax colors |
| Typography mood | Professional + Clean hierarchy |
| Key effects | Color shift hover + Fast 150ms transitions + No shadows |
| Anti-patterns | Excessive decoration + Complex shadows + 3D effects |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_ux_focused": "prioritize-clarity", "if_mobile": "optimize-touch-targets"}
```

### 94. Habit Tracker

| Field | Value |
|---|---|
| Recommended pattern | Social Proof-Focused + Demo |
| Style priority | Claymorphism + Vibrant & Block-based |
| Color mood | Streak warm (amber/orange) + progress green + motivational accents |
| Typography mood | Playful + Rounded + Friendly |
| Key effects | Multi-layer shadows + Spring bounce + Soft press 200ms |
| Anti-patterns | Muted colors + Low energy |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_trust_needed": "add-testimonials"}
```

### 95. Food Delivery / On-Demand

| Field | Value |
|---|---|
| Recommended pattern | Hero-Centric Design + Feature-Rich |
| Style priority | Vibrant & Block-based + Motion-Driven |
| Color mood | Appetizing warm (orange/red) + trust blue + map accent |
| Typography mood | Energetic + Bold + Large |
| Key effects | Scroll animations + Parallax + Page transitions |
| Anti-patterns | Muted colors + Low energy |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_ux_focused": "prioritize-clarity", "if_mobile": "optimize-touch-targets"}
```

### 96. Ride Hailing / Transportation

| Field | Value |
|---|---|
| Recommended pattern | Conversion-Optimized + Demo |
| Style priority | Minimalism + Glassmorphism |
| Color mood | Brand primary + map neutral + status indicator colors |
| Typography mood | Professional + Clean hierarchy |
| Key effects | Backdrop blur (10-20px) + Translucent overlays |
| Anti-patterns | Excessive decoration |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_low_performance": "fallback-to-flat", "if_conversion_focused": "add-urgency-colors"}
```

### 97. Recipe & Cooking App

| Field | Value |
|---|---|
| Recommended pattern | Hero-Centric Design + Feature-Rich |
| Style priority | Claymorphism + Vibrant & Block-based |
| Color mood | Warm food tones (terracotta/sage/cream) + appetizing imagery |
| Typography mood | Playful + Rounded + Friendly |
| Key effects | Multi-layer shadows + Spring bounce + Soft press 200ms |
| Anti-patterns | Muted colors + Low energy |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_ux_focused": "prioritize-clarity", "if_mobile": "optimize-touch-targets"}
```

### 98. Meditation & Mindfulness

| Field | Value |
|---|---|
| Recommended pattern | Storytelling-Driven + Social Proof |
| Style priority | Neumorphism + Soft UI Evolution |
| Color mood | Ultra-calm pastels (lavender/sage/sky) + breathing animation gradient |
| Typography mood | Subtle + Soft + Monochromatic |
| Key effects | Dual shadows (light+dark) + Soft press 150ms |
| Anti-patterns | Inconsistent styling + Poor contrast ratios |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_trust_needed": "add-testimonials"}
```

### 99. Weather App

| Field | Value |
|---|---|
| Recommended pattern | Hero-Centric Design |
| Style priority | Glassmorphism + Aurora UI |
| Color mood | Atmospheric gradients (sky blue → sunset → storm grey) + temp scale |
| Typography mood | Modern + Clear hierarchy |
| Key effects | Backdrop blur (10-20px) + Translucent overlays |
| Anti-patterns | Inconsistent styling + Poor contrast ratios |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_low_performance": "fallback-to-flat"}
```

### 100. Diary & Journal App

| Field | Value |
|---|---|
| Recommended pattern | Storytelling-Driven |
| Style priority | Soft UI Evolution + Minimalism |
| Color mood | Warm paper tones (cream/linen) + muted ink + mood-coded accents |
| Typography mood | Professional + Clean hierarchy |
| Key effects | Subtle hover 200ms + Smooth transitions + Clean |
| Anti-patterns | Excessive decoration |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_ux_focused": "prioritize-clarity", "if_mobile": "optimize-touch-targets"}
```

### 101. CRM & Client Management

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich Showcase + Demo |
| Style priority | Flat Design + Minimalism |
| Color mood | Professional blue + pipeline stage colors + closed-won green |
| Typography mood | Professional + Clean hierarchy |
| Key effects | Color shift hover + Fast 150ms transitions + No shadows |
| Anti-patterns | Excessive decoration + Complex shadows + 3D effects |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_ux_focused": "prioritize-clarity", "if_mobile": "optimize-touch-targets"}
```

### 102. Inventory & Stock Management

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich Showcase |
| Style priority | Flat Design + Minimalism |
| Color mood | Functional neutral + status traffic-light (green/amber/red) + scanner accent |
| Typography mood | Professional + Clean hierarchy |
| Key effects | Color shift hover + Fast 150ms transitions + No shadows |
| Anti-patterns | Excessive decoration + Complex shadows + 3D effects |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_ux_focused": "prioritize-clarity", "if_mobile": "optimize-touch-targets"}
```

### 103. Flashcard & Study Tool

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich Showcase + Demo |
| Style priority | Claymorphism + Micro-interactions |
| Color mood | Playful primary + correct green + incorrect red + progress blue |
| Typography mood | Playful + Rounded + Friendly |
| Key effects | Multi-layer shadows + Spring bounce + Soft press 200ms |
| Anti-patterns | Inconsistent styling + Poor contrast ratios |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_ux_focused": "prioritize-clarity", "if_mobile": "optimize-touch-targets"}
```

### 104. Booking & Appointment App

| Field | Value |
|---|---|
| Recommended pattern | Conversion-Optimized |
| Style priority | Soft UI Evolution + Flat Design |
| Color mood | Trust blue + available green + booked grey + confirm accent |
| Typography mood | Bold + Clean + Sans-serif |
| Key effects | Color shift hover + Fast 150ms transitions + No shadows |
| Anti-patterns | Complex shadows + 3D effects |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_conversion_focused": "add-urgency-colors"}
```

### 105. Invoice & Billing Tool

| Field | Value |
|---|---|
| Recommended pattern | Conversion-Optimized + Trust |
| Style priority | Minimalism + Flat Design |
| Color mood | Professional navy + paid green + overdue red + neutral grey |
| Typography mood | Professional + Clean hierarchy |
| Key effects | Color shift hover + Fast 150ms transitions + No shadows |
| Anti-patterns | Excessive decoration + Complex shadows + 3D effects |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_conversion_focused": "add-urgency-colors"}
```

### 106. Grocery & Shopping List

| Field | Value |
|---|---|
| Recommended pattern | Minimal & Direct + Demo |
| Style priority | Flat Design + Vibrant & Block-based |
| Color mood | Fresh green + food-category colors + checkmark accent |
| Typography mood | Bold + Clean + Sans-serif |
| Key effects | Color shift hover + Fast 150ms transitions + No shadows |
| Anti-patterns | Complex shadows + 3D effects + Muted colors + Low energy |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_ux_focused": "prioritize-clarity", "if_mobile": "optimize-touch-targets"}
```

### 107. Timer & Pomodoro

| Field | Value |
|---|---|
| Recommended pattern | Minimal & Direct |
| Style priority | Minimalism + Neumorphism |
| Color mood | High-contrast on dark + focus red/amber + break green |
| Typography mood | Professional + Clean hierarchy |
| Key effects | Dual shadows (light+dark) + Soft press 150ms |
| Anti-patterns | Excessive decoration |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_ux_focused": "prioritize-clarity", "if_mobile": "optimize-touch-targets"}
```

### 108. Parenting & Baby Tracker

| Field | Value |
|---|---|
| Recommended pattern | Social Proof-Focused + Trust |
| Style priority | Claymorphism + Soft UI Evolution |
| Color mood | Soft pastels (baby pink/sky blue/mint/peach) + warm accents |
| Typography mood | Playful + Rounded + Friendly |
| Key effects | Multi-layer shadows + Spring bounce + Soft press 200ms |
| Anti-patterns | Inconsistent styling + Poor contrast ratios |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_trust_needed": "add-testimonials"}
```

### 109. Scanner & Document Manager

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich Showcase + Demo |
| Style priority | Minimalism + Flat Design |
| Color mood | Clean white + camera viewfinder accent + file-type color coding |
| Typography mood | Professional + Clean hierarchy |
| Key effects | Color shift hover + Fast 150ms transitions + No shadows |
| Anti-patterns | Excessive decoration + Complex shadows + 3D effects |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_ux_focused": "prioritize-clarity", "if_mobile": "optimize-touch-targets"}
```

### 110. Calendar & Scheduling App

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich Showcase + Demo |
| Style priority | Flat Design + Micro-interactions |
| Color mood | Clean blue + event category accent colors + success green |
| Typography mood | Bold + Clean + Sans-serif |
| Key effects | Color shift hover + Fast 150ms transitions + No shadows |
| Anti-patterns | Complex shadows + 3D effects |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_ux_focused": "prioritize-clarity", "if_mobile": "optimize-touch-targets"}
```

### 111. Password Manager

| Field | Value |
|---|---|
| Recommended pattern | Trust & Authority + Feature-Rich |
| Style priority | Minimalism + Accessible & Ethical |
| Color mood | Trust blue + security green + dark neutral |
| Typography mood | Professional + Clean hierarchy |
| Key effects | Subtle hover 200ms + Smooth transitions + Clean |
| Anti-patterns | Excessive decoration + Color-only indicators |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_ux_focused": "prioritize-clarity", "if_mobile": "optimize-touch-targets"}
```

### 112. Expense Splitter / Bill Split

| Field | Value |
|---|---|
| Recommended pattern | Minimal & Direct + Demo |
| Style priority | Flat Design + Vibrant & Block-based |
| Color mood | Success green + alert red + neutral grey + avatar accent colors |
| Typography mood | Bold + Clean + Sans-serif |
| Key effects | Color shift hover + Fast 150ms transitions + No shadows |
| Anti-patterns | Complex shadows + 3D effects + Muted colors + Low energy |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_ux_focused": "prioritize-clarity", "if_mobile": "optimize-touch-targets"}
```

### 113. Voice Recorder & Memo

| Field | Value |
|---|---|
| Recommended pattern | Interactive Product Demo + Minimal |
| Style priority | Minimalism + AI-Native UI |
| Color mood | Clean white + recording red + waveform accent |
| Typography mood | Professional + Clean hierarchy |
| Key effects | Subtle hover 200ms + Smooth transitions + Clean |
| Anti-patterns | Excessive decoration |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_ux_focused": "prioritize-clarity", "if_mobile": "optimize-touch-targets"}
```

### 114. Bookmark & Read-Later

| Field | Value |
|---|---|
| Recommended pattern | Minimal & Direct + Demo |
| Style priority | Minimalism + Flat Design |
| Color mood | Paper warm white + ink neutral + minimal accent + tag colors |
| Typography mood | Professional + Clean hierarchy |
| Key effects | Color shift hover + Fast 150ms transitions + No shadows |
| Anti-patterns | Excessive decoration + Complex shadows + 3D effects |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_ux_focused": "prioritize-clarity", "if_mobile": "optimize-touch-targets"}
```

### 115. Translator App

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich Showcase + Interactive Demo |
| Style priority | Flat Design + AI-Native UI |
| Color mood | Global blue + neutral grey + language flag accent |
| Typography mood | Bold + Clean + Sans-serif |
| Key effects | Color shift hover + Fast 150ms transitions + No shadows |
| Anti-patterns | Complex shadows + 3D effects |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_ux_focused": "prioritize-clarity", "if_mobile": "optimize-touch-targets"}
```

### 116. Calculator & Unit Converter

| Field | Value |
|---|---|
| Recommended pattern | Minimal & Direct |
| Style priority | Neumorphism + Minimalism |
| Color mood | Dark functional + orange operation keys + clear button hierarchy |
| Typography mood | Professional + Clean hierarchy |
| Key effects | Dual shadows (light+dark) + Soft press 150ms |
| Anti-patterns | Excessive decoration |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_ux_focused": "prioritize-clarity", "if_mobile": "optimize-touch-targets"}
```

### 117. Alarm & World Clock

| Field | Value |
|---|---|
| Recommended pattern | Minimal & Direct |
| Style priority | Dark Mode (OLED) + Minimalism |
| Color mood | Deep dark + ambient glow accent + timezone gradient |
| Typography mood | Professional + Clean hierarchy |
| Key effects | Subtle glow + Neon accents + High contrast |
| Anti-patterns | Excessive decoration + Pure white backgrounds |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_light_mode_needed": "provide-theme-toggle"}
```

### 118. File Manager & Transfer

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich Showcase + Demo |
| Style priority | Flat Design + Minimalism |
| Color mood | Functional neutral + file type color coding (PDF orange, doc blue, image purple) |
| Typography mood | Professional + Clean hierarchy |
| Key effects | Color shift hover + Fast 150ms transitions + No shadows |
| Anti-patterns | Excessive decoration + Complex shadows + 3D effects |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_ux_focused": "prioritize-clarity", "if_mobile": "optimize-touch-targets"}
```

### 119. Email Client

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich Showcase + Demo |
| Style priority | Flat Design + Minimalism |
| Color mood | Clean white + brand primary + priority red + snooze amber |
| Typography mood | Professional + Clean hierarchy |
| Key effects | Color shift hover + Fast 150ms transitions + No shadows |
| Anti-patterns | Excessive decoration + Complex shadows + 3D effects |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_ux_focused": "prioritize-clarity", "if_mobile": "optimize-touch-targets"}
```

### 120. Casual Puzzle Game

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich Showcase + Social Proof |
| Style priority | Claymorphism + Vibrant & Block-based |
| Color mood | Cheerful pastels + progression gradient + reward gold + bright accent |
| Typography mood | Playful + Rounded + Friendly |
| Key effects | Multi-layer shadows + Spring bounce + Soft press 200ms |
| Anti-patterns | Muted colors + Low energy |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_trust_needed": "add-testimonials"}
```

### 121. Trivia & Quiz Game

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich Showcase + Social Proof |
| Style priority | Vibrant & Block-based + Micro-interactions |
| Color mood | Energetic blue + correct green + incorrect red + leaderboard gold |
| Typography mood | Energetic + Bold + Large |
| Key effects | Haptic feedback + Small 50-100ms animations |
| Anti-patterns | Muted colors + Low energy |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_trust_needed": "add-testimonials"}
```

### 122. Card & Board Game

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich Showcase |
| Style priority | 3D & Hyperrealism + Flat Design |
| Color mood | Game-theme felt green + dark wood + card back patterns |
| Typography mood | Bold + Clean + Sans-serif |
| Key effects | Color shift hover + Fast 150ms transitions + No shadows |
| Anti-patterns | Complex shadows + 3D effects |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_ux_focused": "prioritize-clarity", "if_mobile": "optimize-touch-targets"}
```

### 123. Idle & Clicker Game

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich Showcase |
| Style priority | Vibrant & Block-based + Motion-Driven |
| Color mood | Coin gold + upgrade blue + prestige purple + progress green |
| Typography mood | Energetic + Bold + Large |
| Key effects | Scroll animations + Parallax + Page transitions |
| Anti-patterns | Muted colors + Low energy |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_ux_focused": "prioritize-clarity", "if_mobile": "optimize-touch-targets"}
```

### 124. Word & Crossword Game

| Field | Value |
|---|---|
| Recommended pattern | Minimal & Direct + Demo |
| Style priority | Minimalism + Flat Design |
| Color mood | Clean white + warm letter tiles + success green + shake red |
| Typography mood | Professional + Clean hierarchy |
| Key effects | Color shift hover + Fast 150ms transitions + No shadows |
| Anti-patterns | Excessive decoration + Complex shadows + 3D effects |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_ux_focused": "prioritize-clarity", "if_mobile": "optimize-touch-targets"}
```

### 125. Arcade & Retro Game

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich Showcase + Hero-Centric |
| Style priority | Pixel Art + Retro-Futurism |
| Color mood | Neon on black + pixel palette + score gold + danger red |
| Typography mood | Nostalgic + Monospace + Neon |
| Key effects | Subtle hover (200ms) + Smooth transitions |
| Anti-patterns | Inconsistent styling + Poor contrast ratios |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_ux_focused": "prioritize-clarity", "if_mobile": "optimize-touch-targets"}
```

### 126. Photo Editor & Filters

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich Showcase + Interactive Demo |
| Style priority | Minimalism + Dark Mode (OLED) |
| Color mood | Dark editor background + vibrant filter preview strip + tool icon accent |
| Typography mood | Professional + Clean hierarchy |
| Key effects | Subtle glow + Neon accents + High contrast |
| Anti-patterns | Excessive decoration + Pure white backgrounds |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_light_mode_needed": "provide-theme-toggle"}
```

### 127. Short Video Editor

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich Showcase + Hero-Centric |
| Style priority | Dark Mode (OLED) + Motion-Driven |
| Color mood | Dark background + timeline track accent colors + effect preview vivid |
| Typography mood | High contrast + Light on dark |
| Key effects | Subtle glow + Neon accents + High contrast |
| Anti-patterns | Pure white backgrounds |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_light_mode_needed": "provide-theme-toggle"}
```

### 128. Drawing & Sketching Canvas

| Field | Value |
|---|---|
| Recommended pattern | Interactive Product Demo + Storytelling |
| Style priority | Minimalism + Dark Mode (OLED) |
| Color mood | Neutral canvas + full-spectrum color picker + tool panel dark |
| Typography mood | Professional + Clean hierarchy |
| Key effects | Subtle glow + Neon accents + High contrast |
| Anti-patterns | Excessive decoration + Pure white backgrounds |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_light_mode_needed": "provide-theme-toggle"}
```

### 129. Music Creation & Beat Maker

| Field | Value |
|---|---|
| Recommended pattern | Interactive Product Demo + Storytelling |
| Style priority | Dark Mode (OLED) + Motion-Driven |
| Color mood | Dark studio background + track colors rainbow + waveform accent + BPM pulse |
| Typography mood | High contrast + Light on dark |
| Key effects | Subtle glow + Neon accents + High contrast |
| Anti-patterns | Pure white backgrounds |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_light_mode_needed": "provide-theme-toggle"}
```

### 130. Meme & Sticker Maker

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich Showcase + Social Proof |
| Style priority | Vibrant & Block-based + Flat Design |
| Color mood | Bold primary + comedic yellow + viral red + high saturation accent |
| Typography mood | Bold + Clean + Sans-serif |
| Key effects | Color shift hover + Fast 150ms transitions + No shadows |
| Anti-patterns | Complex shadows + 3D effects + Muted colors + Low energy |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_trust_needed": "add-testimonials"}
```

### 131. AI Photo & Avatar Generator

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich Showcase + Social Proof |
| Style priority | AI-Native UI + Aurora UI |
| Color mood | AI purple + aurora gradients + before/after neutral |
| Typography mood | Elegant + Gradient-friendly |
| Key effects | Flowing gradients 8-12s + Color morphing |
| Anti-patterns | Inconsistent styling + Poor contrast ratios |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_trust_needed": "add-testimonials"}
```

### 132. Link-in-Bio Page Builder

| Field | Value |
|---|---|
| Recommended pattern | Conversion-Optimized + Social Proof |
| Style priority | Vibrant & Block-based + Bento Box Grid |
| Color mood | Brand-customizable + accent link color + clean white canvas |
| Typography mood | Energetic + Bold + Large |
| Key effects | Large section gaps 48px+ + Color shift hover + Scroll-snap |
| Anti-patterns | Muted colors + Low energy |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_conversion_focused": "add-urgency-colors", "if_trust_needed": "add-testimonials"}
```

### 133. Wardrobe & Outfit Planner

| Field | Value |
|---|---|
| Recommended pattern | Storytelling-Driven + Feature-Rich |
| Style priority | Minimalism + Motion-Driven |
| Color mood | Clean fashion neutral + full clothes color palette + accent |
| Typography mood | Professional + Clean hierarchy |
| Key effects | Subtle hover 200ms + Smooth transitions + Clean |
| Anti-patterns | Excessive decoration |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_ux_focused": "prioritize-clarity", "if_mobile": "optimize-touch-targets"}
```

### 134. Plant Care Tracker

| Field | Value |
|---|---|
| Recommended pattern | Storytelling-Driven + Social Proof |
| Style priority | Organic Biophilic + Soft UI Evolution |
| Color mood | Nature greens + earth brown + sunny yellow reminder + water blue |
| Typography mood | Warm + Humanist + Natural |
| Key effects | Rounded 16-24px + Natural shadows + Flowing SVG |
| Anti-patterns | Inconsistent styling + Poor contrast ratios |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_trust_needed": "add-testimonials"}
```

### 135. Book & Reading Tracker

| Field | Value |
|---|---|
| Recommended pattern | Social Proof-Focused + Feature-Rich |
| Style priority | Swiss Modernism 2.0 + Minimalism |
| Color mood | Warm paper white + ink brown + reading progress green + book cover colors |
| Typography mood | Professional + Clean hierarchy |
| Key effects | Subtle hover 200ms + Smooth transitions + Clean |
| Anti-patterns | Excessive decoration |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_trust_needed": "add-testimonials"}
```

### 136. Couple & Relationship App

| Field | Value |
|---|---|
| Recommended pattern | Storytelling-Driven + Social Proof |
| Style priority | Aurora UI + Soft UI Evolution |
| Color mood | Warm romantic pink/rose + soft gradient + memory photo tones |
| Typography mood | Elegant + Gradient-friendly |
| Key effects | Flowing gradients 8-12s + Color morphing |
| Anti-patterns | Inconsistent styling + Poor contrast ratios |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_trust_needed": "add-testimonials"}
```

### 137. Family Calendar & Chores

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich Showcase + Social Proof |
| Style priority | Flat Design + Claymorphism |
| Color mood | Warm playful + member color coding + chore completion green |
| Typography mood | Playful + Rounded + Friendly |
| Key effects | Multi-layer shadows + Spring bounce + Soft press 200ms |
| Anti-patterns | Complex shadows + 3D effects |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_trust_needed": "add-testimonials"}
```

### 138. Mood Tracker

| Field | Value |
|---|---|
| Recommended pattern | Storytelling-Driven + Social Proof |
| Style priority | Soft UI Evolution + Minimalism |
| Color mood | Emotion gradient (blue sad to yellow happy) + pastel per mood + insight accent |
| Typography mood | Professional + Clean hierarchy |
| Key effects | Subtle hover 200ms + Smooth transitions + Clean |
| Anti-patterns | Excessive decoration |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_trust_needed": "add-testimonials"}
```

### 139. Gift & Wishlist

| Field | Value |
|---|---|
| Recommended pattern | Minimal & Direct + Conversion |
| Style priority | Vibrant & Block-based + Soft UI Evolution |
| Color mood | Celebration warm pink/gold/red + category colors + surprise accent |
| Typography mood | Energetic + Bold + Large |
| Key effects | Large section gaps 48px+ + Color shift hover + Scroll-snap |
| Anti-patterns | Muted colors + Low energy |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_conversion_focused": "add-urgency-colors"}
```

### 140. Running & Cycling GPS

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich Showcase + Social Proof |
| Style priority | Dark Mode (OLED) + Vibrant & Block-based |
| Color mood | Energetic orange + map accent + pace zones (green/yellow/red) |
| Typography mood | High contrast + Light on dark |
| Key effects | Subtle glow + Neon accents + High contrast |
| Anti-patterns | Pure white backgrounds + Muted colors + Low energy |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_light_mode_needed": "provide-theme-toggle", "if_trust_needed": "add-testimonials"}
```

### 141. Yoga & Stretching Guide

| Field | Value |
|---|---|
| Recommended pattern | Storytelling-Driven + Social Proof |
| Style priority | Organic Biophilic + Soft UI Evolution |
| Color mood | Earth calming sage/terracotta/cream + breathing gradient + warm accent |
| Typography mood | Warm + Humanist + Natural |
| Key effects | Rounded 16-24px + Natural shadows + Flowing SVG |
| Anti-patterns | Inconsistent styling + Poor contrast ratios |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_trust_needed": "add-testimonials"}
```

### 142. Sleep Tracker

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich Showcase + Social Proof |
| Style priority | Dark Mode (OLED) + Neumorphism |
| Color mood | Deep midnight blue + stars/moon accent + sleep quality gradient (poor red to great green) |
| Typography mood | High contrast + Light on dark |
| Key effects | Dual shadows (light+dark) + Soft press 150ms |
| Anti-patterns | Pure white backgrounds |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_light_mode_needed": "provide-theme-toggle", "if_trust_needed": "add-testimonials"}
```

### 143. Calorie & Nutrition Counter

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich Showcase + Social Proof |
| Style priority | Flat Design + Vibrant & Block-based |
| Color mood | Healthy green + macro colors (protein blue, carb orange, fat yellow) + progress circle |
| Typography mood | Bold + Clean + Sans-serif |
| Key effects | Color shift hover + Fast 150ms transitions + No shadows |
| Anti-patterns | Complex shadows + 3D effects + Muted colors + Low energy |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_trust_needed": "add-testimonials"}
```

### 144. Period & Cycle Tracker

| Field | Value |
|---|---|
| Recommended pattern | Social Proof-Focused + Trust |
| Style priority | Soft UI Evolution + Aurora UI |
| Color mood | Rose/blush + lavender + fertility green + soft calendar tones |
| Typography mood | Elegant + Gradient-friendly |
| Key effects | Flowing gradients 8-12s + Color morphing |
| Anti-patterns | Inconsistent styling + Poor contrast ratios |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_trust_needed": "add-testimonials"}
```

### 145. Medication & Pill Reminder

| Field | Value |
|---|---|
| Recommended pattern | Trust & Authority + Feature-Rich |
| Style priority | Accessible & Ethical + Flat Design |
| Color mood | Medical trust blue + missed alert red + taken green + clean white |
| Typography mood | Bold + Clean + Sans-serif |
| Key effects | Color shift hover + Fast 150ms transitions + No shadows |
| Anti-patterns | Complex shadows + 3D effects + Color-only indicators |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_ux_focused": "prioritize-clarity", "if_mobile": "optimize-touch-targets"}
```

### 146. Water & Hydration Reminder

| Field | Value |
|---|---|
| Recommended pattern | Minimal & Direct + Demo |
| Style priority | Claymorphism + Vibrant & Block-based |
| Color mood | Refreshing blue + water wave animation + goal progress accent |
| Typography mood | Playful + Rounded + Friendly |
| Key effects | Multi-layer shadows + Spring bounce + Soft press 200ms |
| Anti-patterns | Muted colors + Low energy |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_ux_focused": "prioritize-clarity", "if_mobile": "optimize-touch-targets"}
```

### 147. Fasting & Intermittent Timer

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich Showcase + Social Proof |
| Style priority | Minimalism + Dark Mode (OLED) |
| Color mood | Fasting deep blue/purple + eating window green + timeline neutral |
| Typography mood | Professional + Clean hierarchy |
| Key effects | Subtle glow + Neon accents + High contrast |
| Anti-patterns | Excessive decoration + Pure white backgrounds |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_light_mode_needed": "provide-theme-toggle", "if_trust_needed": "add-testimonials"}
```

### 148. Anonymous Community / Confession

| Field | Value |
|---|---|
| Recommended pattern | Social Proof-Focused + Feature-Rich |
| Style priority | Dark Mode (OLED) + Minimalism |
| Color mood | Dark protective + subtle gradient + upvote green + empathy warm accent |
| Typography mood | Professional + Clean hierarchy |
| Key effects | Subtle glow + Neon accents + High contrast |
| Anti-patterns | Excessive decoration + Pure white backgrounds |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_light_mode_needed": "provide-theme-toggle", "if_trust_needed": "add-testimonials"}
```

### 149. Local Events & Discovery

| Field | Value |
|---|---|
| Recommended pattern | Hero-Centric Design + Feature-Rich |
| Style priority | Vibrant & Block-based + Motion-Driven |
| Color mood | City vibrant + event category colors + map accent + date highlight |
| Typography mood | Energetic + Bold + Large |
| Key effects | Scroll animations + Parallax + Page transitions |
| Anti-patterns | Muted colors + Low energy |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_ux_focused": "prioritize-clarity", "if_mobile": "optimize-touch-targets"}
```

### 150. Study Together / Virtual Coworking

| Field | Value |
|---|---|
| Recommended pattern | Social Proof-Focused + Feature-Rich |
| Style priority | Minimalism + Soft UI Evolution |
| Color mood | Calm focus blue + session progress indicator + ambient warm neutrals |
| Typography mood | Professional + Clean hierarchy |
| Key effects | Subtle hover 200ms + Smooth transitions + Clean |
| Anti-patterns | Excessive decoration |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_trust_needed": "add-testimonials"}
```

### 151. Coding Challenge & Practice

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich Showcase + Social Proof |
| Style priority | Dark Mode (OLED) + Cyberpunk UI |
| Color mood | Code editor dark + success green + difficulty gradient (easy green / medium amber / hard red) |
| Typography mood | High contrast + Light on dark |
| Key effects | Subtle glow + Neon accents + High contrast |
| Anti-patterns | Pure white backgrounds |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_light_mode_needed": "provide-theme-toggle", "if_trust_needed": "add-testimonials"}
```

### 152. Kids Learning (ABC & Math)

| Field | Value |
|---|---|
| Recommended pattern | Social Proof-Focused + Trust |
| Style priority | Claymorphism + Vibrant & Block-based |
| Color mood | Bright primary + child-safe pastels + reward gold + interactive accent |
| Typography mood | Playful + Rounded + Friendly |
| Key effects | Multi-layer shadows + Spring bounce + Soft press 200ms |
| Anti-patterns | Muted colors + Low energy |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_trust_needed": "add-testimonials"}
```

### 153. Music Instrument Learning

| Field | Value |
|---|---|
| Recommended pattern | Interactive Product Demo + Social Proof |
| Style priority | Vibrant & Block-based + Motion-Driven |
| Color mood | Musical warm deep red/brown + note color system + skill progress bar |
| Typography mood | Energetic + Bold + Large |
| Key effects | Scroll animations + Parallax + Page transitions |
| Anti-patterns | Muted colors + Low energy |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_trust_needed": "add-testimonials"}
```

### 154. Parking Finder

| Field | Value |
|---|---|
| Recommended pattern | Conversion-Optimized + Feature-Rich |
| Style priority | Minimalism + Glassmorphism |
| Color mood | Trust blue + available green + occupied red + map neutral |
| Typography mood | Professional + Clean hierarchy |
| Key effects | Backdrop blur (10-20px) + Translucent overlays |
| Anti-patterns | Excessive decoration |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_low_performance": "fallback-to-flat", "if_conversion_focused": "add-urgency-colors"}
```

### 155. Public Transit Guide

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich Showcase + Interactive Demo |
| Style priority | Flat Design + Accessible & Ethical |
| Color mood | Transit brand line colors + real-time indicator green/red + map neutral |
| Typography mood | Bold + Clean + Sans-serif |
| Key effects | Color shift hover + Fast 150ms transitions + No shadows |
| Anti-patterns | Complex shadows + 3D effects + Color-only indicators |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_ux_focused": "prioritize-clarity", "if_mobile": "optimize-touch-targets"}
```

### 156. Road Trip Planner

| Field | Value |
|---|---|
| Recommended pattern | Storytelling-Driven + Hero-Centric |
| Style priority | Aurora UI + Organic Biophilic |
| Color mood | Adventure warm sunset orange + map teal + stop markers + road neutral |
| Typography mood | Elegant + Gradient-friendly |
| Key effects | Flowing gradients 8-12s + Color morphing |
| Anti-patterns | Inconsistent styling + Poor contrast ratios |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_ux_focused": "prioritize-clarity", "if_mobile": "optimize-touch-targets"}
```

### 157. VPN & Privacy Tool

| Field | Value |
|---|---|
| Recommended pattern | Trust & Authority + Conversion-Optimized |
| Style priority | Minimalism + Dark Mode (OLED) |
| Color mood | Dark shield blue + connected green + disconnected red + trust accent |
| Typography mood | Professional + Clean hierarchy |
| Key effects | Subtle glow + Neon accents + High contrast |
| Anti-patterns | Excessive decoration + Pure white backgrounds |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_light_mode_needed": "provide-theme-toggle", "if_conversion_focused": "add-urgency-colors"}
```

### 158. Emergency SOS & Safety

| Field | Value |
|---|---|
| Recommended pattern | Trust & Authority + Social Proof |
| Style priority | Accessible & Ethical + Flat Design |
| Color mood | Alert red + safety blue + location green + high contrast critical |
| Typography mood | Bold + Clean + Sans-serif |
| Key effects | Color shift hover + Fast 150ms transitions + No shadows |
| Anti-patterns | Complex shadows + 3D effects + Color-only indicators |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_trust_needed": "add-testimonials"}
```

### 159. Wallpaper & Theme App

| Field | Value |
|---|---|
| Recommended pattern | Feature-Rich Showcase + Social Proof |
| Style priority | Vibrant & Block-based + Aurora UI |
| Color mood | Content-driven + trending aesthetic palettes + download accent |
| Typography mood | Energetic + Bold + Large |
| Key effects | Large section gaps 48px+ + Color shift hover + Scroll-snap |
| Anti-patterns | Muted colors + Low energy |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_trust_needed": "add-testimonials"}
```

### 160. White Noise & Ambient Sound

| Field | Value |
|---|---|
| Recommended pattern | Minimal & Direct + Social Proof |
| Style priority | Minimalism + Dark Mode (OLED) |
| Color mood | Calming dark + ambient texture visual + subtle sound wave + sleep blue |
| Typography mood | Professional + Clean hierarchy |
| Key effects | Subtle glow + Neon accents + High contrast |
| Anti-patterns | Excessive decoration + Pure white backgrounds |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_light_mode_needed": "provide-theme-toggle", "if_trust_needed": "add-testimonials"}
```

### 161. Home Decoration & Interior Design

| Field | Value |
|---|---|
| Recommended pattern | Storytelling-Driven + Feature-Rich |
| Style priority | Minimalism + 3D Product Preview |
| Color mood | Neutral interior palette + material texture accent + AR blue |
| Typography mood | Professional + Clean hierarchy |
| Key effects | Subtle hover 200ms + Smooth transitions + Clean |
| Anti-patterns | Excessive decoration |
| Severity | HIGH |

Decision rules (JSON):

```json
{"if_ux_focused": "prioritize-clarity", "if_mobile": "optimize-touch-targets"}
```

Source: ui-ux-pro-max ui-reasoning.csv (MIT)
