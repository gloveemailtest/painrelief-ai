import streamlit as st
import requests
import json

# ============================================================================
# CONFIGURATION
# ============================================================================

OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
OPENROUTER_MODEL = "openai/gpt-4o-mini"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# ✅ GIF-first media library with YouTube links as optional buttons
EXERCISE_MEDIA = {
    # Lower Back
    "cat-cow stretch": {
        "gif": "https://media.tenor.com/e1tA7IKD1isAAAAC/cat-cow-yoga.gif",
        "youtube": "https://www.youtube.com/watch?v=kqnua4rHVVA"
    },
    "child's pose": {
        "gif": "https://media.tenor.com/L5oXMs1RCbMAAAAC/childs-pose-yoga.gif",
        "youtube": "https://www.youtube.com/watch?v=qYvYsFRNTj8"
    },
    "pelvic tilt": {
        "gif": "https://media.tenor.com/9qQ4OGgZ5YcAAAAC/pelvic-tilt-exercise.gif",
        "youtube": "https://www.youtube.com/watch?v=JhE4M3oE-Uo"
    },
    "bridge": {
        "gif": "https://media.tenor.com/_K6AoJ6PdrwAAAAC/bridge-exercise.gif",
        "youtube": "https://www.youtube.com/watch?v=wPM8icPu6H8"
    },

    # Neck
    "neck rotation": {
        "gif": "https://media.tenor.com/tbYdfV6TIEUAAAAC/neck-stretch.gif",
        "youtube": "https://www.youtube.com/watch?v=lJzjM4tKp8Q"
    },
    "chin tuck": {
        "gif": "https://media.tenor.com/3yOEPPG29DgAAAAC/chin-tuck-neck.gif",
        "youtube": "https://www.youtube.com/watch?v=tsv7Dq8m73I"
    },
    "neck stretch": {
        "gif": "https://media.tenor.com/3x0Z6pDWWxYAAAAC/neck-stretch-exercise.gif",
        "youtube": "https://www.youtube.com/watch?v=ay0P1zYfJ3o"
    },

    # Shoulder
    "shoulder roll": {
        "gif": "https://media.tenor.com/W6r6mu5RpjYAAAAC/shoulder-rolls.gif",
        "youtube": "https://www.youtube.com/watch?v=7O6PZ3yG2lI"
    },
    "arm circles": {
        "gif": "https://media.tenor.com/Qa0CPDhvzC4AAAAC/arm-circles.gif",
        "youtube": "https://www.youtube.com/watch?v=5eK3yY5xS1A"
    },
    "pendulum": {
        "gif": "https://media.tenor.com/5UNSlgWgK6oAAAAC/pendulum-shoulder.gif",
        "youtube": "https://www.youtube.com/watch?v=KAjOOuG9h2k"
    },

    # Hip
    "hip flexor stretch": {
        "gif": "https://media.tenor.com/Keu6nO9X8vsAAAAC/hip-flexor-stretch.gif",
        "youtube": "https://www.youtube.com/watch?v=tj2dFgxYmhU"
    },
    "clamshell": {
        "gif": "https://media.tenor.com/V5zpiqD2p08AAAAC/clamshell-exercise.gif",
        "youtube": "https://www.youtube.com/watch?v=GgPBxgYDLwU"
    },

    # Knee / Leg
    "hamstring stretch": {
        "gif": "https://media.tenor.com/0ZYsacL8ZVcAAAAC/hamstring-stretch.gif",
        "youtube": "https://www.youtube.com/watch?v=2L2lnxIcNmo"
    },
    "quad stretch": {
        "gif": "https://media.tenor.com/dm6uF93z8KkAAAAC/quad-stretch.gif",
        "youtube": "https://www.youtube.com/watch?v=riEXN0TqN4o"
    },
    "wall sit": {
        "gif": "https://media.tenor.com/8mOGswULjPMAAAAC/wall-sit.gif",
        "youtube": "https://www.youtube.com/watch?v=-cdph8hv0O0"
    },
    "straight leg raise": {
        "gif": "https://media.tenor.com/8xKzL4W0LVEAAAAC/straight-leg-raise.gif",
        "youtube": "https://www.youtube.com/watch?v=q-DAkPie4-c"
    },

    # Ankle / Foot
    "ankle circles": {
        "gif": "https://media.tenor.com/jYngHUV1Gv8AAAAC/ankle-circles.gif",
        "youtube": "https://www.youtube.com/watch?v=tIR7Eu0SRek"
    },
    "calf raise": {
        "gif": "https://media.tenor.com/3rQ70YbsnxYAAAAC/calf-raise.gif",
        "youtube": "https://www.youtube.com/watch?v=-M4-G8p8fmc"
    },

    # Chest
    "chest stretch": {
        "gif": "https://media.tenor.com/NF1C1ZoM0PcAAAAC/chest-stretch.gif",
        "youtube": "https://www.youtube.com/watch?v=gLkKzA3f6zE"
    },

    # Fallback
    "stretch": {
        "gif": "https://media.tenor.com/pjwzLzj1H5oAAAAC/stretch-yoga.gif",
        "youtube": "https://www.youtube.com/watch?v=g_tea8ZNk5A"
    }
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
                st.image(media["gif"], use_container_width=True)
                st.markdown(f"[▶ Watch on YouTube]({media['youtube']})", unsafe_allow_html=True)
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
