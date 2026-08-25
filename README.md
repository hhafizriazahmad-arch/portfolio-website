# HR Autonomous – Enterprise AI Automation Platform & Portfolio

**HR Autonomous** is a premium, enterprise-grade AI Automation brand and portfolio showcasing intelligent automation systems, backend microservices, and AI-powered workflow architecture. Built with a modern dark SaaS aesthetic, Gray & Gold luxury design system, dynamic SQLite database seeding, and real-time lead capture pipelines.

---

## Brand Identity & Positioning

- **Brand Name:** HR Autonomous
- **Tagline:** Building Intelligent Automation Systems for Modern Businesses
- **Founder:** Hafiz Riaz (AI Automation Engineer • Backend Developer • Workflow Architect)
- **Primary Color Palette:** Primary Dark (`#111111`), Secondary Dark (`#1E1E1E`), Card Dark (`#2A2A2A`), Primary Gold (`#D4AF37`), Premium Gold Hover (`#F4C542`), Primary Text (`#F5F5F5`), Secondary Text (`#B0B0B0`)

---

## Technology Stack

- **Backend:** Python 3.11+, FastAPI (REST API design & static file serving), SQLAlchemy ORM, Uvicorn
- **AI Integration:** Google Gemini AI API with conversational memory & lead capture mechanics
- **Database:** SQLite with SQLAlchemy ORM (and automatic Vercel `/tmp/portfolio.db` support)
- **Frontend:** HTML5, Tailwind CSS, Vanilla JavaScript, HTML5 Canvas Network Grid

---

## Features

1. **Luxury Gray & Gold Aesthetic:** Sophisticated dark gray and gold design system, gold borders (`rgba(212,175,55,0.25)`), glassmorphism, and gold hover glows.
2. **Interactive Network Canvas:** Dynamic gold particle constellation network background written in native JavaScript.
3. **Dynamic Systems Showcase:** Projects are seeded automatically into SQLite and fetched via `/api/projects`.
4. **Active Contact & Chat Lead Capture:** Form submissions to `/api/contact` and AI chat leads are logged to SQLite and forwarded via Google Apps Script Webhooks.
5. **SEO & Social Optimization:** Pre-configured Open Graph, Twitter Card tags, and JSON-LD Structured Data for `Organization` / `HR Autonomous`.

---

## Setup & Running Locally

Follow these instructions to run HR Autonomous locally:

### 1. Navigate to Project Directory
```bash
cd portfolio
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Start the Application Server
```bash
python main.py
```
Or directly using Uvicorn:
```bash
uvicorn main:app --reload
```

The application will start, seed the SQLite database (`portfolio.db`), and serve:
- **HR Autonomous Frontend:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive OpenAPI Documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## File Structure

```
├── static/
│   ├── css/
│   │   └── style.css      # Enterprise CSS variables, glassmorphism, scrollbars, glowing utilities
│   ├── js/
│   │   └── main.js        # Canvas particle animation, project renderer, contact & chat controllers
│   └── index.html         # Hero, About, Capabilities, Projects showcase, Contact form, Chatbot UI
├── .gitignore
├── database.py            # SQLite connection pool & Vercel /tmp copy handler
├── main.py                # FastAPI endpoints, Gemini AI integration, database seeding, static file mount
├── models.py              # SQLAlchemy schemas for projects and contact messages
├── requirements.txt       # Dependencies
├── schemas.py             # Pydantic schemas for request & response validation
└── README.md              # Brand overview and documentation
```

---

## API Endpoints

- **`GET /api/projects`** — Returns JSON array of HR Autonomous systems & projects.
- **`POST /api/contact`** — Submits contact form payload.
- **`POST /api/chat`** — Routes chat messages to Gemini AI with conversational memory.
