import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.auth import init_session_state, require_auth, is_authenticated
from utils.data_manager import (
    load_user_roadmaps, load_chat_history, load_user_interactions, 
    save_progress_entry, load_progress_entries
)

st.set_page_config(page_title="Progress Tracking - AI Learning Mentor", page_icon="📊")

init_session_state()
require_auth()

st.title("📊 Progress Tracking Dashboard")
st.markdown("Monitor your learning journey and celebrate your achievements!")

if not is_authenticated():
    st.error("Please log in to access this page.")
    st.stop()

user_data = st.session_state.user_data
user_email = user_data['email']

# Load user data
roadmaps = load_user_roadmaps(user_email)
chat_history = load_chat_history(user_email)
interactions = load_user_interactions(user_email)
progress_entries = load_progress_entries(user_email)

# Overview cards
st.header("📈 Learning Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="🗺️ Learning Roadmaps",
        value=len(roadmaps) if not roadmaps.empty else 0,
        help="Total number of learning roadmaps created"
    )

with col2:
    st.metric(
        label="💬 Mentor Conversations",
        value=len(chat_history[chat_history['role'] == 'user']) if not chat_history.empty else 0,
        help="Number of questions asked to AI mentor"
    )

with col3:
    st.metric(
        label="🎯 Projects Explored",
        value=len(interactions[interactions['interaction_type'] == 'project_suggestion']) if not interactions.empty else 0,
        help="Number of times you've used project suggestions"
    )

with col4:
    total_progress = len(progress_entries) if not progress_entries.empty else 0
    st.metric(
        label="✅ Progress Entries",
        value=total_progress,
        help="Number of progress updates logged"
    )

# Activity timeline
if not interactions.empty or not chat_history.empty:
    st.header("📅 Activity Timeline")
    
    # Combine interactions and chat for timeline
    timeline_data = []
    
    if not interactions.empty:
        for _, interaction in interactions.iterrows():
            try:
                timestamp_date = pd.to_datetime(interaction['timestamp']).date() if pd.notna(interaction['timestamp']) else datetime.now().date()
            except:
                timestamp_date = datetime.now().date()
            timeline_data.append({
                'date': timestamp_date,
                'activity': str(interaction['interaction_type']).replace('_', ' ').title(),
                'details': interaction['details'],
                'type': 'interaction'
            })
    
    if not chat_history.empty:
        chat_days = chat_history.groupby(pd.to_datetime(chat_history['timestamp']).dt.date).size()
        for date, count in chat_days.items():
            timeline_data.append({
                'date': date,
                'activity': 'Mentor Chat',
                'details': f'{count} messages exchanged',
                'type': 'chat'
            })
    
    if timeline_data:
        timeline_df = pd.DataFrame(timeline_data)
        timeline_df = timeline_df.sort_values('date', ascending=False)
        
        # Display recent activities
        st.subheader("🕒 Recent Activities")
        for _, activity in timeline_df.head(10).iterrows():
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{activity['activity']}**")
                    st.markdown(f"{activity['details']}")
                with col2:
                    st.markdown(f"*{activity['date']}*")
                st.markdown("---")

# Progress logging
st.header("📝 Log Your Progress")

