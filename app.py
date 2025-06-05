import streamlit as st
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import time
import sqlite3
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
import sqlite3
from datetime import datetime, timedelta
import time
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import random
import streamlit as st
import sqlite3
from datetime import datetime, timedelta
import time
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import random

# --- Load model and scaler ---
model = joblib.load('burnout_model.pkl')
scaler = joblib.load('scaler.pkl')

st.set_page_config(page_title="🔥 Microburnout Detection Dashboard", layout="wide")
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

def toggle_dark_mode():
    st.session_state.dark_mode = not st.session_state.dark_mode

# Dark mode CSS
if st.session_state.dark_mode:
    st.markdown("""
    <style>
    .stApp {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    .sidebar .sidebar-content {
        background-color: #2d2d2d;
    }
    .stSelectbox > div > div {
        background-color: #3d3d3d;
        color: #ffffff;
    }
    .stTextInput > div > div > input {
        background-color: #3d3d3d;
        color: #ffffff;
    }
    .stTextArea > div > div > textarea {
        background-color: #3d3d3d;
        color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

# Dark mode toggle button in sidebar
st.sidebar.button(
    "🌙 Dark Mode" if not st.session_state.dark_mode else "☀️ Light Mode", 
    on_click=toggle_dark_mode,
    key="dark_mode_toggle"
)

# --- Database Setup (SQLite) ---
conn = sqlite3.connect('burnout_app.db', check_same_thread=False)
c = conn.cursor()


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
    feedback TEXT
)
''')

conn.commit()

# --- Helper functions ---

def send_email_reminder(to_email):
    # NOTE: For actual email sending, you must fill in your SMTP credentials
    # This is a prototype function. Don't expose credentials in production!
    sender_email = "your_email@example.com"
    sender_password = "your_email_password"
    subject = "Reminder: Check Your Burnout Status Today!"
    body = "Hi! This is a friendly reminder to check your burnout levels and take care of your mental health today. Visit the burnout app to log your mood and activities."

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

def burnout_explanation(score):
    if score < 0.4:
        return "Low risk of burnout. Your work-life balance looks healthy."
    elif score < 0.7:
        return "Moderate risk of burnout. Be mindful and take preventive measures."
    else:
        return "High risk of burnout. Please prioritize your well-being urgently."

def get_mood_bar_color(gender, burnout_score):
    if gender == "Male":
        if burnout_score < 0.4:
            return "green"
        elif burnout_score < 0.7:
            return "orange"
        else:
            return "red"
    else:  # Female
        if burnout_score < 0.4:
            return "pink"
        elif burnout_score < 0.7:
            return "orange"
        else:
            return "red"

def get_avatar(gender, mood):
    base = "👨" if gender == "Male" else "👩"
    mood_emoji = {"😊 Happy": "😄", "😐 Neutral": "😐", "😞 Stressed": "😟"}
    return base + mood_emoji.get(mood, "")

def wellness_badge(points):
    if points >= 20:
        return "🏆 Wellness Master"
    elif points >= 10:
        return "🌟 Wellness Pro"
    elif points >= 5:
        return "👍 Wellness Beginner"
    else:
        return "🙂 Keep Going"


# --- Sidebar - User Inputs ---
st.sidebar.header("🧠 Enter Employee Info")


user_name = st.sidebar.text_input("Enter your name or nickname:", key="user_name")
gender = st.sidebar.selectbox("Gender", ["Male", "Female"], key="gender")
company_type = st.sidebar.selectbox("Company Type", ["Product", "Service"], key="company_type")
wfh = st.sidebar.selectbox("WFH Setup Available", ["Yes", "No"], key="wfh")
designation = st.sidebar.slider("Designation Level (0=Intern, 5=Senior)", 0, 5, 1, key="designation")
resource_allocation = st.sidebar.slider("Resource Allocation (1-10)", 1, 10, 5, key="resource_allocation")
mental_fatigue = st.sidebar.slider("Mental Fatigue Score (0-10)", 0.0, 10.0, 5.0, key="mental_fatigue")
experience = st.sidebar.slider("Experience (Years)", 0, 30, 2, key="experience")

# Feature engineering
is_new = int(experience < 2)
gender_enc = 1 if gender == "Male" else 0
company_type_enc = 1 if company_type == "Product" else 0
wfh_enc = 1 if wfh == "Yes" else 0
work_mode_risk = company_type_enc * wfh_enc
fatigue_x_resource = mental_fatigue * resource_allocation

# Prepare feature vector and scale
features = np.array([[gender_enc, company_type_enc, wfh_enc, designation,
                      resource_allocation, mental_fatigue, experience,
                      is_new, work_mode_risk, fatigue_x_resource]])
features_scaled = scaler.transform(features)

# Predict burnout
burnout = model.predict(features_scaled)[0]

st.title("🔥 Microburnout Detection Dashboard")
st.markdown("Use this app to predict potential burnout levels and visualize mood-energy status.")

import random

# Enhanced motivational quotes with categories
motivational_quotes = [
    {
        "quote": "Take rest; a field that has rested gives a bountiful crop.",
        "author": "Ovid",
        "category": "Rest & Recovery",
        "color": "#4CAF50"  # Green
    },
    {
        "quote": "Almost everything will work again if you unplug it for a few minutes, including you.",
        "author": "Anne Lamott",
        "category": "Self-Care",
        "color": "#2196F3"  # Blue
    },
    {
        "quote": "Self-care is how you take your power back.",
        "author": "Lalah Delia",
        "category": "Empowerment",
        "color": "#FF9800"  # Orange
    },
    {
        "quote": "You don't have to control your thoughts. You just have to stop letting them control you.",
        "author": "Dan Millman",
        "category": "Mindfulness",
        "color": "#9C27B0"  # Purple
    },
    {
        "quote": "Your mind is a garden, your thoughts are the seeds. You can grow flowers or you can grow weeds.",
        "author": "William Wordsworth",
        "category": "Mental Health",
        "color": "#E91E63"  # Pink
    },
    {
        "quote": "Progress, not perfection, is the goal.",
        "author": "Unknown",
        "category": "Growth",
        "color": "#00BCD4"  # Cyan
    }
]

# Select a random quote
daily_quote = random.choice(motivational_quotes)

# Create attractive quote display with custom CSS
st.markdown("""
<style>
.quote-container {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 25px;
    border-radius: 15px;
    margin: 20px 0;
    box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
    backdrop-filter: blur(4px);
    border: 1px solid rgba(255, 255, 255, 0.18);
}

.quote-text {
    font-size: 1.3em;
    font-style: italic;
    color: white;
    text-align: center;
    line-height: 1.6;
    margin-bottom: 15px;
    font-family: 'Georgia', serif;
}

.quote-author {
    text-align: center;
    color: #f0f0f0;
    font-weight: bold;
    font-size: 1.1em;
    margin-bottom: 10px;
}

.quote-category {
    text-align: center;
    background: rgba(255, 255, 255, 0.2);
    color: white;
    padding: 5px 15px;
    border-radius: 20px;
    display: inline-block;
    font-size: 0.9em;
    margin: 0 auto;
}

.quote-header {
    text-align: center;
    color: #4a4a4a;
    font-size: 1.2em;
    margin-bottom: 10px;
    font-weight: 600;
}

.quote-emoji {
    font-size: 2em;
    text-align: center;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

# Display the enhanced quote
st.markdown(f"""
<div class="quote-header">
    ✨ Daily Inspiration ✨
</div>
<div class="quote-container">
    <div class="quote-emoji">💫</div>
    <div class="quote-text">
        "{daily_quote['quote']}"
    </div>
    <div class="quote-author">
        — {daily_quote['author']}
    </div>
    <div style="text-align: center;">
        <span class="quote-category">{daily_quote['category']}</span>
    </div>
</div>
""", unsafe_allow_html=True)



# Replace your existing burnout display section with this enhanced version:

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Enhanced burnout display with mesmerizing visuals
def create_burnout_gauge(burnout_score, gender):
    """Create an animated gauge chart for burnout visualization"""
    
    # Color scheme based on burnout level and gender
    if gender == "Male":
        colors = ["#00ff88", "#ffaa00", "#ff4444"] if burnout_score < 0.4 else ["#ffaa00", "#ff4444", "#cc0000"] if burnout_score < 0.7 else ["#ff4444", "#cc0000", "#880000"]
    else:
        colors = ["#ff69b4", "#ffaa00", "#ff4444"] if burnout_score < 0.4 else ["#ffaa00", "#ff4444", "#cc0000"] if burnout_score < 0.7 else ["#ff4444", "#cc0000", "#880000"]
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = burnout_score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "🔥 Burnout Intensity Level", 'font': {'size': 24, 'color': 'white'}},
        delta = {'reference': 0.5, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
        gauge = {
            'axis': {'range': [None, 1], 'tickcolor': "white", 'tickfont': {'color': 'white'}},
            'bar': {'color': colors[1], 'thickness': 0.8},
            'bgcolor': "rgba(0,0,0,0.1)",
            'borderwidth': 3,
            'bordercolor': colors[0],
            'steps': [
                {'range': [0, 0.4], 'color': "rgba(0, 255, 136, 0.3)"},
                {'range': [0.4, 0.7], 'color': "rgba(255, 170, 0, 0.3)"},
                {'range': [0.7, 1], 'color': "rgba(255, 68, 68, 0.3)"}],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': burnout_score}
        }))
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "white", 'family': "Arial Black"},
        height=400,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig

