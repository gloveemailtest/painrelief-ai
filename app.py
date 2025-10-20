import streamlit as st
import requests

st.set_page_config(page_title="PainRelief.AI", page_icon="💪", layout="centered")

st.title("💪 PainRelief.AI")
st.subheader("Personalized Exercise Recommendations for Everyday Pain")
st.markdown("This app suggests safe, evidence-based exercises to help manage mild pain. ⚠️ *Not a substitute for medical care.*")

body_area = st.selectbox("Where is your pain?", ["Lower back", "Neck", "Shoulder", "Knee", "Foot", "Hip", "Other"])
description = st.text_area("Describe your pain (when it started, what makes it worse, etc.)")
intensity = st.slider("Pain intensity (1 = mild, 10 = severe)", 1, 10, 4)

if st.button("Get Exercise Plan"):
    with st.spinner("Generating your exercise plan..."):
        prompt = f"""
        You are a licensed physical therapist. Based on the following description, suggest 3–5 safe, gentle exercises to relieve pain.
        Avoid suggesting anything that requires equipment or medical diagnosis.

        Pain location: {body_area}
        Pain description: {description}
        Pain intensity: {intensity}/10

        Provide the output in this format:
        1. Exercise Name - short description (2 sentences)
        2. Exercise Name - short description
        Include a safety note at the end.
        """

        try:
            headers = {
                "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
                "HTTP-Referer": "https://painrelief-ai.streamlit.app",  # your app URL (optional but helps routing)
                "X-Title": "PainRelief.AI"
            }

            payload = {
                "model": "openai/gpt-4o-mini",  # or try "mistralai/mixtral-8x7b" etc.
                "messages": [
                    {"role": "system", "content": "You are a helpful physical therapy assistant."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.6
            }

            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
            data = response.json()

            if "choices" in data:
                plan = data["choices"][0]["message"]["content"]
                st.success("Here’s your recommended exercise plan:")
                st.markdown(plan)
            else:
                st.error(f"Unexpected response: {data}")

        except Exception as e:
            st.error(f"Error generating plan: {e}")

st.markdown("---")
st.caption("© 2025 PainRelief.AI | Educational use only. Always consult a healthcare provider for persistent or severe pain.")

