import streamlit as st
import numpy as np
import joblib
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random
import time

# Page config
st.set_page_config(
    page_title="🔥 MindWell - Burnout Prevention Hub", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark/light mode and animations
def load_css():
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .burnout-low {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    .burnout-medium {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        color: #333;
    }
    .burnout-high {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
    }
    .quote-card {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #667eea;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .music-card {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .music-card:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
    }
    .breathing-circle {
        width: 200px;
        height: 200px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        margin: 2rem auto;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1.2rem;
        animation: breathe 4s ease-in-out infinite;
    }
    @keyframes breathe {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
    }
    .leaderboard-item {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: white;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .quiz-option {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    .quiz-option:hover {
        background: #e9ecef;
        border-color: #667eea;
        transform: translateX(10px);
    }
    .progress-bar {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        height: 20px;
        border-radius: 10px;
        transition: width 0.5s ease;
    }
    .dark-mode {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
if 'user_score' not in st.session_state:
    st.session_state.user_score = 0
if 'breathing_active' not in st.session_state:
    st.session_state.breathing_active = False

# Load CSS
load_css()
# --- Database Setup (SQLite) ---
conn = sqlite3.connect('burnout_app.db', check_same_thread=False)
c = conn.cursor()

# Create tables if not exist
c.execute('''
CREATE TABLE IF NOT EXISTS mood_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    date TEXT,
    mood TEXT,
    music_used INTEGER,
    journaled INTEGER,
    burnout_score REAL,
    wellness_points INTEGER
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    date TEXT,
    feedback TEXT,
    rating INTEGER
)
''')

conn.commit()

# --- Helper functions ---
def send_email_reminder(to_email):
    sender_email = "your_email@example.com"
    sender_password = "your_email_password"
    subject = "Reminder: Check Your Burnout Status Today!"
    body = "Hi! This is a friendly reminder to check your burnout levels and take care of your mental health today."

    from email.mime.text import MIMEText
    import smtplib

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Email send failed: {e}")
        return False

# Load model and scaler
@st.cache_data
def load_models():
    try:
        model = joblib.load("burnout_model.pkl")
        scaler = joblib.load("scaler.pkl")
        return model, scaler
    except:
        # Dummy fallback
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.preprocessing import StandardScaler
        model = RandomForestRegressor(n_estimators=100)
        scaler = StandardScaler()
        X_dummy = np.random.rand(100, 10)
        y_dummy = np.random.rand(100)
        scaler.fit(X_dummy)
        model.fit(scaler.transform(X_dummy), y_dummy)
        return model, scaler

model, scaler = load_models()

# Header
col1, col2, col3 = st.columns([1, 2, 1])
with col3:
    if st.button("�☀️ Toggle Theme"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

st.markdown("""
<div class="main-header">
    <h1>🔥 MindWell - Burnout Prevention Hub</h1>
    <p>Your comprehensive wellness companion for mental health and productivity</p>
</div>
""", unsafe_allow_html=True)

# Sidebar - User Input
st.sidebar.markdown("### 🧠 Personal Profile")
name = st.sidebar.text_input("Your Name", placeholder="Enter your name")
gender = st.sidebar.selectbox("Gender", ["Male", "Female", "Other"])
company_type = st.sidebar.selectbox("Company Type", ["Product", "Service", "Startup", "Corporate"])
wfh = st.sidebar.selectbox("Work from Home", ["Yes", "No", "Hybrid"])
designation = st.sidebar.slider("Career Level (0=Intern, 5=Senior)", 0, 5, 1)
resource_allocation = st.sidebar.slider("Resource Availability (1-10)", 1, 10, 5)
mental_fatigue = st.sidebar.slider("Mental Fatigue Level (0-10)", 0.0, 10.0, 5.0)
experience = st.sidebar.slider("Years of Experience", 0, 30, 2)

# Feature engineering
is_new = int(experience < 2)
gender_enc = 1 if gender == "Male" else 0
company_enc = 1 if company_type in ["Product", "Startup"] else 0
wfh_enc = 1 if wfh == "Yes" else 0
work_mode_risk = company_enc * wfh_enc
fatigue_x_resource = mental_fatigue * resource_allocation

features = np.array([[gender_enc, company_enc, wfh_enc, designation,
                      resource_allocation, mental_fatigue, experience,
                      is_new, work_mode_risk, fatigue_x_resource]])
features_scaled = scaler.transform(features)
burnout = float(model.predict(features_scaled)[0])

def interpret_burnout(score):
    if score < 0.3:
        return "Low Risk", "You're doing great! Keep maintaining your healthy work-life balance.", "burnout-low"
    elif score < 0.7:
        return "Moderate Risk", "Pay attention to stress levels. Consider wellness activities.", "burnout-medium"
    else:
        return "High Risk", "Take immediate action! Prioritize self-care and consider professional help.", "burnout-high"

risk_level, risk_message, risk_class = interpret_burnout(burnout)

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🔮 Prediction", "📝 Mood Tracker", "🎵 Music Therapy", 
    "🧘 Breathing Games", "🧠 Wellness Quiz", "🏆 Leaderboard", "💬 Feedback"
])

# Tab 1: Burnout Analysis
with tab1:
    st.markdown("## 🔮 AI-Powered Burnout Analysis")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card {risk_class}">
            <h2>Burnout Score</h2>
            <h1>{burnout:.2f}</h1>
            <p>Risk Level: {risk_level}</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        stress_factors = int(mental_fatigue + (10 - resource_allocation) + (designation * 2))
        st.markdown(f"""
        <div class="metric-card">
            <h2>Stress Factors</h2>
            <h1>{stress_factors}/20</h1>
            <p>Environmental Stressors</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        wellness_score = max(0, 100 - int(burnout * 100))
        st.markdown(f"""
        <div class="metric-card burnout-low">
            <h2>Wellness Score</h2>
            <h1>{wellness_score}/100</h1>
            <p>Overall Health Index</p>
        </div>
        """, unsafe_allow_html=True)

    # Gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=burnout,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Burnout Risk Meter", 'font': {'size': 24}},
        delta={'reference': 0.5},
        gauge={
            'axis': {'range': [None, 1], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 0.3], 'color': 'lightgreen'},
                {'range': [0.3, 0.7], 'color': 'yellow'},
                {'range': [0.7, 1], 'color': 'red'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 0.8
            }
        }
    ))
    fig.update_layout(height=400, font={'color': "darkblue", 'family': "Arial"})
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"""
    <div class="quote-card">
        <h3>🎯 Your Risk Analysis</h3>
        <p><strong>{risk_level}:</strong> {risk_message}</p>
    </div>
    """, unsafe_allow_html=True)

# Tab 7: Feedback Tab with FIXED multiselect key
with tab7:
    st.markdown("## 💬 Feedback & Daily Motivation")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### ✨ Daily Motivation")
        quotes = [
            "Your mental health is a priority.",
            "Progress, not perfection.",
            "Burnout is not a badge of honor.",
            "You are stronger than you think.",
            "Healing isn't linear."
        ]
        quote = random.choice(quotes)
        st.markdown(f"""
        <div class="quote-card">
            <p><em>"{quote}"</em></p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("### 📝 Share Your Feedback")

        feedback_rating = st.selectbox("Rate your app experience:", [
            "⭐⭐⭐⭐⭐ Excellent (5/5)",
            "⭐⭐⭐⭐ Good (4/5)", 
            "⭐⭐⭐ Average (3/5)",
            "⭐⭐ Poor (2/5)",
            "⭐ Very Poor (1/5)"
        ])

        feedback_text = st.text_area("What's working well? What could be improved?", 
                                     placeholder="Your feedback helps us improve the wellness experience...",
                                     key="feedback_text_key")

        feature_requests = st.multiselect("What features would you like to see?", [
            "🎮 Wellness games",
            "👥 Community features", 
            "📱 Mobile notifications",
            "📊 Advanced analytics",
            "🎯 Goal setting tools",
            "🏅 More achievements",
            "💬 Peer support chat",
            "📚 Wellness library"
        ], key="feature_requests_multiselect_0")  # FIXED KEY

        if st.button("Submit Feedback", type="primary"):
            if name and feedback_text:
                try:
                    rating = int(feedback_rating.split("(")[1].split("/")[0])
                    now = datetime.now().strftime("%Y-%m-%d %H:%M")

                    c.execute("""INSERT INTO feedback (user, date, rating, feedback) 
                                 VALUES (?, ?, ?, ?)""",
                              (name, now, rating, feedback_text))
                    conn.commit()

                    st.success("🙏 Thank you for your feedback! Your input helps us improve.")
                    st.balloons()

                    st.session_state.user_score += 30
                    st.info("🎉 +30 wellness points for providing feedback!")

                except Exception as e:
                    st.error(f"Error saving feedback: {e}")
            else:
                st.warning("Please enter your name and feedback before submitting.")
# Tab 2: Mood Tracker
with tab2:
    st.markdown("## 📝 Daily Wellness Journal")

    col1, col2 = st.columns(2)
    with col1:
        mood = st.radio("How are you feeling today?", [
            "😊 Energetic & Happy",
            "🙂 Good & Positive", 
            "😐 Neutral & Balanced",
            "😔 Tired & Stressed",
            "😞 Overwhelmed & Anxious"
        ])

        activities = st.multiselect("Wellness activities completed:", [
            "🎵 Listened to calming music",
            "✍️ Journaled thoughts",
            "🧘 Meditation/Breathing exercises",
            "🚶 Physical exercise",
            "👥 Social interaction",
            "📚 Learning/Reading",
            "🌿 Time in nature"
        ], key="wellness_activities_multiselect")

        energy_level = st.slider("Energy Level (1-10)", 1, 10, 5)
        sleep_quality = st.slider("Sleep Quality (1-10)", 1, 10, 7)

    with col2:
        st.markdown("### 💭 Quick Reflection")
        reflection = st.text_area("What's on your mind today?", placeholder="Write something here...")
        gratitude = st.text_input("One thing you're grateful for today:")
        tomorrow_goal = st.text_input("One goal for tomorrow:")

    if st.button("📊 Log Today's Entry", type="primary"):
        if not name.strip():
            st.warning("⚠️ Please enter your name in the sidebar first!")
        else:
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            activity_score = len(activities) * 10

            c.execute("""INSERT INTO mood_logs 
                         (user, date, mood, burnout_score, music_used, journaled, wellness_points)
                         VALUES (?, ?, ?, ?, ?, ?, ?)""",
                      (name, now, mood, float(burnout), 
                       int("🎵 Listened to calming music" in activities),
                       int("✍️ Journaled thoughts" in activities),
                       activity_score))
            conn.commit()

            st.session_state.user_score += activity_score
            st.success(f"✅ Entry logged! You earned {activity_score} wellness points!")

# Tab 3: Music Therapy
import streamlit.components.v1 as components

with tab3:
    st.markdown("## 🎵 Therapeutic Music Playlists")

    playlists = {
        "🎹 Charlie Puth Chill": {
            "description": "Smooth vocals and melodic beats for relaxation",
            "spotify": "https://open.spotify.com/embed/playlist/37i9dQZF1DZ06evO4nQvxI"
        },
        "💃 Shakira Energy Boost": {
            "description": "Latin rhythms to energize and motivate",
            "spotify": "https://open.spotify.com/embed/playlist/37i9dQZF1DX3NRlBO7Wj57"
        },
        "🎤 Diljit Dosanjh Vibes": {
            "description": "Punjabi beats for positivity and joy",
            "spotify": "https://open.spotify.com/embed/playlist/37i9dQZF1DWSV3Tk4GO2fq"
        },
        "🧘 Meditation & Focus": {
            "description": "Ambient sounds for deep concentration",
            "spotify": "https://open.spotify.com/embed/playlist/37i9dQZF1DWZeKCadgRdKQ"
        },
        "💪 Workout Motivation": {
            "description": "High-energy tracks for exercise",
            "spotify": "https://open.spotify.com/embed/playlist/37i9dQZF1DX70RN3TfWWJh"
        }
    }

    col1, col2 = st.columns(2)
    for i, (playlist_name, details) in enumerate(playlists.items()):
        col = col1 if i % 2 == 0 else col2
        with col:
            st.markdown(f"""
            <div class="music-card">
                <h3>{playlist_name}</h3>
                <p>{details['description']}</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"🎧 Play {playlist_name}", key=f"play_{i}"):
                st.success(f"🎵 Now playing: {playlist_name}")
                components.iframe(details["spotify"], height=380, width=300, scrolling=False)
                if name:
                    st.session_state.user_score += 15
                    st.info("🎉 +15 wellness points for music therapy!")

# Tab 4: Breathing Games
with tab4:
    st.markdown("## 🧘 Interactive Breathing Exercises")

    breathing_type = st.selectbox("Choose your breathing technique:", [
        "🌊 4-7-8 Relaxation Breathing",
        "⚡ Box Breathing (4-4-4-4)",
        "🧘 Triangle Breathing (4-4-4)",
        "💪 Energizing Breath (2-1-4-1)"
    ])

    session_duration = st.slider("Session Duration (minutes)", 1, 10, 3)

    if st.button("🎯 Start Breathing Session"):
        st.markdown("""
        <div class="breathing-circle">
            <div style="text-align: center;">
                <h3>Breathe</h3>
                <p>Follow the rhythm</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.success("🎉 Great job! Breathing session completed.")
        st.session_state.user_score += 25
        st.info("🎉 +25 points for breathing!")
# Tab 5: Wellness Quiz
with tab5:
    st.markdown("## 🧠 Wellness Knowledge Quiz")

    quiz_questions = [
        {
            "question": "What percentage of workplace stress is preventable through proper wellness practices?",
            "options": ["25%", "50%", "75%", "90%"],
            "correct": 2
        },
        {
            "question": "How many minutes of daily meditation can significantly reduce burnout?",
            "options": ["5 minutes", "10 minutes", "20 minutes", "60 minutes"],
            "correct": 1
        }
    ]

    if 'quiz_score' not in st.session_state:
        st.session_state.quiz_score = 0
        st.session_state.quiz_index = 0

    if st.session_state.quiz_index < len(quiz_questions):
        q = quiz_questions[st.session_state.quiz_index]
        st.markdown(f"### Q{st.session_state.quiz_index+1}: {q['question']}")
        answer = st.radio("Choose one:", q["options"], key=f"quiz_q_{st.session_state.quiz_index}")

        if st.button("Submit Answer", key=f"submit_q_{st.session_state.quiz_index}"):
            selected_idx = q["options"].index(answer)
            if selected_idx == q["correct"]:
                st.success("✅ Correct!")
                st.session_state.quiz_score += 10
            else:
                st.error("❌ Incorrect.")
            st.session_state.quiz_index += 1
            st.rerun()
    else:
        st.success(f"🎉 Quiz Complete! Score: {st.session_state.quiz_score} pts")
        st.session_state.user_score += st.session_state.quiz_score
        if st.button("Restart Quiz"):
            st.session_state.quiz_score = 0
            st.session_state.quiz_index = 0
            st.rerun()

# Tab 6: Leaderboard
with tab6:
    st.markdown("## 🏆 Wellness Leaderboard")

    c.execute("SELECT user, SUM(wellness_points) as points FROM mood_logs GROUP BY user ORDER BY points DESC LIMIT 5")
    rows = c.fetchall()

    if rows:
         keycap_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

         for i, (username, points) in enumerate(rows):
              if i < 5:
                 rank = ["🥇", "🥈", "🥉", "🎖", "🏅"][i]
              elif i < 10:
                 rank = keycap_emojis[i]  # safe emoji for ranks 6 to 10
              else:
                 rank = f"{i+1}"  # fallback to plain number string for 11+

              st.markdown(f"""
 <div class="leaderboard-item">
    <div>
        <strong>{rank} {username}</strong><br>
        <small>Total Wellness Points</small>
    </div>
    <div style="text-align: right;">
        <strong>{points} pts</strong>
    </div>
 </div>
 """, unsafe_allow_html=True)

        
    else:
        st.info("No leaderboard data available yet.")

# Sidebar Stats
st.sidebar.markdown("### 🎯 Quick Stats")
if name:
    st.sidebar.metric("Your Wellness Points", st.session_state.user_score)
    st.sidebar.metric("Current Burnout Risk", f"{burnout:.1%}")

    next_level = ((st.session_state.user_score // 100) + 1) * 100
    progress = (st.session_state.user_score % 100) / 100
    st.sidebar.progress(progress)
    st.sidebar.caption(f"Progress to next level: {st.session_state.user_score % 100}/100")

st.sidebar.markdown("### 💡 Daily Tip")
daily_tips = [
    "Take a 2-minute breathing break every hour",
    "Practice gratitude - write down 3 things you're thankful for",
    "Stretch your body to release tension",
    "Drink water regularly",
    "Step outside for natural light"
]
st.sidebar.info(random.choice(daily_tips))

# Final save to DB
if name and st.session_state.user_score > 0:
    try:
        c.execute("""INSERT INTO user_scores (user, total_score) 
                     VALUES (?, ?)
                     ON CONFLICT(user) DO UPDATE SET total_score = excluded.total_score""",
                  (name, st.session_state.user_score))
        conn.commit()
    except Exception as e:
        st.warning(f"Could not save score: {e}")

