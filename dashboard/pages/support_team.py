import streamlit as st

from services import require_role

require_role("Support Team")

st.title("🎧 Support Dashboard")
st.caption(f"Welcome, {st.session_state.current_user.get('username', '')}")

st.info(
	"Wire up Support-facing feedback endpoints here — e.g. open tickets, "
	"negative-sentiment queue, response time tracking."
)