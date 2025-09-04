import streamlit as st
import pandas as pd
from utils.auth import init_session_state, require_auth, is_authenticated
from utils.gemini_client import generate_learning_roadmap
from utils.data_manager import save_roadmap, load_user_roadmaps

st.set_page_config(page_title="Learning Roadmap - AI Learning Mentor", page_icon="🗺️")

init_session_state()
require_auth()

st.title("🗺️ Personalized Learning Roadmap")
st.markdown("Create a structured learning path tailored to your goals and timeline!")

if not is_authenticated():
    st.error("Please log in to access this page.")
    st.stop()

user_data = st.session_state.user_data

# Display existing roadmaps
existing_roadmaps = load_user_roadmaps(user_data['email'])
if not existing_roadmaps.empty:
    st.header("📚 Your Learning Roadmaps")
    
    for _, roadmap in existing_roadmaps.iterrows():
        with st.expander(f"🎯 {roadmap['title']} ({roadmap['created_at'][:10]})"):
            st.markdown(f"**Goal:** {roadmap['goal']}")
            st.markdown(f"**Timeline:** {roadmap['timeline']}")
            st.markdown(f"**Difficulty:** {roadmap['difficulty_level']}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"📖 View Full Roadmap", key=f"view_{roadmap['id']}"):
                    st.session_state.viewing_roadmap = roadmap.to_dict()
                    st.rerun()
            
            with col2:
                if st.button(f"💬 Discuss Roadmap", key=f"discuss_{roadmap['id']}"):
                    st.session_state.chat_context = f"I want to discuss my learning roadmap: {roadmap['title']}"
                    st.switch_page("pages/5_Chatbot_Mentor.py")

# Create new roadmap section
st.header("🎨 Create New Learning Roadmap")

# Check if coming from project suggestions
if st.session_state.get('selected_project_for_roadmap'):
    project = st.session_state.selected_project_for_roadmap
    st.info(f"Creating roadmap for project: **{project.get('title', 'Selected Project')}**")

with st.form("roadmap_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        if st.session_state.get('selected_project_for_roadmap'):
            goal = st.text_area(
                "Learning Goal",
                value=f"Complete the project: {st.session_state.selected_project_for_roadmap.get('title', '')} - {st.session_state.selected_project_for_roadmap.get('description', '')}",
                help="What specific skill or project do you want to learn?"
            )
        else:
            goal = st.text_area(
                "Learning Goal",
                value=user_data.get('short_term_goals', ''),
                placeholder="What specific skill, technology, or project do you want to learn?",
                help="Be specific about what you want to achieve"
            )
        
        timeline = st.selectbox(
            "Timeline",
            ["2 weeks", "1 month", "2 months", "3 months", "6 months", "1 year", "Custom"],
            index=2
        )
        
        if timeline == "Custom":
            custom_timeline = st.text_input("Specify custom timeline", placeholder="e.g., 10 weeks")
            timeline = custom_timeline if custom_timeline else "3 months"
    
    with col2:
        difficulty_level = st.selectbox(
            "Difficulty Level",
            ["Beginner", "Intermediate", "Advanced"],
            index=["Beginner", "Intermediate", "Advanced"].index(user_data.get('experience_level', 'Beginner'))
        )
        
        focus_areas = st.multiselect(
            "Focus Areas",
            [
                "Programming Fundamentals",
                "Web Development",
                "Data Science",
                "Machine Learning",
                "Mobile Development",
                "DevOps",
                "Database Design",
                "System Design",
                "UI/UX Design",
                "Project Management",
                "Soft Skills",
                "Industry Knowledge"
            ],
            default=["Programming Fundamentals"] if user_data.get('experience_level') == 'Beginner' else []
        )
        
        learning_style = st.selectbox(
            "Preferred Learning Style",
            ["Hands-on projects", "Theory then practice", "Mixed approach", "Video-based", "Reading-intensive"],
            index=0 if user_data.get('learning_style', '').startswith('Hands-on') else 2
        )
    
    time_per_week = st.selectbox(
        "Time commitment per week",
        ["1-3 hours", "4-7 hours", "8-15 hours", "16+ hours"],
        index=0 if not user_data.get('time_commitment') else 
        ["1-3 hours", "4-7 hours", "8-15 hours", "16+ hours"].index(
            user_data.get('time_commitment', '1-3 hours').replace('25+ hours', '16+ hours')
        )
    )
    
    prior_knowledge = st.text_area(
        "Current Knowledge & Skills",
        value=user_data.get('skills', ''),
        placeholder="What do you already know that's relevant to this goal?"
    )
    
    preferences = st.text_area(
        "Additional Preferences (optional)",
        placeholder="Any specific technologies, tools, or approaches you want to include/avoid?"
    )
    
    generate_roadmap_btn = st.form_submit_button("🚀 Generate Learning Roadmap", type="primary", use_container_width=True)

# Generate roadmap
if generate_roadmap_btn:
    with st.spinner("🤖 AI is creating your personalized learning roadmap..."):
        try:
            roadmap_data = {
                'user_data': user_data,
                'goal': goal,
                'timeline': timeline,
                'difficulty_level': difficulty_level,
                'focus_areas': focus_areas,
                'learning_style': learning_style,
                'time_per_week': time_per_week,
                'prior_knowledge': prior_knowledge,
                'preferences': preferences,
                'project_context': st.session_state.get('selected_project_for_roadmap')
            }
            
            roadmap = generate_learning_roadmap(roadmap_data)
            
            if roadmap:
                st.session_state.current_roadmap = roadmap
                
                # Save roadmap to CSV
                roadmap_record = {
                    'user_email': user_data['email'],
                    'title': roadmap.get('title', goal[:50]) if roadmap and isinstance(roadmap, dict) else goal[:50],
                    'goal': goal,
                    'timeline': timeline,
                    'difficulty_level': difficulty_level,
                    'content': str(roadmap) if roadmap else '',
                    'created_at': st.session_state.get('current_time', ''),
                    'progress': 0
                }
                
                roadmap_id = save_roadmap(roadmap_record)
                if roadmap_id:
                    st.session_state.current_roadmap['id'] = roadmap_id
                
                st.success("✅ Roadmap generated successfully!")
                
                # Clear project context after use
                if 'selected_project_for_roadmap' in st.session_state:
                    del st.session_state.selected_project_for_roadmap
                
                st.rerun()
            else:
                st.error("Failed to generate roadmap. Please try again.")
        
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Display current roadmap
if st.session_state.get('current_roadmap') or st.session_state.get('viewing_roadmap'):
    roadmap = st.session_state.get('current_roadmap') or st.session_state.get('viewing_roadmap')
    
    st.header("📖 Your Learning Roadmap")
    
    # Roadmap header
    if roadmap and roadmap.get('title'):
        st.markdown(f"### 🎯 {roadmap['title']}")
    
    if roadmap and roadmap.get('overview'):
        st.markdown(f"**Overview:** {roadmap['overview']}")
    
    # Add learning videos section for roadmaps
    if roadmap and roadmap.get('title'):
        st.subheader("📺 Recommended Learning Videos")
        
        # Video recommendations for roadmap topics
        learning_videos = [
            {
                "title": "Study Tips for Effective Learning",
                "video_id": "IlU-zDU6aQ0",
                "description": "Master effective study techniques"
            },
            {
                "title": "Project Management Basics",
                "video_id": "wbhXHKHPmXs",
                "description": "Learn to manage your learning projects"
            },
            {
                "title": "Goal Setting and Achievement",
                "video_id": "TQMbvJNRpLE",
                "description": "Set and achieve your learning goals"
            }
        ]
        
        video_cols = st.columns(len(learning_videos))
        for i, video in enumerate(learning_videos):
            with video_cols[i]:
                with st.container():
                    st.markdown(f"**{video['title']}**")
                    st.video(f"https://www.youtube.com/watch?v={video['video_id']}")
                    st.caption(video['description'])
        
        st.markdown("---")
    
    # Display phases/milestones
    if roadmap and roadmap.get('phases'):
        st.subheader("📋 Learning Phases")
        
        for i, phase in enumerate(roadmap['phases'], 1):
            with st.expander(f"Phase {i}: {phase.get('title', f'Phase {i}')} ({phase.get('duration', 'TBD')})", expanded=i==1):
                st.markdown(f"**Objective:** {phase.get('objective', 'Not specified')}")
                
                if phase.get('topics'):
                    st.markdown("**Topics to Learn:**")
                    for topic in phase['topics']:
                        st.markdown(f"• {topic}")
                
                if phase.get('activities'):
                    st.markdown("**Activities:**")
                    for activity in phase['activities']:
                        st.markdown(f"• {activity}")
                
                if phase.get('resources'):
                    st.markdown("**Recommended Resources:**")
                    for resource in phase['resources']:
                        st.markdown(f"• {resource}")
                
                if phase.get('milestones'):
                    st.markdown("**Milestones:**")
                    for j, milestone in enumerate(phase['milestones']):
                        completed = st.checkbox(f"{milestone}", key=f"milestone_phase_{i}_item_{j}")
                        if completed:
                            st.success("✅ Completed!")
                
                # Phase action buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"💬 Get Help with Phase {i}", key=f"help_{i}"):
                        st.session_state.chat_context = f"I need help with Phase {i} of my learning roadmap: {phase.get('title', f'Phase {i}')}"
                        st.switch_page("pages/5_Chatbot_Mentor.py")
                
                with col2:
                    if st.button(f"✅ Mark Phase {i} Complete", key=f"complete_{i}"):
                        st.success(f"Phase {i} marked as complete!")
                        st.balloons()
    
    # Additional resources
    if roadmap and roadmap.get('additional_resources'):
        st.subheader("📚 Additional Resources")
        for resource in roadmap['additional_resources']:
            st.markdown(f"• {resource}")
    
    # Tips and recommendations
    if roadmap and roadmap.get('tips'):
        st.subheader("💡 Study Tips")
        for tip in roadmap['tips']:
            st.markdown(f"• {tip}")
    
    # Action buttons
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Track Progress"):
            st.switch_page("pages/6_Progress_Tracking.py")
    
    with col2:
        if st.button("💬 Discuss with Mentor"):
            title = roadmap.get('title', 'My Roadmap') if roadmap else 'My Roadmap'
            st.session_state.chat_context = f"I want to discuss my learning roadmap: {title}"
            st.switch_page("pages/5_Chatbot_Mentor.py")
    
    with col3:
        if st.button("🎯 New Project Ideas"):
            st.switch_page("pages/3_Project_Suggestions.py")
    
    # Clear viewing roadmap
    if st.button("🔄 Create New Roadmap"):
        if 'viewing_roadmap' in st.session_state:
            del st.session_state.viewing_roadmap
        if 'current_roadmap' in st.session_state:
            del st.session_state.current_roadmap
        st.rerun()

# Navigation
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    if st.button("← Back to Projects"):
        st.switch_page("pages/3_Project_Suggestions.py")

with col2:
    if st.button("💬 Chat with Mentor"):
        st.switch_page("pages/5_Chatbot_Mentor.py")
