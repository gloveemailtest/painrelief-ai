import streamlit as st
import requests
import json

# ============================================================================
# CONFIGURATION
# ============================================================================

OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
OPENROUTER_MODEL = "openai/gpt-4o-mini"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# ✅ Tested YouTube videos (embeddable) and GIF fallbacks
EXERCISE_MEDIA = {
    # Lower Back
    "cat-cow stretch": {"youtube": "kqnua4rHVVA", "gif": "https://media.tenor.com/e1tA7IKD1isAAAAC/cat-cow-yoga.gif"},
    "child's pose": {"youtube": "2MTd6U_8xVg", "gif": "https://media.tenor.com/L5oXMs1RCbMAAAAC/childs-pose-yoga.gif"},
    "pelvic tilt": {"youtube": "QldD-L-h1xY", "gif": "https://media.tenor.com/9qQ4OGgZ5YcAAAAC/pelvic-tilt-exercise.gif"},
    "bridge": {"youtube": "wPM8icPu6H8", "gif": "https://media.tenor.com/_K6AoJ6PdrwAAAAC/bridge-exercise.gif"},

    # Neck
    "neck rotation": {"youtube": "_LVVOvYu8VU", "gif": "https://media.tenor.com/tbYdfV6TIEUAAAAC/neck-stretch.gif"},
    "chin tuck": {"youtube": "g41kEDVTGcg", "gif": "https://media.tenor.com/3yOEPPG29DgAAAAC/chin-tuck-neck.gif"},
    "neck stretch": {"youtube": "fj88jJfNPWw", "gif": "https://media.tenor.com/3x0Z6pDWWxYAAAAC/neck-stretch-exercise.gif"},

    # Shoulder
    "shoulder roll": {"youtube": "3Pp5Mckr-XE", "gif": "https://media.tenor.com/W6r6mu5RpjYAAAAC/shoulder-rolls.gif"},
    "arm circles": {"youtube": "vjvC-tYcwlU", "gif": "https://media.tenor.com/Qa0CPDhvzC4AAAAC/arm-circles.gif"},
    "pendulum": {"youtube": "aU9yU0Pp8oo", "gif": "https://media.tenor.com/5UNSlgWgK6oAAAAC/pendulum-shoulder.gif"},

    # Hip
    "hip flexor stretch": {"youtube": "YQmpO9VT2X4", "gif": "https://media.tenor.com/Keu6nO9X8vsAAAAC/hip-flexor-stretch.gif"},
    "clamshell": {"youtube": "3bCPyM7JvHM", "gif": "https://media.tenor.com/V5zpiqD2p08AAAAC/clamshell-exercise.gif"},

    # Knee / Leg
    "hamstring stretch": {"youtube": "XzP1c1jToAo", "gif": "https://media.tenor.com/0ZYsacL8ZVcAAAAC/hamstring-stretch.gif"},
    "quad stretch": {"youtube": "K7L41e2I48M", "gif": "https://media.tenor.com/dm6uF93z8KkAAAAC/quad-stretch.gif"},
    "wall sit": {"youtube": "y-wV4Venusw", "gif": "https://media.tenor.com/8mOGswULjPMAAAAC/wall-sit.gif"},
    "straight leg raise": {"youtube": "2iTI68aBLgA", "gif": "https://media.tenor.com/8xKzL4W0LVEAAAAC/straight-leg-raise.gif"},

    # Ankle / Foot
    "ankle circles": {"youtube": "_z2s7nD4i90", "gif": "https://media.tenor.com/jYngHUV1Gv8AAAAC/ankle-circles.gif"},
    "calf raise": {"youtube": "gwLzBJYoWlI", "gif": "https://media.tenor.com/3rQ70YbsnxYAAAAC/calf-raise.gif"},

    # Chest
    "chest stretch": {"youtube": "4iE_HL4x4IA", "gif": "https://media.tenor.com/NF1C1ZoM0PcAAAAC/chest-stretch.gif"},

    # Fallback
    "stretch": {"youtube": "g_tea8ZNk5A", "gif": "https://media.tenor.com/pjwzLzj1H5oAAAAC/stretch-yoga.gif"},
}

# ============================================================================
# STYLING
# ============================================================================

