# AimSoft Feedback Analysis

A customer feedback analysis platform for East African insurers. Collects customer feedback through shareable public forms, scores it for sentiment, and surfaces insights through role-based dashboards.

## Features

- Public, shareable feedback links (no login required for customers)
- Dynamic feedback forms — admins can configure which questions to ask
- Sentiment analysis using VADER and a fine-tuned BERT model
- Role-based dashboards for System Admins and Support Team
- JWT authentication with group-based permissions

## Tech Stack

- **Backend:** Django + Django REST Framework
- **Dashboard:** Streamlit
- **Database:** PostgreSQL
- **Sentiment Analysis:** VADER, fine-tuned BERT (Hugging Face Transformers)
- **App Server:** Gunicorn
- **Containerization:** Docker + Docker Compose

## Getting Started

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Admin / Support Dashboard

```bash
cd dashboard
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

### Public Customer Feedback Form

```bash
cd CustomerFeedbackForm
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

### Environment Variables

Create a `.env` file (see `.env.example`) with:

```
DATABASE_URL=your_postgres_connection_string
SECRET_KEY=your_django_secret_key
BACKEND_API_URL=http://localhost:8000
```

## Sentiment Analysis

- `finetune.ipynb` — fine-tunes a BERT model on labeled feedback data
- `sentiment_model/` — the saved, fine-tuned model and tokenizer, loaded at inference time
- `model.py` — sentiment inference logic used by the backend

## Project Structure

```
AimSoft-Feedback-Analysis/
├── backend/              # Django REST API
├── dashboard/             # Streamlit admin/support dashboards
├── CustomerFeedbackForm/  # Public-facing Streamlit feedback form
├── sentiment_model/       # Saved fine-tuned BERT model + tokenizer
├── finetune.ipynb         # BERT fine-tuning notebook
├── model.py               # Sentiment inference logic
└── docker-compose.yml
```

## Author

Built by Christine, JKUAT — BSc Mathematics and Computer Science.