with st.form("progress_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        progress_type = st.selectbox(
            "What did you work on?",
            [
                "Completed a learning module",
                "Finished a project milestone",
                "Learned a new concept",
                "Solved a coding problem",
                "Read documentation/tutorial",
                "Watched educational content",
                "Practiced coding exercises",
                "Attended a course/workshop",
                "Other"
            ]
        )
        
        if progress_type == "Other":
            custom_type = st.text_input("Specify activity type")
            progress_type = custom_type if custom_type else "Other activity"
    
    with col2:
        time_spent = st.selectbox(
            "Time spent",
            ["15 minutes", "30 minutes", "1 hour", "2 hours", "3 hours", "4+ hours"]
        )
        
        difficulty_rating = st.selectbox(
            "How challenging was it?",
            ["😊 Easy", "🤔 Medium", "😅 Hard", "🤯 Very Hard"]
        )
    
    progress_description = st.text_area(
        "Describe your progress",
        placeholder="What did you learn or accomplish? Any challenges or breakthroughs?"
    )
    
    skills_gained = st.text_input(
        "Skills/Technologies learned (comma-separated)",
        placeholder="e.g., Python, React, SQL, Problem-solving"
    )
    
    next_steps = st.text_input(
        "What's next?",
        placeholder="What do you plan to work on next?"
    )
    
    if st.form_submit_button("✅ Log Progress", type="primary", use_container_width=True):
        if progress_description.strip():
            progress_entry = {
                'user_email': user_email,
                'progress_type': progress_type,
                'description': progress_description,
                'time_spent': time_spent,
                'difficulty_rating': difficulty_rating,
                'skills_gained': skills_gained,
                'next_steps': next_steps,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            if save_progress_entry(progress_entry):
                st.success("🎉 Progress logged successfully!")
                st.balloons()
                st.rerun()
            else:
                st.error("Failed to save progress. Please try again.")
        else:
            st.error("Please describe your progress.")

# Progress history
if not progress_entries.empty:
    st.header("📚 Progress History")
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        date_filter = st.date_input(
            "Filter by date (from)",
            value=datetime.now().date() - timedelta(days=30),
            max_value=datetime.now().date()
        )
    
    with col2:
        type_filter = st.selectbox(
            "Filter by activity type",
            ["All"] + list(progress_entries['progress_type'].unique())
        )
    
    # Apply filters
    filtered_entries = progress_entries.copy()
    
    # Date filter
    filtered_entries['date'] = pd.to_datetime(filtered_entries['timestamp']).dt.date
    filtered_entries = filtered_entries[filtered_entries['date'] >= date_filter]
    
    # Type filter
    if type_filter != "All":
        filtered_entries = filtered_entries[filtered_entries['progress_type'] == type_filter]
    
    if len(filtered_entries) > 0:
        # Progress visualization
        st.subheader("📈 Learning Patterns")
        
        # Progress over time
        daily_progress = filtered_entries.groupby('date').size().reset_index(name='entries')
        
        if len(daily_progress) > 1:
            fig = px.line(
                daily_progress, 
                x='date', 
                y='entries',
                title='Daily Learning Activities',
                labels={'entries': 'Number of Activities', 'date': 'Date'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Activity type distribution
        type_counts = filtered_entries['progress_type'].value_counts()
        if len(type_counts) > 1:
            fig = px.pie(
                values=type_counts.values,
                names=type_counts.index,
                title='Activity Type Distribution'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Time investment analysis
        time_mapping = {
            "15 minutes": 0.25, "30 minutes": 0.5, "1 hour": 1,
            "2 hours": 2, "3 hours": 3, "4+ hours": 4
        }
        
        filtered_entries['time_hours'] = filtered_entries['time_spent'].map(time_mapping).fillna(1.0)
        total_time = filtered_entries['time_hours'].sum()
        avg_time = filtered_entries['time_hours'].mean()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("⏰ Total Learning Time", f"{total_time:.1f} hours")
        with col2:
            st.metric("📊 Average Session", f"{avg_time:.1f} hours")
        
        # Recent progress entries
        st.subheader("📖 Recent Progress Entries")
        
        for _, entry in filtered_entries.head(10).iterrows():
            with st.expander(f"🎯 {entry['progress_type']} - {entry['timestamp'][:10]}"):
                st.markdown(f"**Description:** {entry['description']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Time Spent:** {entry['time_spent']}")
                    st.markdown(f"**Difficulty:** {entry['difficulty_rating']}")
                
                with col2:
                    if entry.get('skills_gained'):
                        st.markdown(f"**Skills Gained:** {entry['skills_gained']}")
                    if entry.get('next_steps'):
                        st.markdown(f"**Next Steps:** {entry['next_steps']}")
    else:
        st.info("No progress entries found for the selected filters.")

else:
    st.info("📝 No progress logged yet. Start by logging your first learning activity above!")

# Learning insights
st.header("💡 Learning Insights")

insights = []

if not progress_entries.empty:
    recent_entries = progress_entries.tail(10)
    
    # Most common activity
    most_common = progress_entries['progress_type'].mode().iloc[0] if not progress_entries.empty else None
    if most_common:
        insights.append(f"🎯 Your most common learning activity is: **{most_common}**")
    
    # Learning streak
    if len(progress_entries) > 0:
        progress_entries['date'] = pd.to_datetime(progress_entries['timestamp']).dt.date
        unique_dates = sorted(progress_entries['date'].unique(), reverse=True)
        
        streak = 0
        current_date = datetime.now().date()
        
        for date in unique_dates:
            if (current_date - date).days <= streak:
                streak += 1
                current_date = date
            else:
                break
        
        if streak > 1:
            insights.append(f"🔥 You have a {streak}-day learning streak! Keep it up!")
    
    # Skills analysis
    all_skills = []
    for skills_str in progress_entries['skills_gained'].dropna():
        all_skills.extend([skill.strip() for skill in skills_str.split(',') if skill.strip()])
    
    if all_skills:
        skill_counts = pd.Series(all_skills).value_counts()
        top_skill = skill_counts.index[0]
        insights.append(f"🚀 You've been focusing a lot on: **{top_skill}**")

if not roadmaps.empty:
    insights.append(f"🗺️ You have **{len(roadmaps)}** learning roadmap(s) to guide your journey")

if not chat_history.empty:
    chat_count = len(chat_history[chat_history['role'] == 'user'])
    insights.append(f"🤖 You've asked **{chat_count}** questions to your AI mentor")

if insights:
    for insight in insights:
        st.success(insight)
else:
    st.info("Keep using the app to generate personalized learning insights!")

# Action buttons
st.header("🎯 Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("💬 Ask AI Mentor", use_container_width=True):
        st.session_state.chat_context = "Can you help me analyze my learning progress and suggest next steps?"
        st.switch_page("pages/5_Chatbot_Mentor.py")

with col2:
    if st.button("🎯 Get New Projects", use_container_width=True):
        st.switch_page("pages/3_Project_Suggestions.py")

with col3:
    if st.button("🗺️ Update Roadmap", use_container_width=True):
        st.switch_page("pages/4_Learning_Roadmap.py")

# Navigation
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    if st.button("← Back to Chat"):
        st.switch_page("pages/5_Chatbot_Mentor.py")

with col2:
    if st.button("🏠 Home"):
        st.switch_page("app.py")
