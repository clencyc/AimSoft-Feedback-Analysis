import streamlit as st


def main():
    st.title("Customer Feedback Form")
    st.write("At AimSoft, we value your feedback! Please take a moment to fill out this form and let us know about your experience with our products and services.")

    with st.form(key='feeback_form'):
        satisfaction_level = st.slider("How satisfied are you with our products/services?", 1, 5, 3)
        recommend_others = st.slider("How likely are you to recommend our products/services to others?", 1, 5, 3)

        st.title("Please rate the following aspects of our products/services:")
        product_quality = st.slider("Rate the quality of our products.", 1, 5, 3)
        ease_of_use = st.slider("Rate the ease of use of our products.", 1, 5, 3)
        customer_support = st.slider("Rate the quality of our customer support.", 1, 5, 3)
        value_for_money = st.slider("Rate the value for money of our products/services.", 1, 5, 3)
        delivery_speed = st.slider("Rate the speed of our product/service delivery.", 1, 5, 3)

        st.title("What do you like most about our product?")
        product_service = st.text_area("What do you like most about our product?")
        product_improvement = st.text_area("What would we improve? What dissapointed you? What would you like to see in the future?")
        additianal_comments = st.text_area("Any additional comments or suggestions?")



        submit = st.form_submit_button(label='Submit')




if __name__ == "__main__":
    main()


