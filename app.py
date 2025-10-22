import streamlit as st
import requests
import json

# ============================================================================
# CONFIGURATION
# ============================================================================

OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
OPENROUTER_MODEL = "openai/gpt-4o-mini"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# ✅ Updated with short verified YouTube 'how-to' clips
EXERCISE_MEDIA = {
    "cat-cow stretch": {"youtube": "https://www.youtube.com/watch?v=CiGpYH7j6hU"},
    "child's pose": {"youtube": "https://www.youtube.com/watch?v=QsXWszvjZ8w"},
    "pelvic tilt": {"youtube": "https://www.youtube.com/watch?v=ybBccO4fze4"},
    "bridge": {"youtube": "https://www.youtube.com/watch?v=wPM8icPu6H8"},
    "hamstring stretch": {"youtube": "https://www.youtube.com/watch?v=fs_e9Ai2nlo"},
    "neck stretch": {"youtube": "https://www.youtube.com/watch?v=z6VxZ2XzK2w"},
    "chin tuck": {"youtube": "https://www.youtube.com/watch?v=tsv7Dq8m73I"},
    "shoulder roll": {"youtube": "https://www.youtube.com/watch?v=8W9G0cR0U7Y"},
    "arm circles": {"youtube": "https://www.youtube.com/watch?v=5eK3yY5xS1A"},
    "pendulum": {"youtube": "https://www.youtube.com/watch?v=kLgkGqZ8I_A"},
    "hip flexor stretch": {"youtube": "https://www.youtube.com/watch?v=ly5wFqYE4lc"},
    "clamshell": {"youtube": "https://www.youtube.com/watch?v=GgPBxgYDLwU"},
    "quad stretch": {"youtube": "https://www.youtube.com/watch?v=riEXN0TqN4o"},
    "wall sit": {"youtube": "https://www.youtube.com/watch?v=-cdph8hv0O0"},
    "straight leg raise": {"youtube": "https://www.youtube.com/watch?v=wgPzV6H3Wok"},
    "ankle circles": {"youtube": "https://www.youtube.com/watch?v=gF4dV8qD6AA"},
    "calf raise": {"youtube": "https://www.youtube.com/watch?v=-M4-G8p8fmc"},
    "chest stretch": {"youtube": "https://www.youtube.com/watch?v=XhSvkE5qofM"},
    "stretch": {"youtube": "https://www.youtube.com/watch?v=g_tea8ZNk5A"}
}


# ============================================================================
# STYLING
# ============================================================================

def apply_custom_css():
    st.markdown("""
        <style>
        .main {background: linear-gradient(135deg,#f5f7fa 0%,#e8f4f8 100%);}
        .stButton>button {
            background: linear-gradient(90deg,#667eea 0%,#764ba2 100%);
            color:white;border-radius:25px;padding:10px 25px;border:none;
            font-weight:600;transition:all .3s ease;
        }
        .stButton>button:hover{transform:translateY(-2px);box-shadow:0 5px 15px rgba(102,126,234,0.4);}
        .exercise-card{background:white;padding:20px;border-radius:15px;
            box-shadow:0 4px 6px rgba(0,0,0,0.07);margin:15px 0;border-left:4px solid #667eea;}
        .section-header{color:#667eea;font-size:1.8em;font-weight:700;margin-top:30px;margin-bottom:15px;}
        .safety-box{background:#fff3cd;border-left:4px solid #ffc107;padding:15px;border-radius:8px;margin:20px 0;color:#333;}
        </style>
    """, unsafe_allow_html=True)

# ============================================================================
# HELPERS
# ============================================================================

def get_exercise_media(name):
    name = name.lower()
    for key, val in EXERCISE_MEDIA.items():
        if key in name:
            return val
    return EXERCISE_MEDIA["stretch"]

