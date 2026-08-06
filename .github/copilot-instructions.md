# Copilot instructions for AimSoft-Feedback-Analysis

## Project shape
- This repo is a Django + DRF backend in [backend/](../backend), plus a Streamlit dashboard container in [dashboard/](../dashboard).
- The backend is the source of truth for application logic; the dashboard is meant to consume the backend API through BACKEND_API_URL.
- Database is PostgreSQL (docker-compose uses postgres:16-alpine); Redis is provisioned in compose but is not yet wired into Django code.

## Backend architecture
- Django project settings live in [backend/backend/settings.py](../backend/backend/settings.py); project URLs live in [backend/backend/urls.py](../backend/backend/urls.py).
- The only installed local app right now is users; feedback exists as an app folder but is not yet registered in INSTALLED_APPS.
- User auth is centered on a custom model in [backend/users/models.py](../backend/users/models.py) that extends AbstractUser.
- The admin registration is intentionally simple: [backend/users/admin.py](../backend/users/admin.py) registers User with Django’s default UserAdmin.

## Routing and API boundaries
- Top-level routing currently mounts admin and /api/users/; add new API areas under separate app URLConfs instead of expanding the root project file.
- Be careful with [backend/users/urls.py](../backend/users/urls.py): it currently includes users.urls recursively, so verify routing before building on it.
- Keep app boundaries clear: users should own authentication/profile concerns, while feedback should own feedback domain models and endpoints.

## Auth and DRF conventions
- Django REST Framework is configured globally with JWT authentication and IsAuthenticated as the default permission in settings.
- Existing user views in [backend/users/views.py](../backend/users/views.py) mix APIView-style token auth ideas with @api_view helpers; prefer following the existing file’s lightweight function-view style unless you are refactoring auth end-to-end.
- If you touch auth, update the custom user model path and AUTH_USER_MODEL together; settings currently reference accounts.User while the model lives in users.User.

## Development workflow
- For local backend development, the compose flow runs migrations and then starts the Django dev server on 0.0.0.0:8000.
- The backend container uses Gunicorn for production in [backend/Dockerfile](../backend/Dockerfile); keep WSGI compatibility in mind for new code.
- The dashboard container expects an app.py entrypoint in [dashboard/Dockerfile](../dashboard/Dockerfile); that file is currently absent, so verify before adding dashboard features.

## Conventions and current gaps
- Migrations are currently minimal/empty in both apps; create migrations explicitly when adding models.
- Test modules in [backend/users/tests.py](../backend/users/tests.py) and [backend/feedback/tests.py](../backend/feedback/tests.py) are stubs, so new behavior should be covered with app-local tests when you implement it.
- Keep environment-driven configuration aligned with docker-compose defaults: POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, and BACKEND_API_URL.

## What to inspect first when changing code
- Auth/user work: [backend/backend/settings.py](../backend/backend/settings.py), [backend/users/models.py](../backend/users/models.py), [backend/users/views.py](../backend/users/views.py), [backend/users/urls.py](../backend/users/urls.py)
- API expansion: [backend/backend/urls.py](../backend/backend/urls.py), [backend/feedback/models.py](../backend/feedback/models.py), [backend/feedback/views.py](../backend/feedback/views.py)
- Runtime/deploy behavior: [docker-compose.yml](../docker-compose.yml), [backend/Dockerfile](../backend/Dockerfile), [dashboard/Dockerfile](../dashboard/Dockerfile)
