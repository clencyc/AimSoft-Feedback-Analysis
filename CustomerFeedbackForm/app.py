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


def main():
    st.set_page_config(page_title="Share Your Feedback", layout="centered")

    st.title("Share your feedback")
    st.caption("Takes about 2 minutes. We truly appreciate your input at AimSoft!")

    query = st.query_params
    # query params values can be lists; accept either ['token']=['...'] or ['token']='...'
    raw_token = query.get('token') or query.get('t')
    if isinstance(raw_token, list):
        token = raw_token[0] if raw_token else None
    else:
        token = raw_token

    # st.write("query:", query)
    # st.write("resolved token:", token)

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
    rating_dimensions = data.get('rating_dimensions') or []

    st.caption("Anonymous · about 2 minutes")
  
    # CSAT: 0-4 where 0=Very Dissatisfied ... 4=Very Satisfied
    if 'csat_score' not in st.session_state:
        st.session_state.csat_score = None
    if 'nps_score' not in st.session_state:
        st.session_state.nps_score = None
    if 'dimension_ratings' not in st.session_state:
        st.session_state.dimension_ratings = {}

    with st.form(key='feedback_form'):
        st.markdown("#### Overall satisfaction")
        csat_options = [0, 1, 2, 3, 4]
        csat_emojis = ["😞", "🙁", "😐", "🙂", "😊"]
        csat_choice = st.radio("", options=csat_options, format_func=lambda x: csat_emojis[x], horizontal=True, key='csat_radio')
        st.session_state.csat_score = csat_choice

        st.markdown("#### Net Promoter Score (NPS)")
        nps_choice = st.slider("How likely are you to recommend?", min_value=0, max_value=10, value=0, key='nps_slider')
        st.session_state.nps_score = nps_choice
        st.caption("0 = Not at all likely   10 = Extremely likely")

        # Dimension ratings
        st.markdown("#### Please rate the following aspects (optional)")
        for dim in rating_dimensions:
            st.write(f"**{dim}**")
            val = st.selectbox("", options=["Skip",1,2,3,4,5], index=0, key=f'dim_select_{dim}')
            if val != "Skip":
                st.session_state.dimension_ratings[dim] = int(val)
            elif dim in st.session_state.dimension_ratings:
                st.session_state.dimension_ratings.pop(dim, None)
            st.caption("1 = Poor 5 = Excellent")

        like_most = st.text_area("What do you like most about our product/service?", placeholder="Tell us what you loved...", height=100)
        improve = st.text_area("What can we improve?", placeholder="What disappointed you? Any suggestions for the future?", height=120)
        additional_comments = st.text_area("Any additional comments or suggestions?", placeholder="Optional...", height=100, max_chars=200)

        # Disable submit until CSAT and NPS present
        submit_disabled = st.session_state.get('csat_score') is None or st.session_state.get('nps_score') is None
        submit = st.form_submit_button("Submit Feedback", disabled=submit_disabled)

    if submit:
        payload = {
            "csat_score": st.session_state.csat_score,
            "nps_score": st.session_state.nps_score,
            "dimension_ratings": st.session_state.dimension_ratings or None,
            "like_most": like_most,
            "improve": improve,
            "additional_comments": additional_comments,
        }
        submit_resp = submit_feedback(token, payload)
        if submit_resp is not None and submit_resp.status_code in (200, 201):
            st.success("Thanks — your feedback has been recorded.")
            st.balloons()
            # clear selections
            st.session_state.csat_score = None
            st.session_state.nps_score = None
            st.session_state.dimension_ratings = {}
        elif submit_resp is not None and submit_resp.status_code == 400:
            st.error(submit_resp.json().get('detail', 'Bad request'))
        elif submit_resp is not None and submit_resp.status_code == 410:
            st.error("This feedback link has expired or been revoked.")
        else:
            st.error("Failed to submit feedback — try again later.")


if __name__ == '__main__':
    main()
