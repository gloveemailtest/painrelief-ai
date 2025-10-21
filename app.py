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

# Exercise GIF/Video Mapping (royalty-free sources)
EXERCISE_GIFS = {
    # Lower Back
    "cat-cow stretch": "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExcGR5Z3o4eHE4M3FxYmR6cjB6dGE4bWV4Ym9rN3VmZ2RtZnZ3ZW5xZCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/l0HlTy9x8FZo0XO1i/giphy.gif",
    "child's pose": "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExYzJ3eGM4N3FtZnhpZ3BxdHFtZXhpOHhvZ3g5cnN5Ynd5cGQ4cWFoYSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3oKIPbLHExjDwzNnUI/giphy.gif",
    "pelvic tilt": "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExaDUxYmNkYzR6Nm5xYm5qeGQxdDN6ZW5oYm1yeGFhYnhhd3R4dHBvYyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/xT9IgG50Fb7Mi0prBC/giphy.gif",
    "knee to chest": "https://media.giphy.com/media/l0HlPystfePnYIspG/giphy.gif",
    
    # Neck
    "neck rotation": "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExeHV6bXBxZGE5NnFkYnU2OHUxemwyeG1xdGFsZzR4ZWh6ZWVtOHhoayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o6ZsYq8E24sNKYs7K/giphy.gif",
    "chin tuck": "https://media.giphy.com/media/26FPy3QZQqGtDcrja/giphy.gif",
    "side neck stretch": "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExNm5hN2h5dHBweDJ6dGY4bm0yanE4bmVxMXFhY3F0ZmtzN2NwdHQwMCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/l0HlBO7eyXzSZkJri/giphy.gif",
    
    # Shoulder
    "shoulder roll": "https://media.giphy.com/media/l0HlHFRbmaZtBRhXG/giphy.gif",
    "arm circles": "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExM2U2eGRnYmM2eXlwbnRyeGV4ZWFqdGh1M2pyanFmZHVkY3QwamRybSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3oKIPnAiaMCws8nOsE/giphy.gif",
    "cross-body stretch": "https://media.giphy.com/media/26FPqZXBqKBYVUYJG/giphy.gif",
    "wall angels": "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExNXQxZWR6ZGhvd3V6Y2RjMnhkNGJ5aXR1cWxoOG5yOHc0YzR0dGt3aSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/l0HlNQ03J5VxsuKvS/giphy.gif",
    
    # Knee
    "quad stretch": "https://media.giphy.com/media/l0HlEb3ssLNruKt32/giphy.gif",
    "hamstring stretch": "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExMnE4dGE4c2Q4dGtxZHN5dDN0YnBjY3RyZTl5dHRlaDl0OXBsZjhmZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3oKIPm1v41LsKVkqoE/giphy.gif",
    "wall sit": "https://media.giphy.com/media/26FPqAe3RcEu7GbgQ/giphy.gif",
    "straight leg raise": "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExN3Q4dDhqeGM4eXV5dGNnYTh4dHJ1dGJ6eGhhY3JhY3Q2anh5YmN6NSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/xT9IgN2fLxPaGKI5kQ/giphy.gif",
    
    # Generic fallback
    "stretch": "https://media.giphy.com/media/3oKIPlifLxdigaD2Y8/giphy.gif",
    "breathing": "https://media.giphy.com/media/krP2NRkLqnKEg/giphy.gif",
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
        </style>
    """, unsafe_allow_html=True)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_exercise_gif(exercise_name):
    """Match exercise description to appropriate GIF"""
    exercise_lower = exercise_name.lower()
    
    # Try exact match first
    for key in EXERCISE_GIFS:
        if key in exercise_lower:
            return EXERCISE_GIFS[key]
    
    # Fallback to generic
    if "stretch" in exercise_lower:
        return EXERCISE_GIFS["stretch"]
    elif "breath" in exercise_lower:
        return EXERCISE_GIFS["breathing"]
    else:
        return EXERCISE_GIFS["stretch"]  # Default

def get_ai_recommendations(pain_location, pain_description, intensity):
    """Call OpenRouter API to get exercise recommendations"""
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""You are a physical therapy assistant. A user has {pain_location} pain (intensity: {intensity}/10).
    
User description: {pain_description}

Provide 3-5 safe, gentle exercises they can try. For each exercise:
1. Give it a clear name (like "Cat-Cow Stretch" or "Shoulder Rolls")
2. Provide 2-3 sentences explaining how to do it
3. Keep it simple and safe

Format your response as a JSON array like this:
[
  {{"name": "Exercise Name", "description": "How to do it..."}},
  {{"name": "Exercise Name 2", "description": "How to do it..."}}
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
        st.session_state.exercises_completed = 0
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
                st.session_state.exercises_completed = 0
    
    # Display Results
    if st.session_state.current_plan:
        st.markdown("<div class='section-header'>💪 Your Personalized Plan</div>", unsafe_allow_html=True)
        
        # Progress tracker
        total_exercises = len(st.session_state.current_plan)
        progress = st.session_state.exercises_completed / total_exercises
        st.progress(progress)
        st.caption(f"Completed: {st.session_state.exercises_completed}/{total_exercises} exercises")
        
        # Display each exercise
        for idx, exercise in enumerate(st.session_state.current_plan):
            with st.container():
                st.markdown(f"<div class='exercise-card'>", unsafe_allow_html=True)
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"### {idx + 1}. {exercise['name']}")
                    st.write(exercise['description'])
                    
                    # Completion checkbox
                    if st.checkbox(f"✅ Completed", key=f"check_{idx}"):
                        if idx not in [i for i in range(st.session_state.exercises_completed)]:
                            st.session_state.exercises_completed += 1
                            st.rerun()
                
                with col2:
                    # Display exercise GIF
                    gif_url = get_exercise_gif(exercise['name'])
                    st.image(gif_url, use_container_width=True, caption="Demo")
                
                st.markdown("</div>", unsafe_allow_html=True)
        
        # Safety Disclaimer
        st.markdown("<div class='section-header'>⚠️ Important Safety Information</div>", unsafe_allow_html=True)
        st.markdown("""
            <div class='safety-box'>
            <strong>Please note:</strong> This tool provides general exercise suggestions and is not a substitute for professional medical advice. 
            <ul>
                <li>Stop immediately if any exercise causes increased pain</li>
                <li>Consult a healthcare provider for persistent or severe pain</li>
                <li>Start slowly and listen to your body</li>
                <li>These exercises are for mild to moderate discomfort only</li>
            </ul>
            </div>
        """, unsafe_allow_html=True)
        
        # Feedback section
        if st.session_state.exercises_completed == total_exercises:
            st.balloons()
            st.success("🎉 Great job completing your exercise plan!")
            
            st.markdown("<div class='section-header'>📊 How do you feel?</div>", unsafe_allow_html=True)
            improvement = st.slider("Rate your improvement:", 1, 10, 5, key="improvement")
            if improvement >= 7:
                st.success("That's wonderful! Keep up the good work! 💪")
            elif improvement >= 4:
                st.info("Progress takes time. Try these exercises daily for best results.")
            else:
                st.warning("If pain persists or worsens, please consult a healthcare professional.")

if __name__ == "__main__":
    main()