def create_energy_ring(burnout_score, gender):
    """Create animated energy ring visualization"""
    
    # Calculate energy levels (inverse of burnout)
    energy_level = 1 - burnout_score
    mental_energy = max(0.1, energy_level + np.random.normal(0, 0.1))
    physical_energy = max(0.1, energy_level + np.random.normal(0, 0.15))
    emotional_energy = max(0.1, energy_level + np.random.normal(0, 0.12))
    
    categories = ['Mental Energy', 'Physical Energy', 'Emotional Energy', 'Mental Energy']
    values = [mental_energy, physical_energy, emotional_energy, mental_energy]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(0, 255, 136, 0.4)' if energy_level > 0.6 else 'rgba(255, 170, 0, 0.4)' if energy_level > 0.3 else 'rgba(255, 68, 68, 0.4)',
        line=dict(color='white', width=3),
        name='Current Energy'
    ))
    
    # Add optimal energy reference
    fig.add_trace(go.Scatterpolar(
        r=[1, 1, 1, 1],
        theta=categories,
        fill='toself',
        fillcolor='rgba(255, 255, 255, 0.1)',
        line=dict(color='rgba(255, 255, 255, 0.5)', width=2, dash='dash'),
        name='Optimal Energy'
    ))
    
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0.1)",
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                gridcolor="rgba(255, 255, 255, 0.3)",
                tickfont=dict(color='white')
            ),
            angularaxis=dict(
                gridcolor="rgba(255, 255, 255, 0.3)",
                tickfont=dict(color='white', size=12)
            )
        ),
        showlegend=True,
        legend=dict(font=dict(color='white')),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color='white'),
        height=400,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    return fig

def create_mood_wave(burnout_score):
    """Create animated wave visualization for mood flow"""
    
    x = np.linspace(0, 4*np.pi, 100)
    
    # Base wave affected by burnout
    base_amplitude = 1 - burnout_score
    wave1 = base_amplitude * np.sin(x + np.pi/4) * np.exp(-0.1*x)
    wave2 = (base_amplitude * 0.7) * np.sin(2*x + np.pi/2) * np.exp(-0.05*x)
    combined_wave = wave1 + wave2
    
    fig = go.Figure()
    
    # Add flowing wave
    fig.add_trace(go.Scatter(
        x=x, y=combined_wave,
        mode='lines',
        line=dict(
            color='rgba(0, 255, 200, 0.8)',
            width=4,
            shape='spline'
        ),
        fill='tonexty',
        fillcolor='rgba(0, 255, 200, 0.2)',
        name='Mood Flow'
    ))
    
    # Add baseline
    fig.add_trace(go.Scatter(
        x=x, y=np.zeros_like(x),
        mode='lines',
        line=dict(color='rgba(255, 255, 255, 0.3)', width=1),
        showlegend=False
    ))
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=150,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False
    )
    
    return fig

# Enhanced main display section
st.markdown("""
<div style="
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 30px;
    border-radius: 20px;
    margin: 20px 0;
    box-shadow: 0 20px 40px rgba(0,0,0,0.3);
    border: 2px solid rgba(255, 255, 255, 0.1);
">
    <h2 style="
        color: white;
        text-align: center;
        font-size: 2.5em;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        margin-bottom: 0;
        animation: glow 2s ease-in-out infinite alternate;
    ">
        ✨ Your Burnout Analysis ✨
    </h2>
</div>

<style>
@keyframes glow {
    from { text-shadow: 2px 2px 4px rgba(0,0,0,0.5), 0 0 10px rgba(255,255,255,0.5); }
    to { text-shadow: 2px 2px 4px rgba(0,0,0,0.5), 0 0 20px rgba(255,255,255,0.8), 0 0 30px rgba(255,255,255,0.6); }
}
</style>
""", unsafe_allow_html=True)

# Burnout score display with pulsing effect
burnout_status = "Stable 🌱" if burnout < 0.4 else "Warning ⚠️" if burnout < 0.7 else "Critical 🚨"
status_color = "#00ff88" if burnout < 0.4 else "#ffaa00" if burnout < 0.7 else "#ff4444"

st.markdown(f"""
<div style="
    background: linear-gradient(45deg, rgba(0,0,0,0.8), rgba(50,50,50,0.8));
    padding: 25px;
    border-radius: 15px;
    text-align: center;
    margin: 20px 0;
    border: 3px solid {status_color};
    box-shadow: 0 0 30px rgba(255,255,255,0.1);
    animation: pulse 2s infinite;
">
    <h3 style="color: white; margin: 0;">🔥 Burnout Intensity</h3>
    <h1 style="
        color: {status_color};
        font-size: 4em;
        margin: 10px 0;
        text-shadow: 0 0 20px {status_color};
        font-weight: bold;
    ">{burnout:.2f}</h1>
    <h2 style="color: white; margin: 0;">Status: {burnout_status}</h2>
    <p style="color: #ccc; margin-top: 15px; font-style: italic;">
        {burnout_explanation(burnout)}
    </p>
</div>

<style>
@keyframes pulse {{
    0% {{ box-shadow: 0 0 30px rgba(255,255,255,0.1); }}
    50% {{ box-shadow: 0 0 50px {status_color}40; }}
    100% {{ box-shadow: 0 0 30px rgba(255,255,255,0.1); }}
}}
</style>
""", unsafe_allow_html=True)

# Create three columns for different visualizations
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🎯 Burnout Gauge")
    gauge_fig = create_burnout_gauge(burnout, gender)
    st.plotly_chart(gauge_fig, use_container_width=True)

with col2:
    st.markdown("### ⚡ Energy Ring")
    ring_fig = create_energy_ring(burnout, gender)
    st.plotly_chart(ring_fig, use_container_width=True)

with col3:
    st.markdown("### 🌊 Mood Flow")
    wave_fig = create_mood_wave(burnout)
    st.plotly_chart(wave_fig, use_container_width=True)
    
    # Add breathing visualization
    st.markdown("### 🧘 Breathe")
    if burnout > 0.5:
        st.markdown("""
        <div style="
            width: 100px;
            height: 100px;
            border-radius: 50%;
            background: radial-gradient(circle, #ff6b6b, #4ecdc4);
            margin: 20px auto;
            animation: breathe 4s ease-in-out infinite;
        "></div>
        
        <style>
        @keyframes breathe {
            0%, 100% { transform: scale(1); opacity: 0.8; }
            50% { transform: scale(1.2); opacity: 1; }
        }
        </style>
        """, unsafe_allow_html=True)
        st.caption("Follow the breathing circle")

# Add animated recommendations based on burnout level
st.markdown("---")

if burnout < 0.4:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 20px 0;
    ">
        <h3>🌟 Excellent Balance! Keep Shining!</h3>
        <p>Your energy levels are optimal. Maintain this great momentum!</p>
    </div>
    """, unsafe_allow_html=True)
elif burnout < 0.7:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 20px;
        border-radius: 15px;
        color: #8B4513;
        text-align: center;
        margin: 20px 0;
        animation: gentle-pulse 3s infinite;
    ">
        <h3>⚠️ Moderate Risk - Time for Self-Care</h3>
        <p>Consider taking breaks and practicing mindfulness techniques.</p>
    </div>
    
    <style>
    @keyframes gentle-pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        padding: 20px;
        border-radius: 15px;
        color: #8B0000;
        text-align: center;
        margin: 20px 0;
        animation: urgent-pulse 1.5s infinite;
        border: 2px solid #ff4444;
    ">
        <h3>🚨 High Risk - Immediate Action Needed!</h3>
        <p>Please prioritize your well-being and consider seeking support.</p>
    </div>
    
    <style>
    @keyframes urgent-pulse {
        0%, 100% { transform: scale(1); box-shadow: 0 0 20px rgba(255, 68, 68, 0.3); }
        50% { transform: scale(1.05); box-shadow: 0 0 30px rgba(255, 68, 68, 0.6); }
    }
    </style>
    """, unsafe_allow_html=True)# --- Daily Mood & Coping Section ---
# --- Enhanced Colorful Mood & Coping Section ---
import streamlit as st
from datetime import datetime

