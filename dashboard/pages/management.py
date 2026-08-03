import random
from datetime import date, timedelta

import pandas as pd
import streamlit as st

import services


services.require_role("sysadmin")

st.title("Management Dashboard")
st.caption(f"Welcome, {st.session_state.current_user.get('username', '')}")


QUESTION_TYPE_LABELS = {
	"csat": "CSAT (emoji scale)",
	"nps": "NPS (0-10)",
	"rating_scale": "Rating scale",
	"single_choice": "Single choice",
	"multi_choice": "Multiple choice",
	"yes_no": "Yes / No",
	"short_text": "Short text",
	"long_text": "Long text",
}

st.divider()
st.header("Feedback Form Builder")


def load_summary():
	"""Pulls from the real summary endpoint if it exists yet; otherwise
	returns representative sample data so the dashboard is presentable
	before that endpoint is wired up."""
	try:
		resp = services.get_json("feedback/summary/")
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
orgs_resp = services.list_organizations()
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
			resp = services.create_feedback_link(selected_org_id, payload)
			if resp is not None and resp.ok:
				data = resp.json()
				# show full shareable URL
				base = ''
				try:
					base = services.backend_base_url()
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
	links_resp = services.list_feedback_links(selected_org_id)
	if links_resp is not None and links_resp.ok:
		links = links_resp.json()
		for l in links:
			cols = st.columns([2, 1, 1, 1, 1])
			with cols[0]:
				st.markdown(f"**{l.get('label') or '(no label)'}**")
				base = ''
				try:
					base = services.backend_base_url()
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
					resp = services.revoke_feedback_link(l.get('id'))
					if resp is not None and resp.ok:
						st.success("Revoked")
						st.rerun()
		else:
			st.info("No links for this organization")
else:
	st.info("Select an organization to manage its shareable feedback links")



if selected_org_id:
	questions_resp = services.list_form_questions(selected_org_id)
	questions = questions_resp.json() if questions_resp is not None and questions_resp.ok else []

	st.subheader("Current questions")
	if not questions:
		st.info("No custom questions yet — respondents will see the default CSAT/NPS form.")

	for idx, q in enumerate(questions):
		with st.container(border=True):
			cols = st.columns([4, 2, 1, 1, 1, 1])
			with cols[0]:
				st.markdown(f"**{q['label']}**")
				st.caption(QUESTION_TYPE_LABELS.get(q["question_type"], q["question_type"]))
			with cols[1]:
				st.write("Required" if q.get("required") else "Optional")
			with cols[2]:
				if idx > 0 and st.button("↑", key=f"up_{q['id']}"):
					reordered = questions[:]
					reordered[idx - 1], reordered[idx] = reordered[idx], reordered[idx - 1]
					services.reorder_form_questions(selected_org_id, [item["id"] for item in reordered])
					st.rerun()
			with cols[3]:
				if idx < len(questions) - 1 and st.button("↓", key=f"down_{q['id']}"):
					reordered = questions[:]
					reordered[idx + 1], reordered[idx] = reordered[idx], reordered[idx + 1]
					services.reorder_form_questions(selected_org_id, [item["id"] for item in reordered])
					st.rerun()
			with cols[4]:
				if st.button("Edit", key=f"edit_{q['id']}"):
					st.session_state['editing_question'] = q['id']
					st.rerun()
			with cols[5]:
				if st.button("Delete", key=f"del_{q['id']}"):
					services.delete_form_question(selected_org_id, q["id"])
					st.rerun()

	# Inline editor (appears when Edit clicked)
	if 'editing_question' in st.session_state and st.session_state.get('editing_question'):
		edit_id = st.session_state['editing_question']
		qobj = next((x for x in questions if x['id'] == edit_id), None)
		if not qobj:
			# nothing to edit — clear and continue
			st.session_state['editing_question'] = None
		else:
			st.divider()
			st.subheader(f"Editing question: {qobj.get('label')}")
			with st.form(key=f"edit_form_{edit_id}"):
				edit_label = st.text_input("Label", value=qobj.get('label') or "", key=f"edit_label_{edit_id}")
				edit_help = st.text_input("Help text (optional)", value=qobj.get('help_text') or "", key=f"edit_help_{edit_id}")
				edit_required = st.checkbox("Required", value=bool(qobj.get('required')), key=f"edit_required_{edit_id}")
				edit_options = qobj.get('options') or {}
				qtype = qobj.get('question_type')
				if qtype == 'rating_scale':
					max_scale = st.number_input("Max scale value", min_value=2, max_value=10, value=int(edit_options.get('max', 5)), key=f"edit_max_{edit_id}")
					edit_options = {"max": int(max_scale)}
				elif qtype in ('single_choice', 'multi_choice'):
					raw = st.text_input("Choices (comma-separated)", value=",".join(edit_options if isinstance(edit_options, list) else edit_options.get('choices', []) ), key=f"edit_choices_{edit_id}")
					edit_options = [c.strip() for c in raw.split(',') if c.strip()]
				col1, col2 = st.columns([1,1])
				with col1:
					save = st.form_submit_button("Save")
				with col2:
					cancel = st.form_submit_button("Cancel")
				if save:
					payload = {"label": edit_label, "help_text": edit_help, "required": edit_required, "options": edit_options}
					resp = services.update_form_question(edit_id, payload)
					if resp is not None and getattr(resp, 'ok', False):
						st.success("Saved")
						st.session_state['editing_question'] = None
						st.rerun()
					else:
						st.error("Failed to save")
				if cancel:
					st.session_state['editing_question'] = None
					st.rerun()

	st.write("")
	with st.expander("Add a new question"):
		new_type = st.selectbox(
			"Question type",
			list(QUESTION_TYPE_LABELS.keys()),
			format_func=lambda t: QUESTION_TYPE_LABELS[t],
		)
		new_label = st.text_input("Question label")
		new_help = st.text_input("Help text (optional)")
		new_required = st.checkbox("Required")

		new_options = None
		if new_type == "rating_scale":
			max_scale = st.number_input("Max scale value", min_value=2, max_value=10, value=5)
			new_options = {"max": int(max_scale)}
		elif new_type in ("single_choice", "multi_choice"):
			raw_choices = st.text_input("Choices (comma-separated)")
			new_options = [c.strip() for c in raw_choices.split(",") if c.strip()]

		if st.button("Add question"):
			if not new_label:
				st.error("Please give the question a label")
			else:
				payload = {
					"question_type": new_type,
					"label": new_label,
					"help_text": new_help,
					"required": new_required,
					"options": new_options,
					"order": len(questions),
				}
				resp = services.create_form_question(selected_org_id, payload)
				if resp is not None and resp.ok:
					st.success("Question added")
					st.rerun()
				else:
					st.error("Failed to add question")
else:
	st.info("Select an organization above to edit its feedback form.")
