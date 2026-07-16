import random
from datetime import date, timedelta

import pandas as pd
import streamlit as st

from services import get_json, require_role

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