# Custom CSS for colorful styling
st.markdown("""
<style>
.mood-container {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 20px;
    margin: 1rem 0;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.2);
}

.mood-title {
    color: white;
    text-align: center;
    font-size: 2rem;
    margin-bottom: 1.5rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    animation: glow 2s ease-in-out infinite alternate;
}

@keyframes glow {
    from { text-shadow: 2px 2px 4px rgba(0,0,0,0.3), 0 0 10px rgba(255,255,255,0.2); }
    to { text-shadow: 2px 2px 4px rgba(0,0,0,0.3), 0 0 20px rgba(255,255,255,0.4); }
}

.mood-card {
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    padding: 1.5rem;
    margin: 1rem 0;
    border: 1px solid rgba(255,255,255,0.2);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.mood-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.2);
}

.avatar-display {
    text-align: center;
    font-size: 4rem;
    margin: 1rem 0;
    padding: 1rem;
    background: rgba(255,255,255,0.1);
    border-radius: 50%;
    width: 100px;
    height: 100px;
    margin: 1rem auto;
    display: flex;
    align-items: center;
    justify-content: center;
    animation: bounce 2s infinite;
}

@keyframes bounce {
    0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
    40% { transform: translateY(-10px); }
    60% { transform: translateY(-5px); }
}

.coping-section {
    background: linear-gradient(45deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%);
    padding: 1.5rem;
    border-radius: 15px;
    margin: 1rem 0;
    box-shadow: 0 6px 20px rgba(255,154,158,0.3);
}

.companion-section {
    background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
    padding: 1.5rem;
    border-radius: 15px;
    margin: 1rem 0;
    text-align: center;
    box-shadow: 0 6px 20px rgba(168,237,234,0.3);
}

.log-button {
    background: linear-gradient(45deg, #ff6b6b, #feca57);
    color: white;
    border: none;
    padding: 1rem 2rem;
    border-radius: 25px;
    font-size: 1.2rem;
    font-weight: bold;
    cursor: pointer;
    box-shadow: 0 6px 20px rgba(255,107,107,0.4);
    transition: all 0.3s ease;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { box-shadow: 0 6px 20px rgba(255,107,107,0.4); }
    50% { box-shadow: 0 8px 25px rgba(255,107,107,0.6); }
    100% { box-shadow: 0 6px 20px rgba(255,107,107,0.4); }
}

.wellness-badge {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem;
    border-radius: 15px;
    text-align: center;
    font-size: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 8px 25px rgba(102,126,234,0.4);
    animation: shimmer 3s ease-in-out infinite;
}

@keyframes shimmer {
    0% { background-position: -200px 0; }
    100% { background-position: 200px 0; }
}

.progress-container {
    background: rgba(255,255,255,0.1);
    border-radius: 10px;
    padding: 1rem;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# Main mood container
st.markdown('<div class="mood-container">', unsafe_allow_html=True)
st.markdown('<h2 class="mood-title">✨How are you feeling today? Your mental health matters!💙✨</h2>', unsafe_allow_html=True)

# Mood selection with enhanced styling
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="mood-card">', unsafe_allow_html=True)
    if st.button("😊 Happy", key="happy_mood", help="Feeling great today!"):
        st.session_state.mood_today = "😊 Happy"
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="mood-card">', unsafe_allow_html=True)
    if st.button("😐 Neutral", key="neutral_mood", help="Just an okay day"):
        st.session_state.mood_today = "😐 Neutral"
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="mood-card">', unsafe_allow_html=True)
    if st.button("😞 Stressed", key="stressed_mood", help="Feeling overwhelmed"):
        st.session_state.mood_today = "😞 Stressed"
    st.markdown('</div>', unsafe_allow_html=True)

# Initialize mood if not set
if 'mood_today' not in st.session_state:
    st.session_state.mood_today = "😐 Neutral"

mood_today = st.session_state.mood_today

# Avatar display with animation
avatar = get_avatar(gender, mood_today)
st.markdown(f'<div class="avatar-display">{avatar}</div>', unsafe_allow_html=True)

# Coping activities section
st.markdown('<div class="coping-section">', unsafe_allow_html=True)
st.markdown("### 🎯 Your Wellness Activities Today")

col1, col2 = st.columns(2)
with col1:
    music_used = st.checkbox("🎵 Listened to calming music", help="Music can reduce stress hormones!")
with col2:
    journaled = st.checkbox("✍️ Journaled my thoughts", help="Writing helps process emotions!")

st.markdown('</div>', unsafe_allow_html=True)

mood_score = {"😊 Happy": 0, "😐 Neutral": 1, "😞 Stressed": 2}[mood_today]
coping_effort = int(music_used) + int(journaled)

# Mood companion section with enhanced styling
st.markdown('<div class="companion-section">', unsafe_allow_html=True)
st.markdown("#### 🐾 Your Mood Companion Today")

if mood_today == "😊 Happy":
    st.image("https://media.giphy.com/media/l4FGuhL4U2WyjdkaY/giphy.gif", width=200)
    st.markdown("**Your happy companion is here to celebrate with you! 🎉**")
elif mood_today == "😐 Neutral":
    st.image("https://media.giphy.com/media/xT0xeJpnrWC4XWblEk/giphy.gif", width=200)
    st.markdown("**Your chill companion is keeping you company 😌**")
else:
    st.image("https://media.giphy.com/media/xT5LMzIK1AdZJPRLqQ/giphy.gif", width=200)
    st.markdown("**Your support companion is here to comfort you 🤗**")

st.markdown('</div>', unsafe_allow_html=True)

# Enhanced coping nudges with colorful alerts
if burnout < 0.4:
    if mood_score == 0:
        st.success("🌟 You're doing fantastic! Keep shining bright like a star! ✨")
    elif mood_score == 1:
        st.info("🌿 You're stable overall. Keep nurturing those positive habits! 🌱")
    else:
        st.warning("🧘 Stress is felt but manageable. Try mindfulness or talk it out! 💬")
elif burnout < 0.7:
    if mood_score == 0:
        st.info("⚠️ Energy dipping but mood good. Rest when your body asks for it! 😴")
    elif mood_score == 1:
        st.warning("⚡ Signs of fatigue and neutral mood. Time for coping techniques! 🛠️")
    else:
        st.error("🚨 Burnout risk rising with stress. Prioritize self-care immediately! 💆‍♀️")
else:
    st.error("🆘 High burnout risk! Take immediate action and seek support! 🤝")

# Enhanced suggestions with colorful presentation
if coping_effort == 0:
    st.markdown("""
    <div style="background: linear-gradient(45deg, #ffb3ba, #ffdfba); padding: 1.5rem; border-radius: 15px; margin: 1rem 0;">
    <h4>🎯 It seems like you haven't tried calming techniques today. Here are some magical ideas:</h4>
    <ul>
    <li><strong>✍️ Journaling</strong> prompts: <em>"What are 3 things I'm grateful for today?"</em></li>
    <li><strong>🎵 Calming music</strong> playlists on Spotify:</li>
        <ul>
        <li><a href="https://open.spotify.com/playlist/37i9dQZF1DXcF6B6QPhFDv">🎤 Charlie Puth Vibes</a></li>
        <li><a href="https://open.spotify.com/playlist/37i9dQZF1DX1Xf9nqxkd4H">🎶 Diljit Dosanjh Hits</a></li>
        </ul>
    </ul>
    <p><strong>💪 Small efforts build big resilience! You've got this!</strong></p>
    </div>
    """, unsafe_allow_html=True)
elif coping_effort == 1:
    st.markdown("""
    <div style="background: linear-gradient(45deg, #baffc9, #bae1ff); padding: 1.5rem; border-radius: 15px; margin: 1rem 0;">
    <h4>🎉 Good job taking one positive step today!</h4>
    <p><strong>Keep building on these amazing habits! You're on the right track! 🚀</strong></p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="background: linear-gradient(45deg, #c1fba4, #a8e6cf); padding: 1.5rem; border-radius: 15px; margin: 1rem 0;">
    <h4>🌟 Fantastic! You're actively managing your stress!</h4>
    <p><strong>💚 You're using healthy practices to stay balanced. Keep up this incredible work!</strong></p>
    </div>
    """, unsafe_allow_html=True)

# Enhanced log button
st.markdown('<br>', unsafe_allow_html=True)
if st.button("🌈 Log Today's Mood & Wellness Journey", key="log_mood_enhanced"):
    if not user_name.strip():
        st.warning("🔤 Please enter your name in the sidebar before logging your journey!")
    else:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        wellness_points_today = coping_effort
        c.execute('''
            INSERT INTO mood_logs (user, date, mood, music_used, journaled, burnout_score, wellness_points)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_name, now, mood_today, int(music_used), int(journaled), burnout, wellness_points_today))
        conn.commit()
        st.balloons()
        st.success("✨ Your wellness journey has been logged! You're building amazing habits! 🎯")

st.markdown('</div>', unsafe_allow_html=True)

# --- Enhanced Wellness Badge Section ---
c.execute("SELECT SUM(wellness_points) FROM mood_logs WHERE user = ?", (user_name,))
result = c.fetchone()
total_points = result[0] if result[0] else 0

st.markdown(f"""
<div class="wellness-badge">
    <h3>🏆 Your Wellness Badge: {wellness_badge(total_points)} 🏆</h3>
    <p>Total Wellness Points: <strong>{total_points}</strong></p>
</div>
""", unsafe_allow_html=True)

# Enhanced progress bar
points_for_next = {0:5, 5:10, 10:20, 20:20}
for threshold in sorted(points_for_next.keys(), reverse=True):
    if total_points >= threshold:
        next_target = points_for_next[threshold]
        break

progress = min(total_points / next_target, 1.0)

st.markdown('<div class="progress-container">', unsafe_allow_html=True)
st.markdown("### 🎯 Progress to Next Badge")
st.progress(progress)
st.markdown(f"**{total_points}/{next_target} points** - Keep going! You're doing amazing! 🚀")
st.markdown('</div>', unsafe_allow_html=True)

# Celebration for badge achievements
if total_points in [5, 10, 20]:
    st.balloons()
    st.success(f"🎉 Congratulations {user_name}! You've unlocked the {wellness_badge(total_points)} badge! 🏆")
    st.markdown("""
    <div style="background: linear-gradient(45deg, #ffd700, #ffed4e); padding: 1rem; border-radius: 15px; text-align: center; margin: 1rem 0;">
    <h2>🎊 ACHIEVEMENT UNLOCKED! 🎊</h2>
    <p style="font-size: 1.2rem;">You're building incredible wellness habits!</p>
    </div>
    """, unsafe_allow_html=True)# Progress bar to next badge
points_for_next = {0:5, 5:10, 10:20, 20:20}
for threshold in sorted(points_for_next.keys(), reverse=True):
    if total_points >= threshold:
        next_target = points_for_next[threshold]
        break
progress = min(total_points / next_target, 1.0)
st.progress(progress)
st.write(f"Progress to next badge: {total_points}/{next_target} points")
# Add this after a successful log OR wellness badge display
if total_points in [5, 10, 20]:
    st.balloons()
    st.toast(f"🎉 Congrats {user_name}, you've unlocked the {wellness_badge(total_points)} badge!")


# --- Show Mood & Burnout History Chart for current user ---
c.execute('SELECT date, mood, burnout_score FROM mood_logs WHERE user = ? ORDER BY date ASC', (user_name,))
rows = c.fetchall()
if rows:
    df_history = pd.DataFrame(rows, columns=['date', 'mood', 'burnout_score'])
    df_history['mood_score'] = df_history['mood'].map({"😊 Happy": 0, "😐 Neutral": 1, "😞 Stressed": 2})
    df_history.set_index('date', inplace=True)
    st.markdown("### 📈 Your Mood & Burnout History")
    st.line_chart(df_history[['mood_score', 'burnout_score']])

    # Export CSV
    csv = df_history.to_csv()
    st.download_button(
        label="📥 Download your mood & burnout log as CSV",
        data=csv,
        file_name=f'{user_name}_mood_burnout_log.csv',
        mime='text/csv'
    )

# --- Leaderboard for all users ---
# Enhanced CSS for mesmerizing leaderboard
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

.leaderboard-section {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    padding: 2px;
    border-radius: 32px;
    margin: 40px 0;
    position: relative;
    overflow: hidden;
}

.leaderboard-content {
    background: rgba(255, 255, 255, 0.98);
    backdrop-filter: blur(20px);
    border-radius: 30px;
    padding: 40px 30px;
    position: relative;
}

.leaderboard-header {
    text-align: center;
    margin-bottom: 35px;
    position: relative;
}

.leaderboard-title {
    font-family: 'Inter', sans-serif;
    font-weight: 800;
    font-size: 2.8rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 10px 0;
    text-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
}

.leaderboard-subtitle {
    color: #64748b;
    font-size: 1.1rem;
    font-weight: 500;
    margin: 0;
    font-family: 'Inter', sans-serif;
}

.champion-crown {
    font-size: 3.5rem;
    animation: bounce 2s ease-in-out infinite;
    display: block;
    margin-bottom: 15px;
}

@keyframes bounce {
    0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
    40% { transform: translateY(-15px); }
    60% { transform: translateY(-8px); }
}

.leaderboard-item {
    background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
    border-radius: 20px;
    padding: 20px 25px;
    margin: 15px 0;
    border: 2px solid transparent;
    background-clip: padding-box;
    position: relative;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    overflow: hidden;
}

.leaderboard-item::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, #667eea, #764ba2, #f093fb);
    z-index: -1;
    border-radius: 20px;
    opacity: 0;
    transition: opacity 0.3s ease;
}

.leaderboard-item:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 20px 40px rgba(102, 126, 234, 0.25);
}

.leaderboard-item:hover::before {
    opacity: 0.1;
}

.rank-1 {
    background: linear-gradient(135deg, #ffd700 0%, #ffed4e 50%, #fff2a8 100%);
    border: 3px solid #ffd700;
    box-shadow: 0 15px 35px rgba(255, 215, 0, 0.3);
    position: relative;
}

.rank-1::after {
    content: '👑 CHAMPION';
    position: absolute;
    top: -12px;
    right: 20px;
    background: #ffd700;
    color: #8b5d00;
    padding: 5px 15px;
    border-radius: 15px;
    font-size: 0.8rem;
    font-weight: 700;
    font-family: 'Inter', sans-serif;
}

.rank-2 {
    background: linear-gradient(135deg, #e5e7eb 0%, #f3f4f6 50%, #ffffff 100%);
    border: 3px solid #c0c0c0;
    box-shadow: 0 12px 30px rgba(192, 192, 192, 0.2);
}

.rank-3 {
    background: linear-gradient(135deg, #cd7f32 0%, #daa520 50%, #f4d03f 100%);
    border: 3px solid #cd7f32;
    box-shadow: 0 12px 30px rgba(205, 127, 50, 0.2);
}

.rank-number {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 45px;
    height: 45px;
    border-radius: 50%;
    font-weight: 800;
    font-size: 1.2rem;
    margin-right: 20px;
    color: white;
    font-family: 'Inter', sans-serif;
}

.rank-1 .rank-number {
    background: linear-gradient(135deg, #ffd700, #ffed4e);
    color: #8b5d00;
    box-shadow: 0 4px 15px rgba(255, 215, 0, 0.4);
}

.rank-2 .rank-number {
    background: linear-gradient(135deg, #c0c0c0, #e5e7eb);
    color: #4b5563;
    box-shadow: 0 4px 15px rgba(192, 192, 192, 0.3);
}

.rank-3 .rank-number {
    background: linear-gradient(135deg, #cd7f32, #daa520);
    color: white;
    box-shadow: 0 4px 15px rgba(205, 127, 50, 0.3);
}

.rank-number.other-rank {
    background: linear-gradient(135deg, #667eea, #764ba2);
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.user-info {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.user-name {
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    font-size: 1.3rem;
    color: #1e293b;
    margin: 0;
}

.user-points {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    padding: 8px 16px;
    border-radius: 25px;
    font-weight: 700;
    font-size: 1.1rem;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
    font-family: 'Inter', sans-serif;
}

.leaderboard-row {
    display: flex;
    align-items: center;
    width: 100%;
}

.empty-state {
    text-align: center;
    padding: 60px 40px;
    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    border-radius: 24px;
    border: 2px dashed #cbd5e1;
    margin: 30px 0;
}

.empty-state-icon {
    font-size: 4rem;
    margin-bottom: 20px;
    opacity: 0.6;
    animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 0.6; }
    50% { opacity: 1; }
}

.empty-state-title {
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    font-size: 1.5rem;
    color: #475569;
    margin: 0 0 10px 0;
}

.empty-state-subtitle {
    font-family: 'Inter', sans-serif;
    color: #64748b;
    font-size: 1.1rem;
    margin: 0;
}

.progress-bar {
    position: absolute;
    bottom: 0;
    left: 0;
    height: 4px;
    background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
    border-radius: 0 0 18px 18px;
    transition: width 0.8s ease;
}

.medal-icon {
    font-size: 1.8rem;
    margin-right: 10px;
}
</style>
""", unsafe_allow_html=True)

