import streamlit as st
import pandas as pd
from utils.auth import init_session_state, is_authenticated, require_auth
from utils.data_manager import save_user_profile

st.set_page_config(page_title="Profile Setup - AI Learning Mentor", page_icon="👤")

init_session_state()
require_auth()

st.title("👤 Profile Setup")
st.markdown("Help us personalize your learning experience by completing your profile.")

if not is_authenticated():
    st.error("Please log in to access this page.")
    if st.button("Go to Login"):
        st.switch_page("pages/1_Login.py")
    st.stop()

user_data = st.session_state.user_data

# Profile form
with st.form("profile_form"):
    st.header("📋 Personal Information")
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name", value=user_data.get('name', ''))
        experience_level = st.selectbox(
            "Experience Level",
            ["Beginner", "Intermediate", "Advanced", "Expert"],
            index=["Beginner", "Intermediate", "Advanced", "Expert"].index(
                user_data.get('experience_level', 'Beginner')
            )
        )
    
    with col2:
        email = st.text_input("Email", value=user_data.get('email', ''), disabled=True)
        # Handle age_group with proper NaN checking
        current_age_group = user_data.get('age_group', 'Under 18')
        if pd.isna(current_age_group) or current_age_group == '' or current_age_group not in ["Under 18", "18-25", "26-35", "36-50", "50+"]:
            current_age_group = 'Under 18'
        
        age_group = st.selectbox(
            "Age Group",
            ["Under 18", "18-25", "26-35", "36-50", "50+"],
            index=["Under 18", "18-25", "26-35", "36-50", "50+"].index(current_age_group)
        )
    
    st.header("🎯 Interests & Skills")
    
    # Interests
    st.subheader("Areas of Interest")
    interests_options = [
        "Programming", "Data Science", "Machine Learning", "Web Development",
        "Mobile Development", "Game Development", "Cybersecurity", "DevOps",
        "UI/UX Design", "Digital Marketing", "Business Analysis", "Project Management",
        "Photography", "Writing", "Music", "Art & Design", "Languages", "Mathematics",
        "Physics", "Chemistry", "Biology", "Psychology", "History", "Philosophy"
    ]
    
    current_interests = user_data.get('interests', '').split(',') if user_data.get('interests') else []
    current_interests = [i.strip() for i in current_interests if i.strip()]
    
    selected_interests = st.multiselect(
        "Select your areas of interest (choose multiple)",
        interests_options,
        default=[i for i in current_interests if i in interests_options]
    )
    
    additional_interests = st.text_area(
        "Other interests (comma-separated)",
        value=', '.join([i for i in current_interests if i not in interests_options])
    )
    
    # Current Skills
    st.subheader("Current Skills")
    skills_categories = {
        "Programming Languages": ["Python", "JavaScript", "Java", "C++", "C#", "Go", "Rust", "Swift", "Kotlin"],
        "Web Technologies": ["HTML/CSS", "React", "Vue.js", "Angular", "Node.js", "Django", "Flask", "Express"],
        "Data & Analytics": ["SQL", "Pandas", "NumPy", "Matplotlib", "Tableau", "Excel", "R", "Power BI"],
        "Tools & Platforms": ["Git", "Docker", "AWS", "Azure", "Google Cloud", "Linux", "Jenkins", "Kubernetes"],
        "Design & Creative": ["Photoshop", "Illustrator", "Figma", "Sketch", "Canva", "Video Editing"]
    }
    
    current_skills = user_data.get('skills', '').split(',') if user_data.get('skills') else []
    current_skills = [s.strip() for s in current_skills if s.strip()]
    
    all_skills = []
    for category, skills in skills_categories.items():
        st.write(f"**{category}**")
        selected_skills = st.multiselect(
            f"Select {category.lower()}",
            skills,
            default=[s for s in current_skills if s in skills],
            key=f"skills_{category.replace(' ', '_')}"
        )
        all_skills.extend(selected_skills)
    
    additional_skills = st.text_area(
        "Other skills (comma-separated)",
        value=', '.join([s for s in current_skills if s not in [skill for skills in skills_categories.values() for skill in skills]])
    )
    
    # Learning Goals
    st.header("🎯 Learning Goals")
    
    # Handle time_commitment with proper checking
    current_time_commitment = user_data.get('time_commitment', '1-3 hours')
    time_options = ["1-3 hours", "4-7 hours", "8-15 hours", "16-25 hours", "25+ hours"]
    if pd.isna(current_time_commitment) or current_time_commitment == '' or current_time_commitment not in time_options:
        current_time_commitment = '1-3 hours'
    
    time_commitment = st.selectbox(
        "How much time can you dedicate to learning per week?",
        time_options,
        index=time_options.index(current_time_commitment)
    )
    
    # Handle learning_style with proper checking
    current_learning_style = user_data.get('learning_style', 'Mixed approach')
    style_options = ["Visual (videos, diagrams)", "Reading (articles, documentation)", "Hands-on (projects, coding)", "Audio (podcasts, lectures)", "Mixed approach"]
    if pd.isna(current_learning_style) or current_learning_style == '' or current_learning_style not in style_options:
        current_learning_style = 'Mixed approach'
    
    learning_style = st.selectbox(
        "Preferred Learning Style",
        style_options,
        index=style_options.index(current_learning_style)
    )
    
    short_term_goals = st.text_area(
        "Short-term goals (3-6 months)",
        value=user_data.get('short_term_goals', ''),
        placeholder="What do you want to achieve in the next 3-6 months?"
    )
    
    long_term_goals = st.text_area(
        "Long-term goals (1-2 years)",
        value=user_data.get('long_term_goals', ''),
        placeholder="What are your long-term career or learning objectives?"
    )
    
    # Submit button
    if st.form_submit_button("💾 Save Profile", type="primary", use_container_width=True):
        # Combine all interests
        all_interests = selected_interests.copy()
        if additional_interests.strip():
            all_interests.extend([i.strip() for i in additional_interests.split(',') if i.strip()])
        
        # Combine all skills
        if additional_skills.strip():
            all_skills.extend([s.strip() for s in additional_skills.split(',') if s.strip()])
        
        # Update user data
        updated_profile = {
            'name': name,
            'email': user_data['email'],
            'password': user_data['password'],  # Keep existing password
            'experience_level': experience_level,
            'age_group': age_group,
            'interests': ', '.join(all_interests),
            'skills': ', '.join(all_skills),
            'time_commitment': time_commitment,
            'learning_style': learning_style,
            'short_term_goals': short_term_goals,
            'long_term_goals': long_term_goals,
            'created_at': user_data.get('created_at', pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')),
            'updated_at': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if save_user_profile(updated_profile):
            st.session_state.user_data = updated_profile
            st.success("✅ Profile saved successfully!")
            st.balloons()
            
            # Show next steps
            st.markdown("### 🎉 What's Next?")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🎯 Get Project Suggestions", use_container_width=True):
                    st.switch_page("pages/3_Project_Suggestions.py")
            
            with col2:
                if st.button("🗺️ Create Learning Roadmap", use_container_width=True):
                    st.switch_page("pages/4_Learning_Roadmap.py")
            
            with col3:
                if st.button("💬 Chat with AI Mentor", use_container_width=True):
                    st.switch_page("pages/5_Chatbot_Mentor.py")
        else:
            st.error("Failed to save profile. Please try again.")

# Navigation
col1, col2 = st.columns(2)
with col1:
    if st.button("← Back to Home"):
        st.switch_page("app.py")

with col2:
    if st.button("Continue to Project Suggestions →", type="primary"):
        st.switch_page("pages/3_Project_Suggestions.py")
