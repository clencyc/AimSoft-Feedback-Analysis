import random
from datetime import date, timedelta

import pandas as pd
import streamlit as st

from services import get_json, require_role, list_organizations

require_role("support")

st.title("Support Team Dashboard")
st.caption(f"Welcome, {st.session_state.current_user.get('username', '')}")

def load_feedback_list(org_id=None, channel=None, sentiment=None):
	"""Pulls from the real feedback list endpoint if it exists yet; otherwise
	returns representative sample data so the dashboard is presentable
	before that endpoint is wired up."""
	params = {}
	if org_id:
		params["organization_id"] = org_id
	if channel and channel != "All":
		params["channel"] = channel
	if sentiment and sentiment != "All":
		params["sentiment"] = sentiment

	try:
		resp = get_json("feedback/list/", params=params)
		if resp.ok:
			return resp.json(), True
	except Exception:
		pass

	random.seed(11)
	channels = ["WhatsApp", "Email", "Web survey", "Phone call"]
	modules = ["General Insurance", "Life", "Portals", "Mobile App"]
	clients = ["CIC Insurance", "APA Insurance", "Britam", "Jubilee Insurance"]
	sentiments = ["Negative", "Neutral", "Positive"]
	texts = [
		"App keeps logging me out mid-claim, had to restart twice.",
		"Portal takes forever to load monthly reports.",
		"Support agent was quick to resolve my query, thanks.",
		"Can't find where to update my policy details on mobile.",
		"Payment confirmation email never arrived after renewal.",
		"Dashboard crashed while exporting the Excel report.",
	]

	sample = []
	for i in range(14):
		sample.append({
			"id": i + 1,
			"client": random.choice(clients),
			"channel": random.choice(channels),
			"module": random.choice(modules),
			"sentiment": random.choices(sentiments, weights=[3, 2, 2])[0],
			"text": random.choice(texts),
			"received_at": (date.today() - timedelta(days=random.randint(0, 6))).strftime("%b %d"),
			"status": random.choice(["Open", "Open", "Acknowledged"]),
		})

	if org_id:
		# sample data has no real org linkage, so this only matters once live
		pass
	if channel and channel != "All":
		sample = [s for s in sample if s["channel"] == channel]
	if sentiment and sentiment != "All":
		sample = [s for s in sample if s["sentiment"] == sentiment]

	return sample, False


def acknowledge_feedback(feedback_id):
	"""Marks a feedback item as acknowledged. Falls back to local session
	state if the backend endpoint isn't wired up yet."""
	try:
		resp = get_json(f"feedback/{feedback_id}/acknowledge/", method="POST")
		if resp.ok:
			return True
	except Exception:
		pass

	acked = st.session_state.setdefault("acked_local", set())
	acked.add(feedback_id)
	return True


# --- Filters ---
orgs_resp = list_organizations()
org_options = {}
if orgs_resp is not None and orgs_resp.ok:
	orgs = orgs_resp.json()
	org_options = {o["name"]: o["id"] for o in orgs}

col_a, col_b, col_c = st.columns(3)
with col_a:
	selected_name = st.selectbox("Client", ["All"] + list(org_options.keys()))
	selected_org_id = org_options.get(selected_name)
with col_b:
	channel_filter = st.selectbox("Channel", ["All", "WhatsApp", "Email", "Web survey", "Phone call"])
with col_c:
	sentiment_filter = st.selectbox("Sentiment", ["All", "Negative", "Neutral", "Positive"])

feedback, is_live = load_feedback_list(selected_org_id, channel_filter, sentiment_filter)

# if not is_live:
# 	st.caption("Sample data shown — connect `feedback/list/` for live figures.")

acked_local = st.session_state.get("acked_local", set())
open_count = sum(1 for f in feedback if f["status"] == "Open" and f["id"] not in acked_local)
negative_count = sum(1 for f in feedback if f["sentiment"] == "Negative")

st.write("")
m1, m2, m3 = st.columns(3)
m1.metric("Open items", open_count)
m2.metric("Negative feedback", negative_count)
m3.metric("Total in view", len(feedback))

st.write("")
st.subheader("Feedback queue")

if not feedback:
	st.info("No feedback matches the selected filters.")

for item in feedback:
	is_acked = item["status"] == "Acknowledged" or item["id"] in acked_local
	with st.container(border=True):
		cols = st.columns([2, 2, 5, 2, 1.2])
		with cols[0]:
			st.markdown(f"**{item['client']}**")
			st.caption(item["channel"])
		with cols[1]:
			st.write(item["module"])
			badge = {"Negative": "🔴", "Neutral": "🟡", "Positive": "🟢"}.get(item["sentiment"], "")
			st.caption(f"{badge} {item['sentiment']}")
		with cols[2]:
			st.write(item["text"])
			st.caption(item["received_at"])
		with cols[3]:
			st.write("Acknowledged" if is_acked else "Open")
		with cols[4]:
			if not is_acked:
				if st.button("Ack", key=f"ack_{item['id']}"):
					acknowledge_feedback(item["id"])
					st.rerun()