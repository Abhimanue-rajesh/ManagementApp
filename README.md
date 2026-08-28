# ManagementApp

[![Django CI](https://github.com/Abhimanue-rajesh/deepsea_tasks/actions/workflows/django.yml/badge.svg)](https://github.com/Abhimanue-rajesh/deepsea_tasks/actions/workflows/django.yml)
![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-6-092E20?logo=django&logoColor=white)

A unified Django admin for day-to-day operations — projects, tickets, web assets, credentials, and subscriptions in one dashboard.

## What's inside

- **Projects & Tasks** — projects, departments, daily tasks, and activity tracking
- **Support Tickets** — routing, status, urgency, and history
- **Web Management** — domains, pages, forms, and DNS zones
- **Credentials** — encrypted passwords, notes, and PEM files
- **Subscriptions** — platforms, renewals, and payment tracking
- **Quick Copy** — reusable snippets for common responses
- **Dashboard** — charts, renewals, and task summaries at a glance

Powered by [Django Unfold](https://github.com/unfoldadmin/django-unfold) and [django-easy-audit](https://github.com/soynatan/django-easy-audit).

## Get started

```bash
python -m venv venv && venv\Scripts\activate   # Windows
pip install -r requirements.txt
cp .env.example .env
```

Set `SECRET_KEY` and `FIELD_ENCRYPTION_KEY` in `.env`. Generate a Fernet key:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Then:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

→ [http://localhost:8000/admin/](http://localhost:8000/admin/)

## Docker

```bash
docker compose up --build
```

See [README.Docker.md](README.Docker.md) for deployment details.

## Development

```bash
pre-commit install && pre-commit run --all-files
python manage.py test
```

| Environment | Settings module |
| --- | --- |
| Local | `core.settings.development` (default) |
| Production | `core.settings.production` |

## Structure

```
core/           settings · urls · wsgi
tasks/          projects · tasks · daily tasks
tickets/        support tickets
web_management/ domains · pages · forms · dns
credentials/    encrypted storage
subscriptions/  renewal tracking
quickcopy/      text snippets
dashboard/      admin widgets
accounts/       user customizations
```

---

Built for internal use at **The Deep Seafood**.
