import streamlit as st
import openai

# Set page config
st.set_page_config(page_title="PainRelief.AI", page_icon="💪", layout="centered")

st.title("💪 PainRelief.AI")
st.subheader("Personalized Exercise Recommendations for Everyday Pain")
st.markdown("This app suggests safe, evidence-based exercises to help manage mild pain. ⚠️ *Not a substitute for medical care.*")

# User input
body_area = st.selectbox("Where is your pain?", ["Lower back", "Neck", "Shoulder", "Knee", "Foot", "Hip", "Other"])
description = st.text_area("Describe your pain (when it started, what makes it worse, etc.)")
intensity = st.slider("Pain intensity (1 = mild, 10 = severe)", 1, 10, 4)

# Submit button
if st.button("Get Exercise Plan"):
    with st.spinner("Generating your exercise plan..."):
        # AI prompt
        prompt = f"""
        You are a licensed physical therapist. Based on the following description, suggest 3-5 safe, gentle exercises to relieve pain.
        Avoid suggesting anything that requires equipment or medical diagnosis.

        Pain location: {body_area}
        Pain description: {description}
        Pain intensity: {intensity}/10

        Provide the output in this format:
        1. Exercise Name - short description of how to do it (2 sentences)
        2. Exercise Name - short description
        ...
        Include a safety note at the end.
        """

        # Use GPT API (requires API key)
        try:
            openai.api_key = st.secrets["OPENAI_API_KEY"]
            response = openai.ChatCompletion.create(
                model="gpt-5",
                messages=[{"role": "system", "content": "You are a helpful physical therapy assistant."},
                         {"role": "user", "content": prompt}],
                temperature=0.6
            )
            plan = response["choices"][0]["message"]["content"]
            st.success("Here’s your recommended exercise plan:")
            st.markdown(plan)
        except Exception as e:
            st.error(f"Error generating plan: {e}")

st.markdown("---")
st.caption("© 2025 PainRelief.AI | Educational use only. Always consult a healthcare provider for persistent or severe pain.")
