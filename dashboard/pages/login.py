import streamlit as st

from services import login_user


def render_login():
	st.markdown(
		"""
		<style>
			.card {
				padding: 1rem 1.1rem;
				border-radius: 14px;
				border: 1px solid rgba(148, 163, 184, 0.25);
				background: rgba(255,255,255,0.65);
				backdrop-filter: blur(8px);
			}
		</style>
		""",
		unsafe_allow_html=True,
	)

	st.title("Sign in")

	left, _ = st.columns([1, 1.4])
	with left:
		st.markdown('<div class="card">', unsafe_allow_html=True)
		with st.form("login_form"):
			username = st.text_input("Username")
			password = st.text_input("Password", type="password")
			submitted = st.form_submit_button("Log in", use_container_width=True)

		if submitted:
			if not username or not password:
				st.warning("Enter both username and password.")
			else:
				with st.spinner("Signing in..."):
					try:
						response = login_user(username, password)
					except Exception:
						response = None

				if response is None:
					st.error("Couldn't reach the backend API. Is it running?")
				elif response.ok:
					data = response.json()
					st.session_state.access_token = data["access"]
					st.session_state.refresh_token = data["refresh"]
					st.session_state.current_user = data["user"]
					st.rerun()
				else:
					try:
						detail = response.json().get("detail", "Invalid credentials.")
					except ValueError:
						detail = "Invalid credentials."
					st.error(detail)
		st.markdown("</div>", unsafe_allow_html=True)

		if st.button("← Back to home"):
			st.session_state.view = "home"
			st.rerun()

		st.caption(
			"No dashboard assigned yet? Contact an admin to have your account "
			"added to a group."
		)


render_login()