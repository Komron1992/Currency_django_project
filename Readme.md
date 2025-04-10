# 💱 Django Currency Rates Parser

A Django web application that collects and displays real-time currency exchange rates by parsing data from multiple bank websites.

## 🌍 Features

- 📊 Live currency rates from several banks (via web scraping)
- 🕵️‍♂️ Custom parser for each bank's website
- 🔄 Auto-update currency data using scheduled tasks (optional: Celery + Redis)
- 🧭 Clean UI to view and compare rates
- 🛠️ Admin panel to manage data manually
- 🔐 Secure config via `.env` file

## 🧰 Tech Stack

- **Backend**: Python, Django
- **Parsing**: `requests`, `BeautifulSoup4`
- **Scheduling (optional)**: Celery, Redis
- **Database**: SQLite3 or PostgreSQL
- **Environment**: `python-dotenv`

## 🚀 Getting Started

1. **Clone the repo**:

```bash
git clone https://github.com/Komron1992/Currency_django_project
cd Currency_django_project

2. Install dependencies:
pip install -r requirements.txt

3.Setup database:
python manage.py migrate

4.Run the server:
python manage.py runserver

👤 Author
Your Name
📧 kemeron2016@gmail.com
🌐 Telegram @kemeron1992
