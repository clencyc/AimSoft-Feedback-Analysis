import streamlit as st
import requests
import os

BACKEND = os.getenv('BACKEND_API_URL', 'http://localhost:8000').rstrip('/')


def validate_token(token: str):
	try:
		resp = requests.get(f"{BACKEND}/api/public/feedback/{token}/", timeout=8)
		return resp
	except Exception:
		return None


def submit_feedback(token: str, payload: dict):
	try:
		resp = requests.post(f"{BACKEND}/api/public/feedback/{token}/submit/", json=payload, timeout=8)
		return resp
	except Exception:
		return None


def render_question(question):
	"""Renders one widget based on the question's configured type and
	returns whatever value the respondent enters."""
	qtype = question["question_type"]
	label = question["label"]
	help_text = question.get("help_text") or None
	key = f"q_{question['id']}"

	if qtype == "csat":
		emojis = ["😞", "🙁", "😐", "🙂", "😊"]
		return st.radio(label, options=[0, 1, 2, 3, 4], format_func=lambda x: emojis[x], horizontal=True, key=key, help=help_text)

	if qtype == "nps":
		val = st.slider(label, min_value=0, max_value=10, value=0, key=key, help=help_text)
		st.caption("0 = Not at all likely   10 = Extremely likely")
		return val

	if qtype == "rating_scale":
		max_scale = (question.get("options") or {}).get("max", 5)
		return st.selectbox(label, options=["Skip"] + list(range(1, max_scale + 1)), index=0, key=key, help=help_text)

	if qtype == "yes_no":
		return st.radio(label, options=["Yes", "No"], horizontal=True, key=key, help=help_text)

	if qtype == "single_choice":
		options = question.get("options") or []
		return st.selectbox(label, options=["Skip"] + options, index=0, key=key, help=help_text)

	if qtype == "multi_choice":
		options = question.get("options") or []
		return st.multiselect(label, options=options, key=key, help=help_text)

	if qtype == "long_text":
		return st.text_area(label, placeholder=help_text or "Type your answer...", height=120, key=key)

	# default: short_text
	return st.text_input(label, placeholder=help_text or "", key=key)


def build_legacy_schema(data):
	"""Backward compatibility: if the backend hasn't been updated to send
	form_schema yet, reconstruct the old fixed question set from
	rating_dimensions so this file still works against the old API."""
	legacy_dimensions = data.get('rating_dimensions') or []
	schema = [
		{"id": "csat", "question_type": "csat", "label": "Overall satisfaction", "required": True},
		{"id": "nps", "question_type": "nps", "label": "How likely are you to recommend?", "required": True},
	]
	schema += [
		{"id": f"dim_{d}", "question_type": "rating_scale", "label": d, "options": {"max": 5}, "required": False}
		for d in legacy_dimensions
	]
	schema += [
		{"id": "like_most", "question_type": "long_text", "label": "What do you like most about our product/service?", "required": False},
		{"id": "improve", "question_type": "long_text", "label": "What can we improve?", "required": False},
		{"id": "additional_comments", "question_type": "long_text", "label": "Any additional comments or suggestions?", "required": False},
	]
	return schema


def main():
	st.set_page_config(page_title="Share Your Feedback", layout="centered")

	st.title("Share your feedback")
	st.caption("Takes about 2 minutes. We truly appreciate your input at AimSoft!")

	query = st.query_params
	raw_token = query.get('token') or query.get('t')
	token = raw_token[0] if isinstance(raw_token, list) else raw_token

	if not token:
		st.error("This feedback page requires a token in the URL. Please use the shared link.")
		return

	resp = validate_token(token)
	if resp is None:
		st.error("Could not validate link — please try again later.")
		return
	if resp.status_code == 404:
		st.error("Feedback link not found.")
		return
	if resp.status_code == 410:
		st.error("This feedback link has expired or been revoked.")
		return
	if not resp.ok:
		st.error("Invalid feedback link.")
		return

	data = resp.json()
	form_schema = data.get('form_schema') or build_legacy_schema(data)

	st.caption("Anonymous · about 2 minutes")

	with st.form(key='feedback_form'):
		answers = {}
		for question in form_schema:
			answers[question["id"]] = render_question(question)
		submit = st.form_submit_button("Submit Feedback")

	if submit:
		required_ids = [q["id"] for q in form_schema if q.get("required")]
		missing = [qid for qid in required_ids if answers.get(qid) in (None, "", "Skip", [])]
		if missing:
			st.error("Please answer all required questions before submitting.")
			return

		payload = {"answers": answers}
		submit_resp = submit_feedback(token, payload)
		if submit_resp is not None and submit_resp.status_code in (200, 201):
			st.success("Thanks — your feedback has been recorded.")
			st.balloons()
		elif submit_resp is not None and submit_resp.status_code == 400:
			st.error(submit_resp.json().get('detail', 'Bad request'))
		elif submit_resp is not None and submit_resp.status_code == 410:
			st.error("This feedback link has expired or been revoked.")
		else:
			st.error("Failed to submit feedback — try again later.")


if __name__ == '__main__':
	main()