def get_ai_recommendations(location, description, intensity):
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    prompt = f"""
    You are a physical therapy assistant. A user has {location} pain (intensity {intensity}/10).
    Description: {description}
    Provide 3–5 safe home exercises (name + short how-to). Return pure JSON array:
    [{{"name":"Exercise","description":"How to do it"}}]
    """
    payload = {"model": OPENROUTER_MODEL, "messages": [{"role": "user", "content": prompt}]}
    try:
        res = requests.post(OPENROUTER_URL, headers=headers, json=payload)
        res.raise_for_status()
        data = res.json()
        text = data["choices"][0]["message"]["content"].strip()
        if text.startswith("```json"): text = text[7:]
        if text.endswith("```"): text = text[:-3]
        return json.loads(text)
    except Exception as e:
        st.error(f"Error getting exercises: {e}")
        return []

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    apply_custom_css()

    if "exercises_completed" not in st.session_state:
        st.session_state.exercises_completed = []
    if "current_plan" not in st.session_state:
        st.session_state.current_plan = None

    st.markdown("<h1 style='text-align:center;color:#667eea;'>🧘 PainRelief.AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#666;'>Your personalized pain relief exercise companion</p>", unsafe_allow_html=True)
    st.markdown("---")

    col1, col2 = st.columns([2,1])
    with col1:
        location = st.selectbox("Where does it hurt?", [
            "Lower Back","Upper Back","Neck","Shoulder","Elbow","Wrist",
            "Hand","Chest","Hip","Knee","Ankle","Shin","Foot","Jaw","Other"
        ])
    with col2:
        intensity = st.slider("Pain intensity", 1, 10, 5)
        st.caption(f"Level: {intensity}/10")
    description = st.text_area("Describe your pain (optional):", height=100)

    if st.button("✨ Get My Exercise Plan", use_container_width=True):
        with st.spinner("Creating your personalized plan..."):
            st.session_state.current_plan = get_ai_recommendations(location, description, intensity)
            st.session_state.exercises_completed = []

    if st.session_state.current_plan:
        st.markdown("<div class='section-header'>💪 Your Personalized Plan</div>", unsafe_allow_html=True)
        total = len(st.session_state.current_plan)
        done = len(st.session_state.exercises_completed)
        st.progress(done/total if total else 0)
        st.caption(f"Completed {done}/{total} exercises")

        for i, ex in enumerate(st.session_state.current_plan):
            media = get_exercise_media(ex["name"])
            st.markdown("<div class='exercise-card'>", unsafe_allow_html=True)
            col1, col2 = st.columns([2,1])
            with col1:
                st.markdown(f"### {i+1}. {ex['name']}")
                st.write(ex["description"])
                checked = st.checkbox("✅ Mark as completed", key=f"check_{i}", value=i in st.session_state.exercises_completed)
                if checked and i not in st.session_state.exercises_completed:
                    st.session_state.exercises_completed.append(i)
                    st.rerun()
                elif not checked and i in st.session_state.exercises_completed:
                    st.session_state.exercises_completed.remove(i)
                    st.rerun()
            with col2:
                # Use short verified 'how-to' video clips
                if media["youtube"]:
                    st.video(media["youtube"])
                st.markdown(
                    f"""
                    <a href="{media['youtube']}" target="_blank"
                       style="display:inline-block;margin-top:8px;background:#667eea;color:white;
                              padding:6px 12px;border-radius:8px;text-decoration:none;font-weight:600;">
                       ▶ Watch on YouTube
                    </a>
                    """,
                    unsafe_allow_html=True
                )

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='section-header'>⚠️ Important Safety Information</div>", unsafe_allow_html=True)
        st.markdown("""
        <div class='safety-box'>
        <strong>Please note:</strong> This tool provides general exercise suggestions and is not a substitute for professional medical advice.
        <ul>
        <li>Stop immediately if any exercise causes pain</li>
        <li>Consult a healthcare provider for persistent pain</li>
        <li>Start slowly and listen to your body</li>
        <li>These exercises are for mild to moderate discomfort only</li>
        <li>If symptoms persist >2 weeks, seek medical attention</li>
        </ul></div>
        """, unsafe_allow_html=True)

        if done == total and total > 0:
            st.balloons()
            st.success("🎉 Great job completing your exercise plan!")

if __name__ == "__main__":
    main()
