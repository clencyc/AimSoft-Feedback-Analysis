import streamlit as st

from routing import build_navigation
from services import is_authenticated, logout_user

st.set_page_config(
	page_title="AimSoft Feedback Analysis",
	page_icon="📊",
	layout="wide",
	initial_sidebar_state="expanded",
)

if "access_token" not in st.session_state:
	st.session_state.access_token = ""
if "refresh_token" not in st.session_state:
	st.session_state.refresh_token = ""
if "current_user" not in st.session_state:
	st.session_state.current_user = {}
if "view" not in st.session_state:
	st.session_state.view = "home"  # "home" -> "login" -> authenticated dashboard


def render_sidebar():
	if not is_authenticated():
		return  # no sidebar chrome on the public home/login screens
	with st.sidebar:
		st.title("AimSoft")
		st.divider()
		user = st.session_state.current_user
		st.success(f"Signed in as {user.get('username', 'user')}")
		st.caption(user.get("role_name") or "No role assigned")
		st.divider()
		if st.button("Log out", use_container_width=True):
			response = logout_user()
			st.session_state.access_token = ""
			st.session_state.refresh_token = ""
			st.session_state.current_user = {}
			st.session_state.view = "home"
			if response is not None and response.ok:
				st.success("Logged out")
			else:
				st.info("Local session cleared")
			st.rerun()


def main():
	render_sidebar()
	nav = build_navigation()
	nav.run()


if __name__ == "__main__":
	main()