# Beautiful divider
st.markdown("""
<div style='height: 2px; background: linear-gradient(90deg, transparent, #667eea, #764ba2, #f093fb, transparent); margin: 50px 0 30px 0; border-radius: 2px;'></div>
""", unsafe_allow_html=True)

# Enhanced Leaderboard Section
st.markdown('<div class="leaderboard-section">', unsafe_allow_html=True)
st.markdown('<div class="leaderboard-content">', unsafe_allow_html=True)

# Header with animation
st.markdown("""
<div class="leaderboard-header">
    <div class="champion-crown">👑</div>
    <h1 class="leaderboard-title">Wellness Champions</h1>
    <p class="leaderboard-subtitle">Celebrating our community's wellness journey and achievements</p>
</div>
""", unsafe_allow_html=True)

# Database query (your existing code)
c.execute('''
    SELECT user, SUM(wellness_points) AS total_points
    FROM mood_logs
    GROUP BY user
    ORDER BY total_points DESC
    LIMIT 10
''')
leaderboard = c.fetchall()

if leaderboard:
    # Display leaderboard with enhanced styling
    for idx, (user, points) in enumerate(leaderboard, 1):
        # Determine rank styling
        rank_class = ""
        medal_icon = ""
        progress_width = min(100, (points / leaderboard[0][1]) * 100) if leaderboard[0][1] > 0 else 0
        
        if idx == 1:
            rank_class = "rank-1"
            medal_icon = "🥇"
        elif idx == 2:
            rank_class = "rank-2"
            medal_icon = "🥈"
        elif idx == 3:
            rank_class = "rank-3"
            medal_icon = "🥉"
        else:
            medal_icon = "⭐"
        
        # Create leaderboard item
        st.markdown(f"""
        <div class="leaderboard-item {rank_class}">
            <div class="leaderboard-row">
                <div class="rank-number {'other-rank' if idx > 3 else ''}">{idx}</div>
                <div class="user-info">
                    <div style="display: flex; align-items: center;">
                        <span class="medal-icon">{medal_icon}</span>
                        <h3 class="user-name">{user}</h3>
                    </div>
                    <div class="user-points">{points:,} pts</div>
                </div>
            </div>
            <div class="progress-bar" style="width: {progress_width}%;"></div>
        </div>
        """, unsafe_allow_html=True)
        
    # Add some stats
    total_users = len(leaderboard)
    total_points = sum(points for _, points in leaderboard)
    avg_points = total_points / total_users if total_users > 0 else 0
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Stats section
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #f0f9ff, #e0f2fe); border-radius: 16px; border: 2px solid #0ea5e9;'>
            <div style='font-size: 2.5rem; margin-bottom: 8px;'>👥</div>
            <div style='font-size: 2rem; font-weight: 700; color: #0369a1; font-family: Inter;'>{total_users}</div>
            <div style='color: #0284c7; font-weight: 500;'>Active Champions</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #f0fdf4, #dcfce7); border-radius: 16px; border: 2px solid #22c55e;'>
            <div style='font-size: 2.5rem; margin-bottom: 8px;'>🎯</div>
            <div style='font-size: 2rem; font-weight: 700; color: #15803d; font-family: Inter;'>{total_points:,}</div>
            <div style='color: #16a34a; font-weight: 500;'>Total Points</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #fefce8, #fef3c7); border-radius: 16px; border: 2px solid #eab308;'>
            <div style='font-size: 2.5rem; margin-bottom: 8px;'>📊</div>
            <div style='font-size: 2rem; font-weight: 700; color: #a16207; font-family: Inter;'>{avg_points:.0f}</div>
            <div style='color: #ca8a04; font-weight: 500;'>Avg Points</div>
        </div>
        """, unsafe_allow_html=True)

else:
    # Enhanced empty state
    st.markdown("""
    <div class="empty-state">
        <div class="empty-state-icon">🌱</div>
        <h2 class="empty-state-title">Your Wellness Journey Awaits!</h2>
        <p class="empty-state-subtitle">Be the first to start logging your moods and claim the champion's crown. Every small step counts towards a healthier, happier you.</p>
        <br>
        <div style='display: flex; justify-content: center; gap: 20px; margin-top: 20px;'>
            <div style='padding: 10px 20px; background: linear-gradient(135deg, #667eea, #764ba2); color: white; border-radius: 25px; font-weight: 600;'>🎯 Start Your Journey</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Motivational footer