def apply_custom_css():
    st.markdown("""
        <style>
        .main {background: linear-gradient(135deg, #f5f7fa 0%, #e8f4f8 100%);}
        .stButton>button {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white; border-radius: 25px; padding: 12px 30px; border: none;
            font-weight: 600; transition: all 0.3s ease;
        }
        .stButton>button:hover {transform: translateY(-2px); box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);}
        .exercise-card {
            background: white; padding: 20px; border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.07); margin: 15px 0;
            border-left: 4px solid #667eea;
        }
        .section-header {color: #667eea; font-size: 1.8em; font-weight: 700; margin-top: 30px; margin-bottom: 20px;}
        .safety-box {
            background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px;
            border-radius: 8px; margin: 20px 0; color: #333333;
        }
        </style>
    """, unsafe_allow_html=True)

# ============================================================================
# HELPERS
# ============================================================================

def get_exercise_media(exercise_name):
    """Find matching exercise media (YouTube or GIF)."""
    name = exercise_name.lower()
    for key, val in EXERCISE_MEDIA.items():
        if key in name:
            return val
    return EXERCISE_MEDIA["stretch"]

def get_ai_recommendations(pain_location, pain_description, intensity):
    """Call OpenRouter API to get exercise recommendations"""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    prompt = f"""
    You are a physical therapy assistant. A user has {pain_location} pain (intensity: {intensity}/10).
    Description: {pain_description}
    Provide 3–5 safe, gentle home exercises. For each:
    - Give a short, clear name (like "Cat-Cow Stretch")
    - Explain in 2–3 sentences how to perform it safely
    Return only valid JSON:
    [{{"name":"Exercise","description":"How to do it safely"}}]
    """
    payload = {"model": OPENROUTER_MODEL, "messages": [{"role": "user", "content": prompt}]}
    try:
        res = requests.post(OPENROUTER_URL, headers=headers, json=payload)
        res.raise_for_status()
        data = res.json()
        content = data["choices"][0]["message"]["content"].strip()
        if content.startswith("```json"): content = content[7:]
        if content.endswith("```"): content = content[:-3]
        return json.loads(content)
    except Exception as e:
        st.error(f"Error: {e}")
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

    # Input Section
    st.markdown("<div class='section-header'>📍 Where does it hurt?</div>", unsafe_allow_html=True)
    col1, col2 = st.columns([2,1])
    with col1:
        location = st.selectbox("Pain location", [
            "Lower Back", "Upper Back", "Neck", "Shoulder", "Elbow",
            "Wrist", "Hand", "Chest", "Hip", "Knee", "Ankle", "Shin", "Foot", "Jaw", "Other"
        ], label_visibility="collapsed")
    with col2:
        intensity = st.slider("Pain intensity", 1, 10, 5)
        st.caption(f"Level: {intensity}/10")
    desc = st.text_area("Describe your pain (optional):", height=100)

    if st.button("✨ Get My Exercise Plan", use_container_width=True):
        with st.spinner("Generating your personalized plan..."):
            st.session_state.current_plan = get_ai_recommendations(location, desc, intensity)
            st.session_state.exercises_completed = []

    # Display Plan
    if st.session_state.current_plan:
        st.markdown("<div class='section-header'>💪 Your Personalized Plan</div>", unsafe_allow_html=True)
        total = len(st.session_state.current_plan)
        done = len(st.session_state.exercises_completed)
        st.progress(done / total if total else 0)
        st.caption(f"Completed {done}/{total} exercises")

        for i, ex in enumerate(st.session_state.current_plan):
            media = get_exercise_media(ex["name"])
            st.markdown("<div class='exercise-card'>", unsafe_allow_html=True)
            col1, col2 = st.columns([2,1])
            with col1:
                st.markdown(f"### {i+1}. {ex['name']}")
                st.write(ex["description"])
                check = st.checkbox("✅ Mark as completed", key=f"check_{i}", value=i in st.session_state.exercises_completed)
                if check and i not in st.session_state.exercises_completed:
                    st.session_state.exercises_completed.append(i)
                    st.rerun()
                elif not check and i in st.session_state.exercises_completed:
                    st.session_state.exercises_completed.remove(i)
                    st.rerun()
            with col2:
                try:
                    st.markdown(f"""
                        <iframe width="100%" height="200"
                        src="https://www.youtube.com/embed/{media['youtube']}"
                        frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowfullscreen></iframe>
                    """, unsafe_allow_html=True)
                except:
                    st.image(media["gif"], use_column_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Safety Section
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
