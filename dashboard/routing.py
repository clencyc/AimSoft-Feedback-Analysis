import streamlit as st

from services import current_role, is_authenticated

# Role-specific dashboards. Only ever ONE of these is placed into
# st.navigation() at a time, based on the signed-in user's role_name.
# Keys are matched case/whitespace-insensitively - see _normalize().
ROLE_PAGES = {
	"sysadmin": st.Page(
		"pages/management.py", title="Management Dashboard", icon="📈"
	),
	"Secondary Stakeholder": st.Page(
		"pages/product_development.py", title="Product Dev Dashboard", icon="🛠️"
	),
	"Secondary Stakeholder": st.Page(
		"pages/support_team.py", title="Support Dashboard", icon="🎧"
	),
}

# Pre-normalize once, at import time, so lookups below are cheap.
_NORMALIZED_ROLE_PAGES = {name.strip().lower(): page for name, page in ROLE_PAGES.items()}

HOME_PAGE = st.Page("pages/home.py", title="Home", url_path="home")
LOGIN_PAGE = st.Page("pages/login.py", title="Sign In", url_path="login")


def _normalize(value) -> str:
	return (value or "").strip().lower()


def _render_no_dashboard():
	"""Fallback page rendered as a plain function (never a missing file path),
	so this can never itself be the source of a None-page crash."""
	role = current_role()
	st.error(
		f"No dashboard is configured for role '{role or '(empty)'}'. "
		f"Expected one of: {', '.join(ROLE_PAGES)}. "
		"Check the user's group/role_name in Django admin, and that it "
		"matches one of the names above exactly."
	)


NO_DASHBOARD_PAGE = st.Page(_render_no_dashboard, title="No Dashboard", url_path="no-dashboard")


def build_navigation():
	"""Builds st.navigation with exactly one reachable page for the
	current auth state / flow step:

	  not logged in, view == "home"  -> Home (landing + Get Started button)
	  not logged in, view == "login" -> Login form
	  logged in, role recognized     -> that user's role dashboard
	  logged in, role NOT recognized -> a clear error page (never a bare None)

	Calling st.navigation() explicitly (even for the home/login steps)
	is what stops Streamlit from auto-listing every file in pages/ in
	the sidebar - without it, unauthenticated visitors would see links
	to every dashboard regardless of role.
	"""
	if is_authenticated():
		page = _NORMALIZED_ROLE_PAGES.get(_normalize(current_role()))
		selected = page if page is not None else NO_DASHBOARD_PAGE
		return st.navigation([selected], position="hidden")

	if st.session_state.get("view") == "login":
		return st.navigation([LOGIN_PAGE], position="hidden")

	return st.navigation([HOME_PAGE], position="hidden")