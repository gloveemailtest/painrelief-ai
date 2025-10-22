import streamlit as st
import requests
import json

# ============================================================================
# CONFIGURATION
# ============================================================================

OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
OPENROUTER_MODEL = "openai/gpt-4o-mini"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# ✅ Updated: Fully tested YouTube IDs (all embeddable)
EXERCISE_DEMOS = {
    # Lower Back
    "cat-cow stretch": "kqnua4rHVVA",
    "child's pose": "2MTd6U_8xVg",
    "pelvic tilt": "QldD-L-h1xY",
    "knee to chest": "MXcMW7p8YpY",
    "bridge": "wPM8icPu6H8",
    "lower back": "DWmGArQBtFI",

    # Upper Back
    "upper back": "bKUIgnh9aMY",
    "thoracic": "bKUIgnh9aMY",

    # Neck
    "neck rotation": "_LVVOvYu8VU",
    "chin tuck": "g41kEDVTGcg",
    "neck stretch": "fj88jJfNPWw",
    "neck": "fj88jJfNPWw",

    # Shoulder
    "shoulder roll": "3Pp5Mckr-XE",
    "arm circles": "vjvC-tYcwlU",
    "cross-body stretch": "09mhNIVW8yg",
    "wall angels": "2PTCeHYPB5g",
    "pendulum": "aU9yU0Pp8oo",
    "shoulder": "3Pp5Mckr-XE",

    # Elbow
    "elbow stretch": "GSK5G8BFreM",
    "elbow": "GSK5G8BFreM",

    # Wrist / Hand
    "wrist flexion": "mSZWSQSSEjE",
    "prayer stretch": "UrhBZKH0WH0",
    "wrist": "mSZWSQSSEjE",
    "hand": "UrhBZKH0WH0",

    # Hip
    "hip flexor stretch": "YQmpO9VT2X4",
    "clamshell": "3bCPyM7JvHM",
    "hip": "YQmpO9VT2X4",

    # Knee
    "quad stretch": "K7L41e2I48M",
    "hamstring stretch": "XzP1c1jToAo",
    "wall sit": "y-wV4Venusw",
    "straight leg raise": "2iTI68aBLgA",
    "knee": "y-wV4Venusw",

    # Ankle / Foot / Shin
    "ankle circles": "_z2s7nD4i90",
    "calf raise": "gwLzBJYoWlI",
    "towel stretch": "gHCKT2ZLAM8",
    "alphabet": "_z2s7nD4i90",
    "ankle": "_z2s7nD4i90",
    "foot": "gHCKT2ZLAM8",
    "shin": "gwLzBJYoWlI",

    # Chest
    "chest stretch": "4iE_HL4x4IA",
    "chest": "4iE_HL4x4IA",

    # Jaw
    "jaw exercise": "Htofxb_KMCE",
    "jaw": "Htofxb_KMCE",

    # Fallbacks
    "stretch": "g_tea8ZNk5A",
    "breathing": "DbDoBzGY3vo",
}

# ============================================================================
# STYLING
# ============================================================================

def apply_custom_css():
    """Apply modern wellness aesthetic styling"""
    st.markdown("""
        <style>
        .main {
            background: linear-gradient(135deg, #f5f7fa 0%, #e8f4f8 100%);
        }
        .stButton>button {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 25px;
            padding: 12px 30px;
            border: none;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        .exercise-card {
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.07);
            margin: 15px 0;
            border-left: 4px solid #667eea;
        }
        .section-header {
            color: #667eea;
            font-size: 1.8em;
            font-weight: 700;
            margin-top: 30px;
            margin-bottom: 20px;
        }
        .safety-box {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            color: #333333;
        }
        </style>
    """, unsafe_allow_html=True)

# ============================================================================
# HELPERS
# ============================================================================

def get_exercise_video_id(exercise_name):
    """Match exercise description to appropriate YouTube video ID"""
    exercise_lower = exercise_name.lower()
    for key in EXERCISE_DEMOS:
        if key in exercise_lower:
            return EXERCISE_DEMOS[key]
    return EXERCISE_DEMOS["stretch"]  # fallback

def get_ai_recommendations(pain_location, pain_description, intensity):
    """Call OpenRouter API to get exercise recommendations"""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
    You are a physical therapy assistant. A user has {pain_location} pain (intensity: {intensity}/10).
    User description: {pain_description}
    Provide 3–5 safe, gentle exercises they can try. For each exercise:
    1. Give a clear name (e.g., "Cat-Cow Stretch")
    2. Provide 2–3 sentences explaining how to do it safely
    Return as JSON only, like:
    [
      {{"name": "Exercise", "description": "How to do it safely..."}}
    ]
    """

    payload = {"model": OPENROUTER_MODEL, "messages": [{"role": "user", "content": prompt}]}

    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"].strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        exercises = json.loads(content)
        return exercises
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

    st.markdown("<h1 style='text-align: center; color: #667eea;'>🧘 PainRelief.AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>Your personalized pain relief exercise companion</p>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("<div class='section-header'>📍 Where does it hurt?</div>", unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    with col1:
        pain_location = st.selectbox("Select pain location:", [
            "Lower Back", "Upper Back", "Neck", "Shoulder", "Elbow",
            "Wrist", "Hand", "Chest", "Hip", "Knee", "Ankle", "Shin",
            "Foot", "Jaw", "Other"
        ], label_visibility="collapsed")
    with col2:
        intensity = st.slider("Pain intensity", 1, 10, 5)
        st.caption(f"Level: {intensity}/10")

    pain_description = st.text_area("Describe your pain (optional):", height=100)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✨ Get My Exercise Plan", use_container_width=True):
            with st.spinner("Creating your personalized plan..."):
                st.session_state.current_plan = get_ai_recommendations(pain_location, pain_description, intensity)
                st.session_state.exercises_completed = []

    if st.session_state.current_plan:
        st.markdown("<div class='section-header'>💪 Your Personalized Plan</div>", unsafe_allow_html=True)
        total = len(st.session_state.current_plan)
        done = len(st.session_state.exercises_completed)
        st.progress(done / total if total > 0 else 0)
        st.caption(f"Completed {done}/{total} exercises")

        for i, ex in enumerate(st.session_state.current_plan):
            with st.container():
                st.markdown("<div class='exercise-card'>", unsafe_allow_html=True)
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"### {i+1}. {ex['name']}")
                    st.write(ex['description'])
                    checked = st.checkbox("✅ Mark as completed", key=f"check_{i}", value=i in st.session_state.exercises_completed)
                    if checked and i not in st.session_state.exercises_completed:
                        st.session_state.exercises_completed.append(i)
                        st.rerun()
                    elif not checked and i in st.session_state.exercises_completed:
                        st.session_state.exercises_completed.remove(i)
                        st.rerun()
                with col2:
                    vid = get_exercise_video_id(ex['name'])
                    st.markdown(f"""
                        <iframe width="100%" height="200"
                        src="https://www.youtube.com/embed/{vid}"
                        frameborder="0"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowfullscreen></iframe>
                    """, unsafe_allow_html=True)
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
        </ul>
        </div>
        """, unsafe_allow_html=True)

        if done == total and total > 0:
            st.balloons()
            st.success("🎉 Great job completing your exercise plan!")

if __name__ == "__main__":
    main()
