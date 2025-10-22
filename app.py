import streamlit as st
import requests
import json

# ============================================================================
# CONFIGURATION
# ============================================================================

# OpenRouter API Configuration
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
OPENROUTER_MODEL = "openai/gpt-4o-mini"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Exercise demonstration videos - YouTube embed IDs
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
    "pendulum": "YqkXrT94rZk",
    "shoulder": "3Pp5Mckr-XE",
    
    # Elbow
    "elbow stretch": "GSK5G8BFreM",
    "elbow": "GSK5G8BFreM",
    
    # Wrist/Hand
    "wrist flexion": "mSZWSQSSEjE",
    "prayer stretch": "UrhBZKH0WH0",
    "wrist": "mSZWSQSSEjE",
    "hand": "UrhBZKH0WH0",
    
    # Hip
    "hip flexor stretch": "YQmpO9VT2X4",
    "clamshell": "bK0KuF-Bz-o",
    "hip": "YQmpO9VT2X4",
    
    # Knee
    "quad stretch": "K7L41e2I48M",
    "hamstring stretch": "PivvLRcKSqA",
    "wall sit": "y-wV4Venusw",
    "straight leg raise": "2iTI68aBLgA",
    "knee": "y-wV4Venusw",
    
    # Ankle/Foot/Shin
    "ankle circles": "JO0NKcZU0Zo",
    "calf raise": "gwLzBJYoWlI",
    "towel stretch": "gHCKT2ZLAM8",
    "ankle": "JO0NKcZU0Zo",
    "foot": "gHCKT2ZLAM8",
    "shin": "gwLzBJYoWlI",
    
    # Chest
    "chest stretch": "4iE_HL4x4IA",
    "chest": "4iE_HL4x4IA",
    
    # Jaw
    "jaw exercise": "Htofxb_KMCE",
    "jaw": "Htofxb_KMCE",
    
    # Generic fallback
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
        }
        .demo-button {
            background: #667eea;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            text-decoration: none;
            display: inline-block;
            margin-top: 10px;
            font-size: 0.9em;
        }
        </style>
    """, unsafe_allow_html=True)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_exercise_demo(exercise_name):
    """Match exercise description to appropriate demo"""
    exercise_lower = exercise_name.lower()
    
    # Try exact match first
    for key in EXERCISE_DEMOS:
        if key in exercise_lower:
            return EXERCISE_DEMOS[key]
    
    # Try partial matches for common exercises
    if "stretch" in exercise_lower:
        return EXERCISE_DEMOS["stretch"]
    elif "breath" in exercise_lower:
        return EXERCISE_DEMOS["breathing"]
    elif "bridge" in exercise_lower:
        return EXERCISE_DEMOS["bridge"]
    elif "clamshell" in exercise_lower:
        return EXERCISE_DEMOS["clamshell"]
    elif "roll" in exercise_lower and "shoulder" in exercise_lower:
        return EXERCISE_DEMOS["shoulder roll"]
    elif "raise" in exercise_lower and ("leg" in exercise_lower or "calf" in exercise_lower):
        if "calf" in exercise_lower:
            return EXERCISE_DEMOS["calf raise"]
        return EXERCISE_DEMOS["straight leg raise"]
    else:
        # Default fallback
        return EXERCISE_DEMOS["stretch"]

def get_ai_recommendations(pain_location, pain_description, intensity):
    """Call OpenRouter API to get exercise recommendations"""
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""You are a physical therapy assistant. A user has {pain_location} pain (intensity: {intensity}/10).

User description: {pain_description}

Provide 3-5 safe, gentle exercises they can try. For each exercise:
1. Give it a clear, simple name (like "Cat-Cow Stretch" or "Shoulder Rolls")
2. Provide 2-3 sentences explaining how to do it safely
3. Keep it simple and appropriate for home practice

Format your response as a JSON array like this:
[
  {{"name": "Exercise Name", "description": "How to do it safely..."}},
  {{"name": "Exercise Name 2", "description": "How to do it safely..."}}
]

Only return the JSON array, nothing else."""

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        
        # Parse the AI response
        content = result['choices'][0]['message']['content']
        # Clean up potential markdown formatting
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        exercises = json.loads(content)
        return exercises
    
    except Exception as e:
        st.error(f"Error getting recommendations: {str(e)}")
        return []

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    apply_custom_css()
    
    # Initialize session state
    if 'exercises_completed' not in st.session_state:
        st.session_state.exercises_completed = []
    if 'current_plan' not in st.session_state:
        st.session_state.current_plan = None
    
    # Header
    st.markdown("<h1 style='text-align: center; color: #667eea;'>🧘 PainRelief.AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666; font-size: 1.1em;'>Your personalized pain relief exercise companion</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Input Section
    st.markdown("<div class='section-header'>📍 Where does it hurt?</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        pain_location = st.selectbox(
            "Select pain location:",
            [
                "Lower Back",
                "Upper Back", 
                "Neck",
                "Shoulder",
                "Elbow",
                "Wrist",
                "Hand",
                "Chest",
                "Hip",
                "Knee",
                "Ankle",
                "Shin",
                "Foot",
                "Jaw",
                "Other"
            ],
            label_visibility="collapsed"
        )
    
    with col2:
        intensity = st.slider("Pain intensity", 1, 10, 5)
        st.caption(f"Level: {intensity}/10")
    
    pain_description = st.text_area(
        "Describe your pain (optional):",
        placeholder="e.g., Sharp pain when bending, stiffness in the morning...",
        height=100
    )
    
    # Generate Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✨ Get My Exercise Plan", use_container_width=True):
            with st.spinner("Creating your personalized plan..."):
                exercises = get_ai_recommendations(pain_location, pain_description, intensity)
                st.session_state.current_plan = exercises
                st.session_state.exercises_completed = []
    
    # Display Results
    if st.session_state.current_plan:
        st.markdown("<div class='section-header'>💪 Your Personalized Plan</div>", unsafe_allow_html=True)
        
        # Progress tracker
        total_exercises = len(st.session_state.current_plan)
        completed_count = len(st.session_state.exercises_completed)
        progress = completed_count / total_exercises if total_exercises > 0 else 0
        st.progress(progress)
        st.caption(f"Completed: {completed_count}/{total_exercises} exercises")
        
        # Display each exercise
        for idx, exercise in enumerate(st.session_state.current_plan):
            with st.container():
                st.markdown(f"<div class='exercise-card'>", unsafe_allow_html=True)
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"### {idx + 1}. {exercise['name']}")
                    st.write(exercise['description'])
                    
                    # Get demo info
                    demo = get_exercise_demo(exercise['name'])
                    st.markdown(f"[▶️ Watch Video Demo]({demo['video']})", unsafe_allow_html=True)
                    
                    # Completion checkbox
                    is_completed = idx in st.session_state.exercises_completed
                    if st.checkbox(f"✅ Mark as completed", key=f"check_{idx}", value=is_completed):
                        if idx not in st.session_state.exercises_completed:
                            st.session_state.exercises_completed.append(idx)
                            st.rerun()
                    else:
                        if idx in st.session_state.exercises_completed:
                            st.session_state.exercises_completed.remove(idx)
                            st.rerun()
                
                with col2:
                    # Display placeholder image
                    demo = get_exercise_demo(exercise['name'])
                    st.image(demo['image'], use_container_width=True)
                    st.caption("Click link for video demo")
                
                st.markdown("</div>", unsafe_allow_html=True)
        
        # Safety Disclaimer
        st.markdown("<div class='section-header'>⚠️ Important Safety Information</div>", unsafe_allow_html=True)
        st.markdown("""
            <div class='safety-box'>
            <strong>Please note:</strong> This tool provides general exercise suggestions and is not a substitute for professional medical advice. 
            <ul>
                <li><strong>Stop immediately</strong> if any exercise causes increased pain</li>
                <li><strong>Consult a healthcare provider</strong> for persistent or severe pain</li>
                <li><strong>Start slowly</strong> and listen to your body</li>
                <li>These exercises are for <strong>mild to moderate discomfort only</strong></li>
                <li>If symptoms worsen or persist beyond 2 weeks, seek medical attention</li>
            </ul>
            </div>
        """, unsafe_allow_html=True)
        
        # Feedback section
        if completed_count == total_exercises and total_exercises > 0:
            st.balloons()
            st.success("🎉 Great job completing your exercise plan!")
            
            st.markdown("<div class='section-header'>📊 How do you feel?</div>", unsafe_allow_html=True)
            improvement = st.slider("Rate your improvement:", 1, 10, 5, key="improvement")
            
            if improvement >= 7:
                st.success("💪 That's wonderful! Keep up the good work!")
                st.info("💡 Tip: Continue these exercises daily for lasting relief.")
            elif improvement >= 4:
                st.info("⏳ Progress takes time. Try these exercises consistently for 2 weeks.")
                st.write("Consider doing them 2-3 times per day for better results.")
            else:
                st.warning("⚕️ If pain persists or worsens, please consult a healthcare professional.")
                st.write("You may benefit from a thorough evaluation by a physical therapist or doctor.")

if __name__ == "__main__":
    main()