st.markdown("""
<div style='text-align: center; padding: 30px 20px; color: #64748b; font-style: italic; font-family: Inter;'>
    <div style='font-size: 1.5rem; margin-bottom: 10px;'>✨</div>
    <p style='font-size: 1.1rem; margin: 0;'>"Every day is a new opportunity to improve your wellness score. Keep going, champion!"</p>
</div>
""", unsafe_allow_html=True)
# --- Mini Stress Quiz ---
# Enhanced Stress Awareness & Journaling Application
import streamlit as st
import sqlite3
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import time

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
    }
    
    
    .quiz-container {
        background: rgba(255, 255, 255, 0.95);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin: 1rem 0;
        transition: transform 0.3s ease;
    }
    
    .quiz-container:hover {
        transform: translateY(-5px);
background: linear-gradient(145deg, #fff7ed, #fed7aa);
padding: 2rem;
border-radius: 20px;
box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
margin: 1rem 0;
border-left: 5px solid #f97316;
    }
    
    .journal-container {
       background: linear-gradient(145deg, #e8f8f5, #d5f4e6);
padding: 2rem;
border-radius: 20px;
box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
margin: 1rem 0;
border-left: 5px solid #10b981;
    }
    
    .score-card {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
    
    .question-card {
        background: linear-gradient(145deg, #f8f9ff, #e8ecff);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
        transition: all 0.3s ease;
    }
    
    .question-card:hover {
        transform: translateX(5px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }
    
    .motivational-quote {
        background: linear-gradient(135deg, #ffeaa7, #fdcb6e);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin: 2rem 0;
        font-style: italic;
        font-size: 1.1rem;
        box-shadow: 0 5px 15px rgba(253, 203, 110, 0.3);
    }
    
    .progress-bar {
        background: linear-gradient(90deg, #667eea, #764ba2);
        height: 8px;
        border-radius: 4px;
        margin: 1rem 0;
    }
    
    .celebration-text {
        background: linear-gradient(135deg, #00b894, #00cec9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 1.5rem;
        font-weight: bold;
        text-align: center;
        margin: 1rem 0;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 15px;
        border: 2px solid #e0e0e0;
        transition: border-color 0.3s ease;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 10px rgba(102, 126, 234, 0.2);
    }
    
    .wellness-tip {
        background: linear-gradient(135deg, #a8edea, #fed6e3);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.8s ease-out;
    }
    
    .emoji-large {
        font-size: 3rem;
        text-align: center;
        margin: 1rem 0;
        animation: bounce 2s infinite;
    }
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-10px); }
        60% { transform: translateY(-5px); }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for quiz progress
if 'quiz_started' not in st.session_state:
    st.session_state.quiz_started = False
if 'quiz_completed' not in st.session_state:
    st.session_state.quiz_completed = False
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'quiz_answers' not in st.session_state:
    st.session_state.quiz_answers = {}

# Motivational quotes
motivational_quotes = [
    "🌟 Every moment is a fresh beginning. - T.S. Eliot",
    "🌈 The only way out is through. - Robert Frost",
    "🦋 What lies behind us and what lies before us are tiny matters compared to what lies within us. - Ralph Waldo Emerson",
    "🌸 You are braver than you believe, stronger than you seem, and smarter than you think. - A.A. Milne",
    "🎯 Progress, not perfection, is the goal. - Unknown"
]

# Wellness tips
wellness_tips = [
    "💧 Remember to stay hydrated throughout the day!",
    "🧘‍♀️ Take 5 deep breaths when feeling overwhelmed.",
    "🌿 Spend a few minutes in nature to reset your mind.",
    "📱 Consider a digital detox for better mental clarity.",
    "💤 Prioritize 7-9 hours of quality sleep each night."
]

# Header with animation
st.markdown("""
<div class="fade-in">
    <h1 style="text-align: center; color: #667eea; font-size: 3rem; margin-bottom: 0;">
        🧠✨ Mindful Moments
    </h1>
    <p style="text-align: center; color: #666; font-size: 1.2rem; margin-top: 0;">
        Your Personal Stress Awareness & Wellness Journey
    </p>
</div>
""", unsafe_allow_html=True)

# Random motivational quote
import random
quote = random.choice(motivational_quotes)
st.markdown(f'<div class="motivational-quote fade-in">{quote}</div>', unsafe_allow_html=True)

# Stress Awareness Quiz Section
st.markdown("""
<div class="quiz-container fade-in">
    <h2 style="color: #667eea; text-align: center; margin-bottom: 1.5rem;">
        🧩 Interactive Stress Awareness Quiz
    </h2>
    <p style="text-align: center; color: #666; margin-bottom: 2rem;">
        Test your knowledge about stress management and build better habits!
    </p>
</div>
""", unsafe_allow_html=True)

# Enhanced quiz questions with explanations
quiz_questions = {
    "What is the most effective practice to reduce stress?": {
        "options": [
            "🚫 Ignoring stress completely",
            "🧘‍♂️ Meditation and mindfulness",
            "💼 Working harder and longer",
            "🎮 Avoiding all responsibilities"
        ],
        "correct": "🧘‍♂️ Meditation and mindfulness",
        "explanation": "Meditation helps regulate your nervous system and builds resilience against stress."
    },
    "Which habit helps build long-term resilience?": {
        "options": [
            "🏃‍♂️ Regular exercise and movement",
            "😴 Skipping sleep to be productive",
            "🤹‍♂️ Constant multitasking",
            "🏠 Avoiding social connections"
        ],
        "correct": "🏃‍♂️ Regular exercise and movement",
        "explanation": "Exercise releases endorphins and helps your body manage stress hormones effectively."
    },
    "Journaling can help with:": {
        "options": [
            "📝 Expressing and processing emotions",
            "📈 Increasing daily workload",
            "🙈 Ignoring difficult emotions",
            "❌ None of the above"
        ],
        "correct": "📝 Expressing and processing emotions",
        "explanation": "Writing helps externalize thoughts and provides clarity during stressful times."
    },
    "What's the best way to handle overwhelming situations?": {
        "options": [
            "🏃‍♂️ Run away from the problem",
            "🧘‍♀️ Break it down into smaller steps",
            "😤 Push through without breaks",
            "🤷‍♂️ Hope it resolves itself"
        ],
        "correct": "🧘‍♀️ Break it down into smaller steps",
        "explanation": "Breaking large problems into manageable pieces reduces anxiety and increases success rates."
    }
}

# Quiz Progress Bar
if st.session_state.quiz_started:
    progress = len(st.session_state.quiz_answers) / len(quiz_questions)
    st.progress(progress)
    st.write(f"Progress: {len(st.session_state.quiz_answers)}/{len(quiz_questions)} questions completed")

# Interactive Quiz Logic
if not st.session_state.quiz_started:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Begin Your Wellness Quiz", key="start_quiz"):
            st.session_state.quiz_started = True
            st.rerun()

elif not st.session_state.quiz_completed:
    # Display current question
    questions_list = list(quiz_questions.keys())
    current_q = questions_list[st.session_state.current_question]
    
    st.markdown(f"""
    <div class="question-card">
        <h3 style="color: #667eea;">Question {st.session_state.current_question + 1} of {len(questions_list)}</h3>
        <h4>{current_q}</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Radio buttons for current question
    answer = st.radio(
        "Choose your answer:",
        quiz_questions[current_q]["options"],
        key=f"q_{st.session_state.current_question}"
    )
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("Next Question ➡️", key="next_q"):
            st.session_state.quiz_answers[current_q] = answer
            
            if st.session_state.current_question < len(questions_list) - 1:
                st.session_state.current_question += 1
                st.rerun()
            else:
                st.session_state.quiz_completed = True
                st.rerun()

else:
    # Calculate and display results
    quiz_score = 0
    for question, user_answer in st.session_state.quiz_answers.items():
        if user_answer == quiz_questions[question]["correct"]:
            quiz_score += 1
    
    # Animated score display
    st.markdown(f"""
    <div class="score-card fade-in">
        <div class="emoji-large">🎉</div>
        <h2>Quiz Complete!</h2>
        <h1 style="font-size: 3rem; margin: 1rem 0;">{quiz_score}/{len(quiz_questions)}</h1>
        <h3>Fantastic effort!</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Personalized feedback
    if quiz_score == len(quiz_questions):
        st.markdown("""
        <div class="celebration-text">
            🌟 Excellent! You're a stress management expert! 🌟
        </div>
        """, unsafe_allow_html=True)
        st.balloons()
    elif quiz_score >= len(quiz_questions) // 2:
        st.markdown("""
        <div class="celebration-text">
            🎯 Great job! You're on the right track! 🎯
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="celebration-text">
            🌱 Keep learning! Every step counts! 🌱
        </div>
        """, unsafe_allow_html=True)
    
    # Show explanations
    st.markdown("### 📚 Learn More:")
    for question, details in quiz_questions.items():
        user_answer = st.session_state.quiz_answers.get(question, "")
        is_correct = user_answer == details["correct"]
        
        emoji = "✅" if is_correct else "❌"
        st.markdown(f"""
        <div class="question-card">
            <strong>{emoji} {question}</strong><br>
            <span style="color: #667eea;">Correct Answer:</span> {details["correct"]}<br>
            <span style="color: #666;">💡 {details["explanation"]}</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Reset button
    if st.button("🔄 Take Quiz Again"):
        st.session_state.quiz_started = False
        st.session_state.quiz_completed = False
        st.session_state.current_question = 0
        st.session_state.quiz_answers = {}
        st.rerun()

# Wellness Tip
tip = random.choice(wellness_tips)
st.markdown(f'<div class="wellness-tip fade-in"><strong>💡 Wellness Tip:</strong> {tip}</div>', unsafe_allow_html=True)

# Enhanced Journaling Section
st.markdown("""
<div class="journal-container fade-in">
    <h2 style="color: #667eea; text-align: center; margin-bottom: 1rem;">
        ✍️ Mindful Journaling Space
    </h2>
    <p style="text-align: center; color: #666; margin-bottom: 2rem;">
        Express your thoughts and feelings in this safe, private space
    </p>
</div>
""", unsafe_allow_html=True)

# Journaling prompts
journal_prompts = [
    "What am I grateful for today?",
    "What challenged me today and how did I handle it?",
    "What would I like to accomplish tomorrow?",
    "How are my stress levels right now?",
    "What made me smile today?",
    "What lesson did I learn today?",
    "How can I be kinder to myself?"
]

# Prompt selector
selected_prompt = st.selectbox(
    "🎯 Choose a journaling prompt (or write freely):",
    ["Write freely..."] + journal_prompts
)

# Display selected prompt
if selected_prompt != "Write freely...":
    st.markdown(f"""
    <div class="question-card">
        <h4 style="color: #667eea;">Today's Reflection:</h4>
        <p style="font-style: italic; color: #666;">{selected_prompt}</p>
    </div>
    """, unsafe_allow_html=True)

# Enhanced text area
journal_entry = st.text_area(
    "Your thoughts:",
    height=200,
    placeholder="Start writing your thoughts here... There's no right or wrong way to journal. Just let your thoughts flow naturally. 🌸",
    help="Take your time. This is your space to be authentic and honest with yourself."
)

# Word count and encouragement
if journal_entry:
    word_count = len(journal_entry.split())
    st.markdown(f"""
    <div style="text-align: right; color: #666; font-size: 0.9rem;">
        📝 {word_count} words written
    </div>
    """, unsafe_allow_html=True)
    
    if word_count > 50:
        st.markdown("""
        <div style="color: #667eea; text-align: center; font-style: italic;">
            🌟 Beautiful! You're really opening up. Keep going! 🌟
        </div>
        """, unsafe_allow_html=True)

# Save button with enhanced functionality
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("💾 Save My Reflection", key="save_journal"):
        if not st.session_state.get('user_name', '').strip():
            st.warning("⚠️ Please enter your name in the sidebar before saving your journal.")
        elif journal_entry.strip() == "":
            st.warning("⚠️ Please write something before saving.")
        else:
            # Simulate saving (replace with your actual database code)
            st.success("✨ Your reflection has been saved successfully!")
            st.markdown("""
            <div style="text-align: center; margin-top: 1rem;">
                <p style="color: #667eea; font-style: italic;">
                    Thank you for taking time for self-reflection. You're investing in your mental wellness! 🌱
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show confetti effect
            time.sleep(1)
            st.balloons()
# --- Custom CSS for Enhanced Styling ---
st.markdown("""
<style>
    /* Main background gradient */
   
    
    /* Custom card styling */
    .wellness-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 30px;
        margin: 20px 0;
        border: 1px solid rgba(255, 255, 255, 0.5);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .wellness-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 45px rgba(0, 0, 0, 0.2);
    }
    
    /* Animated gradient text */
    .gradient-text {
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4);
        background-size: 300% 300%;
        animation: gradient 3s ease infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: bold;
        font-size: 2.5rem;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Pulsing animation for buttons */
    .pulse-button {
        animation: pulse 2s infinite;
        border-radius: 25px !important;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4) !important;
        border: none !important;
        color: white !important;
        font-weight: bold !important;
        padding: 12px 30px !important;
        transition: all 0.3s ease !important;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 107, 107, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(255, 107, 107, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 107, 107, 0); }
    }
    
    /* Floating animation */
    .floating {
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    /* Breathing animation */
    .breathing-circle {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        background: radial-gradient(circle, #4ecdc4, #44a08d);
        margin: 30px auto;
        animation: breathe 4s ease-in-out infinite;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 1.2rem;
    }
    
    @keyframes breathe {
        0%, 100% { transform: scale(1); opacity: 0.8; }
        50% { transform: scale(1.1); opacity: 1; }
    }
    
    /* Music player styling */
    .music-container {
        background: rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        padding: 25px;
        margin: 20px 0;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    /* Email section styling */
    .email-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 30px;
        margin: 30px 0;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    }
    
    /* Custom input styling */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.2) !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 15px !important;
        color: black !important;
        padding: 15px !important;
        font-size: 16px !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: rgba(255, 255, 255, 0.7) !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #4ecdc4 !important;
        box-shadow: 0 0 15px rgba(78, 205, 196, 0.5) !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Hero Section ---
st.markdown('<h1 class="gradient-text">✨ Wellness Sanctuary ✨</h1>', unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; font-size: 1.3rem; margin-bottom: 30px; opacity: 0.9;">
    Your personal space for mindfulness, relaxation, and inner peace
</div>
""", unsafe_allow_html=True)

# --- Music Player Section ---
st.markdown("""
<div class="music-container floating">
    <h2 style="text-align: center; margin-bottom: 20px;">🎵 Soothing Soundscape</h2>
    <p style="text-align: center; opacity: 0.8; margin-bottom: 20px;">Let calming melodies wash away your stress</p>
</div>
""", unsafe_allow_html=True)

# Multiple music options
col1, col2 = st.columns(2)

with col1:
    st.markdown("**🌊 Ocean Waves**")
    ocean_iframe = """
    <iframe style="border-radius:12px" src="https://open.spotify.com/embed/track/5nTtCOCds6I0PHMNtqelas?utm_source=generator" width="100%" height="80" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>
    """
    st.components.v1.html(ocean_iframe, height=100)

with col2:
    st.markdown("**🌙 Night Ambience**")
    night_iframe = """
    <iframe style="border-radius:12px" src="https://open.spotify.com/embed/track/4uLU6hMCjMI75M1A2tKUQC?utm_source=generator" width="100%" height="80" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>
    """
    st.components.v1.html(night_iframe, height=100)

# --- Interactive Breathing Section ---
# --- Interactive Breathing Section ---
# --- Interactive Breathing Section ---
st.markdown("---")

# Enhanced CSS for breathing animations and styling
st.markdown("""
<style>
    .wellness-card {
        background: linear-gradient(135deg, rgba(78, 205, 196, 0.1), rgba(255, 217, 61, 0.1));
        padding: 30px;
        border-radius: 20px;
        margin: 20px 0;
        border: 1px solid rgba(78, 205, 196, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .breathing-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 300px;
        margin: 30px 0;
    }
    
    .breathing-circle {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(78, 205, 196, 0.3), rgba(78, 205, 196, 0.1));
        display: flex;
        justify-content: center;
        align-items: center;
        animation: breathe 4s ease-in-out infinite;
        border: 3px solid rgba(78, 205, 196, 0.5);
        box-shadow: 0 0 30px rgba(78, 205, 196, 0.3);
        position: relative;
    }
    
    .breathing-circle::before {
        content: '';
        position: absolute;
        width: 120%;
        height: 120%;
        border-radius: 50%;
        border: 2px solid rgba(78, 205, 196, 0.2);
        animation: pulse 4s ease-in-out infinite;
    }
    
    .breathing-circle span {
        font-size: 1.2rem;
        font-weight: bold;
        color: #2c3e50;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    @keyframes breathe {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.3); }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 0.3; transform: scale(1); }
        50% { opacity: 0.1; transform: scale(1.2); }
    }
    
    .phase-indicator {
        text-align: center;
        padding: 20px;
        border-radius: 15px;
        margin: 15px 0;
        transition: all 0.3s ease;
        font-size: 1.3rem;
        font-weight: bold;
    }
    
    .inhale { background: linear-gradient(45deg, #4ecdc4, #44a08d); color: white; }
    .hold { background: linear-gradient(45deg, #ffd93d, #f39c12); color: #2c3e50; }
    .exhale { background: linear-gradient(45deg, #ff6b6b, #ee5a24); color: white; }
    
    .completion-message {
        text-align: center;
        padding: 25px;
        border-radius: 20px;
        background: linear-gradient(135deg, #4ecdc4, #44a08d);
        color: white;
        margin: 20px 0;
        animation: fadeIn 1s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .breathing-stats {
        background: rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Main breathing section header
st.markdown("""
<div class="wellness-card">
    <h2 style="text-align: center; margin-bottom: 15px;">🧘‍♀️ Mindful Breathing</h2>
    <p style="text-align: center; opacity: 0.9; font-size: 1.1rem;">Find your center with guided breathing exercises</p>
</div>
""", unsafe_allow_html=True)

# Breathing animation display
st.markdown("""
<div class="breathing-container">
    <div class="breathing-circle">
        <span>Breathe</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Enhanced breathing exercise with better UX
with st.expander("🌟 Guided 4-7-8 Breathing Journey", expanded=False):
    st.markdown("""
    ## The Science Behind 4-7-8 Breathing

    This evidence-based technique activates your parasympathetic nervous system. It reduces cortisol levels and promotes relaxation.

    ### Step-by-Step Guide:
    **🌬️ Inhale:** Breathe in quietly through your nose for **4 counts**  
    **⏸️ Hold:** Retain your breath gently for **7 counts**  
    **💨 Exhale:** Release completely through your mouth for **8 counts**  

    *💡 Tip: Start slowly and let it flow naturally.*
    """)  # No HTML needed    # Control buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Session options
        cycles = st.selectbox("Choose session length:", [3, 5, 8], index=0, 
                             help="Select number of breathing cycles")
        
        if st.button("🌟 Begin Your Breathing Journey", key="breathing_start", type="primary"):
            # Initialize session tracking
            session_container = st.container()
            
            with session_container:
                st.markdown(f"""
                <div class="breathing-stats">
                    <h4>🎯 Session: {cycles} Cycles | ⏱️ Duration: ~{cycles * 19} seconds</h4>
                </div>
                """, unsafe_allow_html=True)
                
                # Progress tracking
                overall_progress = st.progress(0)
                cycle_progress = st.progress(0)
                status_container = st.empty()
                
                # Breathing phases configuration
                phases = [
                    ("🌬️ Inhale deeply through your nose...", 4, "inhale"),
                    ("⏸️ Hold your breath gently...", 7, "hold"),
                    ("💨 Exhale slowly through your mouth...", 8, "exhale")
                ]
                
                try:
                    for cycle in range(1, cycles + 1):
                        # Update overall progress
                        overall_progress.progress(cycle / cycles)
                        
                        st.markdown(f"""
                        <div style="text-align: center; margin: 20px 0;">
                            <h3 style="color: #4ecdc4;">Cycle {cycle} of {cycles}</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        for phase_text, duration, phase_class in phases:
                            # Display current phase
                            status_container.markdown(f"""
                            <div class="phase-indicator {phase_class}">
                                {phase_text}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Countdown for current phase
                            for i in range(duration):
                                cycle_progress.progress((i + 1) / duration)
                                time.sleep(1)
                            
                            # Small pause between phases
                            time.sleep(0.5)
                            cycle_progress.progress(0)
                    
                    # Completion message
                    status_container.markdown("""
                    <div class="completion-message">
                        <h3>✨ Congratulations! ✨</h3>
                        <p>You've completed your mindful breathing journey. Notice how you feel - more centered, calm, and present.</p>
                        <p style="margin-top: 15px;">🌟 Take a moment to appreciate this gift you've given yourself.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Success celebration
                    st.balloons()
                    
                    # Session summary
                    st.markdown(f"""
                    <div class="breathing-stats">
                        <h4>📊 Session Complete!</h4>
                        <p>✅ {cycles} cycles completed | ⏱️ {cycles * 19} seconds of mindfulness</p>
                        <p>🧘‍♀️ Remember: Regular practice enhances the benefits!</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error("Session interrupted. Feel free to try again when you're ready.")

# Additional breathing techniques
st.markdown("### 🌿 More Breathing Techniques")

col1, col2 = st.columns(2)

with col1:
    with st.expander("🌊 Box Breathing (4-4-4-4)"):
        st.markdown("""
        **Perfect for focus and concentration**
        - Inhale for 4 counts
        - Hold for 4 counts  
        - Exhale for 4 counts
        - Hold empty for 4 counts
        
        *Great for before important meetings or exams!*
        """)

with col2:
    with st.expander("🌅 Physiological Sigh"):
        st.markdown("""
        **Quick stress relief in 1-2 breaths**
        - Take a normal inhale
        - Add a second, smaller inhale on top
        - Long, slow exhale through mouth
        
        *Scientifically proven to calm the nervous system rapidly!*
        """)

# Tips section
st.markdown("""
<div style="background: rgba(255, 217, 61, 0.1); padding: 20px; border-radius: 15px; margin: 20px 0; border-left: 4px solid #ffd93d;">
    <h4>💡 Pro Tips for Better Breathing:</h4>
    <ul style="line-height: 1.8;">
        <li>Practice in a quiet, comfortable space</li>
        <li>Maintain good posture - sit or stand tall</li>
        <li>Don't force the breath - let it flow naturally</li>
        <li>Consistency matters more than duration</li>
        <li>Try different times of day to find what works best</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# --- Wellness Statistics Dashboard ---
st.markdown("---")
st.markdown("""
<div class="wellness-card">
    <h2 style="text-align: center;">📊 Your Wellness Journey</h2>

</div>

""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🧘 Sessions Today", "3", "↑ 1")
with col2:
    st.metric("⏱️ Minutes Practiced", "15", "↑ 5")
with col3:
    st.metric("🔥 Day Streak", "7", "↑ 1")
with col4:
    st.metric("😌 Stress Level", "3/10", "↓ 2")

# --- Enhanced Email Reminder Section ---
st.markdown("---")
st.markdown("""
<div class="email-section">
    <h2 style="text-align: center; margin-bottom: 25px;">📧 Wellness Reminders</h2>
    <p style="text-align: center; font-size: 1.1rem; opacity: 0.9; margin-bottom: 30px;">
        Never miss your self-care moments. Get gentle reminders to prioritize your wellbeing.
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    email_input = st.text_input(
        "", 
        placeholder="✉️ Enter your email for wellness reminders...",
        key="email_input",
        help="We'll send you gentle reminders to take breaks and practice mindfulness"
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
    send_email = st.button("🌟 Start My Journey", key="email_submit")

if send_email:
    if email_input.strip() == "":
        st.error("🌸 Please enter your email to begin your wellness journey")
    elif "@" not in email_input or "." not in email_input:
        st.error("🌸 Please enter a valid email address")
    else:
        # Simulate email sending with progress
        with st.spinner("✨ Setting up your wellness reminders..."):
            time.sleep(2)  # Simulate processing
        
        st.success(f"""
        🎉 Welcome to your wellness journey, {email_input.split('@')[0]}! 
        
        Your personalized reminders are now active. You'll receive:
        • 🌅 Morning mindfulness prompts
        • 🍃 Midday breathing reminders  
        • 🌙 Evening reflection guides
        
        *Note: Configure SMTP settings for actual email delivery*
        """)
        st.balloons()
# --- Feedback Section ---
# Enhanced CSS for professional appearance
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

.feedback-hero {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    padding: 40px 30px;
    border-radius: 24px;
    margin: 30px 0;
    position: relative;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(102, 126, 234, 0.25);
}

.feedback-hero::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.08"/><circle cx="50" cy="10" r="0.5" fill="white" opacity="0.12"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
    opacity: 0.3;
}

.feedback-hero-content {
    position: relative;
    z-index: 2;
    text-align: center;
}

.feedback-hero h2 {
    color: white;
    font-family: 'Inter', sans-serif;
    font-weight: 700;
    font-size: 2.5rem;
    margin: 0 0 15px 0;
    text-shadow: 0 2px 20px rgba(0,0,0,0.2);
}

.feedback-hero p {
    color: rgba(255,255,255,0.95);
    font-family: 'Inter', sans-serif;
    font-size: 1.1rem;
    font-weight: 400;
    margin: 0;
    line-height: 1.6;
}

.feedback-container {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    padding: 40px;
    border-radius: 28px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 25px 80px rgba(0, 0, 0, 0.08);
    margin: 30px 0;
    position: relative;
}

.feedback-container::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
    border-radius: 28px 28px 0 0;
}

.rating-container {
    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    padding: 25px;
    border-radius: 20px;
    margin: 25px 0;
    border: 1px solid #e2e8f0;
}

.submit-container {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2px;
    border-radius: 16px;
    margin: 30px 0 20px 0;
}

.submit-button {
    background: white;
    color: #667eea;
    padding: 15px 30px;
    border-radius: 14px;
    border: none;
    font-weight: 600;
    font-size: 1.1rem;
    cursor: pointer;
    width: 100%;
    transition: all 0.3s ease;
    font-family: 'Inter', sans-serif;
}

.submit-button:hover {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
}

.floating-icon {
    font-size: 4rem;
    animation: float 3s ease-in-out infinite;
    display: block;
    text-align: center;
    margin-bottom: 15px;
}

@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
}

.stSelectbox > div > div {
    border-radius: 12px !important;
    border: 2px solid #e2e8f0 !important;
    padding: 8px !important;
}

.stTextArea > div > div > textarea {
    border-radius: 16px !important;
    border: 2px solid #e2e8f0 !important;
    padding: 16px !important;
    font-family: 'Inter', sans-serif !important;
    line-height: 1.6 !important;
}

.stTextArea > div > div > textarea:focus {
    border-color: #667eea !important;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
}
</style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class="feedback-hero">
    <div class="feedback-hero-content">
        <div class="floating-icon">💫</div>
        <h2>Share Your Experience</h2>
        <p>Your insights shape our journey towards excellence. Every word matters, every suggestion counts.</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Main Feedback Container
st.markdown('<div class="feedback-container">', unsafe_allow_html=True)

# Elegant spacing
st.markdown("<br>", unsafe_allow_html=True)

# Feedback Category Selection
feedback_category = st.selectbox(
    "🎯 **What would you like to share feedback about?**",
    ["✨ Overall Experience", "🚀 App Features & Functionality", "🐛 Bug Report & Issues", "💡 Feature Suggestions", "🎨 Design & User Interface", "📚 Content & Resources", "🔧 Technical Performance", "💭 Other Thoughts"],
    help="Choose the category that best fits your feedback to help us respond more effectively"
)

st.markdown("<br>", unsafe_allow_html=True)

# Enhanced Text Area
feedback_text = st.text_area(
    "✍️ **Tell us what's on your mind**",
    placeholder="Share your detailed thoughts, experiences, suggestions, or any concerns. We genuinely value your perspective and read every single piece of feedback to continuously improve our service...",
    height=140,
    key="feedback_text",
    help="The more specific you are, the better we can address your feedback. Feel free to be as detailed as you'd like!"
)

st.markdown("<br>", unsafe_allow_html=True)

# Rating Section with beautiful styling
st.markdown('<div class="rating-container">', unsafe_allow_html=True)
st.markdown("### ⭐ **Rate Your Experience**")
st.markdown("<small style='color: #64748b;'>Help us understand how we're doing overall</small>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    rating = st.select_slider(
        "",
        options=[1, 2, 3, 4, 5],
        value=5,
        format_func=lambda x: ["⭐ Needs Improvement", "⭐⭐ Fair Experience", "⭐⭐⭐ Good Overall", "⭐⭐⭐⭐ Great Experience", "⭐⭐⭐⭐⭐ Outstanding!"][x-1]
    )
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# Submit Button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🚀 **Submit Your Feedback**", type="primary", use_container_width=True):
        if feedback_text.strip() == "":
            st.error("💭 **Please share your thoughts before submitting** - we're excited to hear from you!")
        else:
            # Assuming you have the database setup
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Database insert (uncomment when you have the database setup)
            # c.execute("INSERT INTO feedback (user, date, feedback, category, rating) VALUES (?, ?, ?, ?, ?)", 
            #          (user_name, now, feedback_text, feedback_category, rating))
            # conn.commit()
            
            # Success animation and message
            st.balloons()
            st.success("🎉 **Thank you for your valuable feedback!** Your insights help us create an even better experience for everyone in our community.")
            
            # Additional appreciation message
            st.info("💜 **We truly appreciate you taking the time to share your thoughts.** Our team will review your feedback and use it to enhance our service.")
            
            # Auto-clear and refresh (uncomment if needed)
            # time.sleep(2)
            # st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# Footer message
st.markdown("""
<div style='text-align: center; padding: 20px; color: #64748b; font-style: italic;'>
    <small>💝 Your feedback drives our continuous improvement. Thank you for being part of our journey!</small>
</div>
""", unsafe_allow_html=True)

# --- Enhanced Data Management Section ---
st.markdown("---")

# Warning section with better design
st.markdown("""
<div style='background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%);
            padding: 20px; border-radius: 15px; margin: 20px 0;
            border-left: 5px solid #ff6b6b;'>
    <h3 style='color: #d63031; margin: 0 0 10px 0; display: flex; align-items: center;'>
        ⚠️ Data Management Zone
    </h3>
    <p style='color: #2d3436; margin: 0; font-size: 14px;'>
        Handle your personal data with care. These actions cannot be undone.
    </p>
</div>
""", unsafe_allow_html=True)

# Data management options
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div style='background: #fff5f5; padding: 20px; border-radius: 10px; border: 1px solid #fed7d7;'>
        <h4 style='color: #e53e3e; margin: 0 0 10px 0;'>🗑️ Reset Your Data</h4>
        <p style='color: #4a5568; font-size: 13px; margin: 0;'>
            This will permanently delete all your mood logs and feedback. 
            Use this if you want to start fresh.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("⚠️ Reset All My Data", type="secondary", help="This action cannot be undone"):
        if user_name.strip() == "":
            st.warning("👤 Please enter your name in the sidebar first to reset your data.")
        else:
            # Confirmation dialog simulation
            if 'confirm_reset' not in st.session_state:
                st.session_state.confirm_reset = False
            
            if not st.session_state.confirm_reset:
                st.session_state.confirm_reset = True
                st.error("⚠️ Are you absolutely sure? Click the button again to confirm.")
            else:
                c.execute("DELETE FROM mood_logs WHERE user = ?", (user_name,))
                c.execute("DELETE FROM feedback WHERE user = ?", (user_name,))
                conn.commit()
                st.success("✅ All your data has been successfully reset. You can start fresh now!")
                st.session_state.confirm_reset = False

with col2:
    st.markdown("""
    <div style='background: #f0fff4; padding: 20px; border-radius: 10px; border: 1px solid #c6f6d5;'>
        <h4 style='color: #38a169; margin: 0 0 10px 0;'>📊 Export Your Data</h4>
        <p style='color: #4a5568; font-size: 13px; margin: 0;'>
            Download your mood logs and feedback as a CSV file 
            for your personal records.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("📥 Export My Data", type="secondary", help="Download your data as CSV"):
        if user_name.strip() == "":
            st.warning("👤 Please enter your name in the sidebar first.")
        else:
            # Get user data
            c.execute("SELECT * FROM mood_logs WHERE user = ?", (user_name,))
            mood_data = c.fetchall()
            c.execute("SELECT * FROM feedback WHERE user = ?", (user_name,))
            feedback_data = c.fetchall()
            
            if mood_data or feedback_data:
                import pandas as pd
                import io
                
                # Create CSV content
                output = io.StringIO()
                output.write("=== MOOD LOGS ===\n")
                if mood_data:
                    df_mood = pd.DataFrame(mood_data, columns=['ID', 'User', 'Date', 'Mood', 'Music_Used', 'Journaled', 'Notes'])
                    df_mood.to_csv(output, index=False)
                
                output.write("\n\n=== FEEDBACK ===\n")
                if feedback_data:
                    df_feedback = pd.DataFrame(feedback_data, columns=['ID', 'User', 'Date', 'Feedback', 'Category', 'Rating'])
                    df_feedback.to_csv(output, index=False)
                
                st.download_button(
                    label="💾 Download CSV File",
                    data=output.getvalue(),
                    file_name=f"{user_name}_mood_data.csv",
                    mime="text/csv"
                )
                st.success("📁 Your data is ready for download!")
            else:
                st.info("📭 No data found to export. Start logging your moods first!")

# --- Enhanced Sidebar: Recent Mood Summary ---
with st.sidebar:
    st.markdown("---")
    st.markdown("""
    <div style='background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
                padding: 15px; border-radius: 10px; margin: 10px 0;'>
        <h3 style='margin: 0; color: #2d3436; text-align: center;'>📅 Recent Moods</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if user_name.strip() != "":
        c.execute("SELECT date, mood, music_used, journaled FROM mood_logs WHERE user = ? ORDER BY date DESC LIMIT 5", (user_name,))
        recent_moods = c.fetchall()
        
        if recent_moods:
            for i, entry in enumerate(recent_moods):
                date_str = entry[0].split(" ")[0]
                mood, music_used, journaled = entry[1], entry[2], entry[3]
                
                # Mood emoji mapping
                mood_emojis = {
                    "Great": "😄", "Good": "😊", "Okay": "😐", 
                    "Bad": "😔", "Terrible": "😢"
                }
                mood_emoji = mood_emojis.get(mood, "😐")
                
                # Color coding
                colors = {
                    "Great": "#4ade80", "Good": "#60a5fa", "Okay": "#fbbf24", 
                    "Bad": "#f87171", "Terrible": "#ef4444"
                }
                color = colors.get(mood, "#6b7280")
                
                st.markdown(f"""
                <div style='background: {color}20; padding: 12px; border-radius: 8px; margin: 8px 0;
                            border-left: 4px solid {color};'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <span style='font-weight: bold; color: #2d3436;'>{mood_emoji} {mood}</span>
                        <span style='font-size: 12px; color: #636e72;'>{date_str}</span>
                    </div>
                    <div style='margin-top: 8px; font-size: 12px;'>
                        {'🎵' if music_used else '🔇'} Music {'  ✍️' if journaled else '  📝'} Journal
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='text-align: center; padding: 20px; color: #6b7280;'>
                <div style='font-size: 48px; margin-bottom: 10px;'>🌱</div>
                <p style='margin: 0; font-size: 14px;'>Start logging your moods to see your journey!</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='text-align: center; padding: 20px; color: #6b7280;'>
            <div style='font-size: 48px; margin-bottom: 10px;'>👋</div>
            <p style='margin: 0; font-size: 14px;'>Enter your name above to see your mood history!</p>
        </div>
        """, unsafe_allow_html=True)

# Note: Database connection cleanup handled automatically by Streamlit