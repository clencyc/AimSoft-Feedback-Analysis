import random
from datetime import date, timedelta

import pandas as pd
import streamlit as st

from services import get_json, require_role, list_organizations, create_feedback_link, list_feedback_links, revoke_feedback_link

require_role("sysadmin")

st.title("Management Dashboard")
st.caption(f"Welcome, {st.session_state.current_user.get('username', '')}")


def load_summary():
	"""Pulls from the real summary endpoint if it exists yet; otherwise
	returns representative sample data so the dashboard is presentable
	before that endpoint is wired up."""
	try:
		resp = get_json("feedback/summary/")
		if resp.ok:
			return resp.json(), True
	except Exception:
		pass

	random.seed(7)  # stable sample data across reruns
	weeks = [date.today() - timedelta(weeks=i) for i in range(7, -1, -1)]
	trend = [round(random.uniform(3.4, 4.6), 2) for _ in weeks]
	sample = {
		"avg_satisfaction": round(sum(trend) / len(trend), 2),
		"nps": 42,
		"total_responses": 318,
		"trend": {"week": [w.strftime("%b %d") for w in weeks], "satisfaction": trend},
		"sentiment": {"Positive": 61, "Neutral": 24, "Negative": 15},
	}
	return sample, False


data, is_live = load_summary()

# if not is_live:
# 	st.caption("Sample data shown — connect `feedback/summary/` for live figures.")

col1, col2, col3 = st.columns(3)
col1.metric("Avg. Satisfaction", f"{data['avg_satisfaction']} / 5")
col2.metric("NPS Score", data["nps"])
col3.metric("Total Responses", data["total_responses"])

st.write("")
left, right = st.columns([1.4, 1])

with left:
	st.subheader("Satisfaction trend (last 8 weeks)")
	trend_df = pd.DataFrame(data["trend"]).set_index("week")
	st.line_chart(trend_df)

with right:
	st.subheader("Sentiment breakdown")
	sentiment_df = pd.DataFrame(
		{"count": data["sentiment"].values()}, index=data["sentiment"].keys()
	)
	st.bar_chart(sentiment_df)


# --- Feedback links admin UI ---
st.divider()
st.header("Feedback Links (Super Admin)")

# Load organizations
orgs_resp = list_organizations()
org_options = []
if orgs_resp is not None and orgs_resp.ok:
	orgs = orgs_resp.json()
	org_options = {o['name']: o['id'] for o in orgs}
else:
	st.warning("Could not load organizations — ensure backend is reachable and you are authorized.")

selected_org_id = None
if org_options:
	selected_name = st.selectbox("Select organization", ["Choose..."] + list(org_options.keys()))
	if selected_name != "Choose...":
		selected_org_id = org_options[selected_name]
else:
	st.info("No organizations available to manage.")

with st.expander("Create new shareable feedback link"):
	label = st.text_input("Label (optional)")
	expires_at = st.date_input("Expiry date (optional)", value=None)
	max_sub = st.number_input("Max submissions (optional)", min_value=0, value=0)
	if st.button("Create link"):
		if not selected_org_id:
			st.error("Please select an organization first")
		else:
			payload = {}
			if label:
				payload['label'] = label
			if expires_at:
				# store ISO date; backend will accept and parse if provided
				payload['expires_at'] = expires_at.isoformat()
			if max_sub and max_sub > 0:
				payload['max_submissions'] = int(max_sub)
			resp = create_feedback_link(selected_org_id, payload)
			if resp is not None and resp.ok:
				data = resp.json()
				# show full shareable URL
				base = ''
				try:
					from services import backend_base_url
					base = backend_base_url()
				except Exception:
					base = ''
				full_url = f"{base}/api/public/feedback/{data['token']}/"
				st.success("Link created")
				st.code(full_url)
			else:
				st.error("Failed to create link")

st.write("")
if selected_org_id:
	st.subheader("Existing links for selected organization")
	links_resp = list_feedback_links(selected_org_id)
	if links_resp is not None and links_resp.ok:
		links = links_resp.json()
		for l in links:
			cols = st.columns([2, 1, 1, 1, 1])
			with cols[0]:
				st.markdown(f"**{l.get('label') or '(no label)'}**")
				base = ''
				try:
					from services import backend_base_url
					base = backend_base_url()
				except Exception:
					base = ''
				full_url = f"http://localhost:8502/?token={l.get('token')}"
				st.code(full_url)
			with cols[1]:
				st.write("Active" if l.get('is_active') else "Revoked")
			with cols[2]:
				count = l.get('submission_count') or 0
				maxs = l.get('max_submissions') or '∞'
				st.write(f"{count} / {maxs}")
			with cols[3]:
				st.write(l.get('expires_at') or "—")
			with cols[4]:
				if st.button("Revoke", key=f"revoke_{l.get('id')}"):
					resp = revoke_feedback_link(l.get('id'))
					if resp is not None and resp.ok:
						st.success("Revoked")
						st.experimental_rerun()
		else:
			st.info("No links for this organization")
else:
	st.info("Select an organization to manage its shareable feedback links")
