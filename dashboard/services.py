import os
from typing import Any

import requests
import streamlit as st


def backend_base_url() -> str:
	return os.getenv("BACKEND_API_URL", "http://localhost:8000/").rstrip("/")


def api_url(path: str) -> str:
	return f"{backend_base_url()}/{path.lstrip('/') }"


def auth_headers() -> dict[str, str]:
	"""Return Authorization headers using the stored access_token (Bearer)."""
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


# Feedback-link specific helpers
def create_feedback_link(org_id: int, payload: dict[str, Any]):
	"""Admin: create a new feedback link for organization (requires auth)."""
	return post_json(f"api/admin/organizations/{org_id}/feedback-links/", payload, use_auth=True)


def list_feedback_links(org_id: int):
	return get_json(f"api/admin/organizations/{org_id}/feedback-links/", use_auth=True)


def revoke_feedback_link(link_id: int):
	return post_json(f"api/admin/feedback-links/{link_id}/revoke/", {}, use_auth=True)


def list_organizations():
	return get_json("api/admin/organizations/", use_auth=True)


def get_summary(org_id: int):
	"""Admin: fetch aggregated summary for the given organization."""
	return get_json(f"api/admin/organizations/{org_id}/summary/", use_auth=True)


# Form builder helpers (admin/dashboard)
def list_form_questions(org_id: int):
	return get_json(f"api/admin/organizations/{org_id}/form-questions/", use_auth=True)


def create_form_question(org_id: int, payload: dict[str, Any]):
	return post_json(f"api/admin/organizations/{org_id}/form-questions/", payload, use_auth=True)


def delete_form_question(org_id: int, question_id: int):
	# org_id present for UX parity but endpoint ignores it; keep for future checks
	return requests.delete(api_url(f"/api/admin/form-questions/{question_id}/"), headers={**auth_headers(), "Content-Type": "application/json"}, timeout=15)


def reorder_form_questions(org_id: int, order_list: list[int]):
	return post_json(f"api/admin/organizations/{org_id}/form-questions/reorder/", {"order": order_list}, use_auth=True)


def update_form_question(question_id: int, payload: dict[str, Any]):
	"""Update a single form question (admin).
	Uses PUT on /api/admin/form-questions/{id}/
	"""
	h = {"Content-Type": "application/json"}
	h.update(auth_headers())
	return requests.put(api_url(f"/api/admin/form-questions/{question_id}/"), json=payload, headers=h, timeout=15)


# Public endpoints helpers
def public_validate_token(token: str):
	return get_json(f"api/public/feedback/{token}/", use_auth=False)


def public_submit_feedback(token: str, payload: dict[str, Any]):
	return post_json(f"api/public/feedback/{token}/submit/", payload, use_auth=False)


def login_user(username: str, password: str):
	return post_json("api/users/login/", {"username": username, "password": password})


def create_user(payload: dict[str, Any]):
	return post_json("api/users/create/", payload, use_auth=True)

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
