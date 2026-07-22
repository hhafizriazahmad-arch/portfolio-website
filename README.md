# Professional Portfolio Website

A lightweight, modern, and professional portfolio website showcasing backend engineering and automation pipelines. Built with a cyber-dark aesthetic, dynamic SQLite content loading, and real-time form submission tracking.

## Technology Stack

- **Backend:** Python, FastAPI (API design & static file serving)
- **Database:** SQLite with SQLAlchemy ORM
- **Frontend:** HTML5, Tailwind CSS (via CDN), Vanilla JavaScript, custom CSS animations

---

## Features

1. **Cyber-Dark Theme:** Modern tech colors, glowing hover micro-interactions, and glassmorphism styling.
2. **Interactive Background:** A moving constellation particle canvas written in native JavaScript.
3. **Dynamic Project Showcase:** Projects are automatically loaded from an SQLite database via a `/api/projects` endpoint.
4. **Active Contact Logging:** Forms submitted to `/api/contact` are validated on the backend and stored in the database.
5. **Auto-seeding Engine:** Automatically pre-populates the database on startup if no projects are present.

---

## Setup & Running Locally

Follow these instructions to run the application on your computer:

### 1. Clone or Open Directory
Navigate to the directory in your terminal:
```bash
cd portfolio
```

### 2. Create and Activate a Virtual Environment
Create a virtual environment:
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
Install all required packages:
```bash
pip install -r requirements.txt
```

### 4. Start the Application
Run the FastAPI development server with Uvicorn:
```bash
uvicorn main:app --reload
```

The application will start, seed the SQLite database (`portfolio.db`), and serve:
- **Frontend Portfolio:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger Documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Folder Structure

```
├── static/
│   ├── css/
│   │   └── style.css      # Custom animations, custom glow transitions, and scrollbar setup
│   ├── js/
│   │   └── main.js        # Interactive canvas drawing, contact submissions, API loader
│   └── index.html         # Hero, About, Skills, Projects, and Contact sections
├── .gitignore
├── database.py            # SQLite connection pool initialization
├── main.py                # FastAPI endpoints, seeding mechanics, and static file mount
├── models.py              # SQLAlchemy schemas for database
├── requirements.txt       # Necessary Python modules
├── schemas.py             # Pydantic schemas for request validation
└── README.md              # Instructions & overview
```

---

## API Endpoints

- **`GET /api/projects`**  
  Returns a JSON array of all projects.
- **`POST /api/contact`**  
  Submits contact form payload.  
  *Payload format:*
  ```json
  {
    "name": "John Doe",
    "email": "john@example.com",
    "subject": "Inquiry",
    "message": "Let's collaborate!"
  }
  ```
