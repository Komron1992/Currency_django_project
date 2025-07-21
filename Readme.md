# 💱 Django Currency Rates Platform

A full-stack Django & Vue application that fetches, stores, and displays real-time currency exchange rates from various Tajikistan banks using custom parsers.

---

## 🌍 Features

- 📊 Live currency rates from banks (web scraping)
- 🕵️‍♂️ Individual parser for each bank (Selenium or BeautifulSoup)
- 🔄 Periodic updates with Celery & Redis
- 📈 Admin dashboard for manual data control
- 🧭 Clean and responsive frontend with Vue 3
- 🔐 Secure `.env`-based configuration

---

## 🧰 Tech Stack

| Layer     | Technology                          |
|-----------|--------------------------------------|
| Backend   | Python, Django, DRF, Celery, Redis   |
| Frontend  | Vue 3, Vite                          |
| Scraping  | Selenium, BeautifulSoup, Requests    |
| Database  | PostgreSQL (or SQLite for dev)       |
| DevOps    | Docker, Docker Compose, Nginx        |

---

## 📁 Project Structure

```bash
.
├── app/                  # Django app with bank scrapers and logic
├── frontend/             # Vue.js admin/public interfaces
├── myproject/            # Django settings and routing
├── nginx/                # Nginx configs for prod
├── static/, templates/   # Static files and templates
├── entrypoint.sh         # Backend Docker entrypoint
├── docker-compose.yml    # Full docker environment
├── requirements.txt      # Python dependencies
└── README.md             # Project description
```
🚀 Getting Started (Locally)
1. Clone the repo
```
git clone https://github.com/Komron1992/Currency_django_project
```
2. Create virtual environment & activate
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
3. Install dependencies
```
pip install -r requirements.txt
```
4. Setup database
```
python manage.py migrate
```
5. Run development server
```
python manage.py runserver
```
🐳 Run via Docker (recommended)
Make sure Docker & Docker Compose are installed.

1. Create .env file
```
DEBUG=1
SECRET_KEY=your-secret-key
POSTGRES_DB=db
POSTGRES_USER=user_name
POSTGRES_PASSWORD=pass
```
2. Build and start containers
```
docker-compose up --build
```
🛠 Development Tips
Use docker-compose.override.yml to mount local volumes and enable Vite dev mode
Use Celery Beat for periodic scraping from banks
Selenium version managed inside container using webdriver-manager

👤 Author
Komron Shukurov
📧 kemeron2016@gmail.com
🌐 Telegram: @kemeron1992