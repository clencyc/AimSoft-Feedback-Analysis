import os
from typing import Any

import requests
import streamlit as st


def backend_base_url() -> str:
	return os.getenv("BACKEND_API_URL", "http://localhost:8000/").rstrip("/")


def api_url(path: str) -> str:
	return f"{backend_base_url()}/{path.lstrip('/')}"


def auth_headers() -> dict[str, str]:
	token = st.session_state.get("access_token")
	if not token:
		return {}
	return {"Authorization": f"Bearer {token}"}


def post_json(path: str, payload: dict[str, Any], use_auth: bool = False):
	headers = {"Content-Type": "application/json"}
	if use_auth:
		headers.update(auth_headers())
	return requests.post(api_url(path), json=payload, headers=headers, timeout=15)


def get_json(path: str, params: dict[str, Any] | None = None, use_auth: bool = True):
	headers = {}
	if use_auth:
		headers.update(auth_headers())
	return requests.get(api_url(path), params=params, headers=headers, timeout=15)


def login_user(username: str, password: str):
	return post_json("users/login/", {"username": username, "password": password})


def create_user(payload: dict[str, Any]):
	return post_json("users/create/", payload, use_auth=True)


def logout_user():
	refresh = st.session_state.get("refresh_token")
	if not refresh:
		return None
	return post_json("users/logout/", {"refresh": refresh}, use_auth=True)


def is_authenticated() -> bool:
	return bool(st.session_state.get("access_token")) and bool(
		st.session_state.get("current_user")
	)


def current_role() -> str:
	return (st.session_state.get("current_user") or {}).get("role_name", "")


def require_role(*allowed_roles: str):
	"""Guard for the top of each dashboard page. Stops rendering if unauthorized.

	This is a defensive check in addition to app.py only listing the pages a
	user is allowed to reach — it protects against someone landing on a page
	directly (e.g. a stale browser tab) after their session/role changes.
	"""
	if not is_authenticated():
		st.error("Please log in to view this page.")
		st.stop()
	if current_role() not in allowed_roles:
		st.error("You don't have access to this dashboard.")
		st.stop()