import streamlit as st
import requests

def main():
    st.set_page_config(page_title="Share Your Feedback", layout="centered")
    
    st.title("Share your feedback")
    st.caption("Takes about 2 minutes. We truly appreciate your input at AimSoft!")

    with st.form(key='feedback_form'):
        
        # CSAT
        st.subheader("Overall, how satisfied are you? (CSAT)")
        satisfaction_level = st.radio(
            label="CSAT Rating",
            options=[1, 2, 3, 4, 5],
            format_func=lambda x: ["😡 Very Dissatisfied", "🙁 Dissatisfied", "😐 Neutral", "🙂 Satisfied", "😊 Very Satisfied"][x-1],
            horizontal=True,
            label_visibility="collapsed"
        )

        # NPS
        st.subheader("How likely are you to recommend us to a friend or colleague? (NPS)")
        nps_cols = st.columns(11)
        recommend_others = st.session_state.get('nps_score', None)
        
        for i in range(11):
            with nps_cols[i]:
                if st.form_submit_button(
                    label=str(i),
                    key=f"nps_btn_{i}",
                    use_container_width=True,
                    help=f"Score {i}"
                ):
                    recommend_others = i
                    st.session_state.nps_score = i

        if recommend_others is not None:
            st.success(f"Selected NPS: **{recommend_others}**")
        st.caption("0 = Not likely at all                              10 = Extremely likely")

        st.divider()

        # Aspect Ratings
        st.subheader("Please rate the following aspects of our products/services:")
        aspects = ["Product Quality", "Ease of Use", "Customer Support", "Value for Money", "Delivery Speed"]
        ratings = {}

        for aspect in aspects:
            st.write(f"**{aspect}**")
            cols = st.columns(5)
            current_value = st.session_state.get(f"rating_{aspect}", 3)
            
            for i in range(1, 6):
                with cols[i-1]:
                    if st.form_submit_button(
                        label=str(i),
                        key=f"{aspect}_{i}",
                        use_container_width=True,
                        help=f"Rate {i}/5"
                    ):
                        current_value = i
                        st.session_state[f"rating_{aspect}"] = i
            
            ratings[aspect.lower().replace(" ", "_")] = current_value
            st.caption("1 = Poor                               5 = Excellent")
            st.divider()

        # Open-ended questions - Fixed with proper labels
        product_service = st.text_area(
            label="What do you like most about our product/service?",
            placeholder="Tell us what you loved...",
            height=100,
            key="like_most",
            label_visibility="collapsed"
        )

        product_improvement = st.text_area(
            label="What can we improve?",
            placeholder="What disappointed you? Any suggestions for the future?",
            height=120,
            key="improve",
            label_visibility="collapsed"
        )

        additional_comments = st.text_area(
            label="Any additional comments or suggestions?",
            placeholder="Optional...",
            height=100,
            key="additional",
            label_visibility="collapsed"
        )

        # Main Submit Button
        submit = st.form_submit_button("Submit Feedback", type="primary", use_container_width=True)

    if submit:
        if recommend_others is None:
            st.error("Please select a product satisfaction score.")
        else:
            data = {
                "satisfaction_level": satisfaction_level,
                "recommend_others": recommend_others,
                **ratings,
                "product_service": product_service,
                "product_improvement": product_improvement,
                "additional_comments": additional_comments,
            }

            try:
                response = requests.post(
                    "http://localhost:8000/feedback/", 
                    json=data,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code in [201, 200]:
                    st.success("Thank you for your feedback!")
                    st.balloons()
                    # Clear session state
                    for key in list(st.session_state.keys()):
                        if key.startswith("rating_") or key == "nps_score":
                            del st.session_state[key]
                else:
                    st.error("Failed to submit feedback.")
            except:
                st.error("Could not connect to the server. Please try again.")

if __name__ == "__main__":
    main()