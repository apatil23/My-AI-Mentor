import pandas as pd
import os
import csv
from datetime import datetime
from typing import Dict, Any, List

# File paths for data storage
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.csv")
ROADMAPS_FILE = os.path.join(DATA_DIR, "roadmaps.csv")
INTERACTIONS_FILE = os.path.join(DATA_DIR, "interactions.csv")
CHAT_HISTORY_FILE = os.path.join(DATA_DIR, "chat_history.csv")
PROGRESS_FILE = os.path.join(DATA_DIR, "progress.csv")

def init_data_files():
    """Initialize CSV files if they don't exist."""
    # Create data directory if it doesn't exist
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Initialize users file
    if not os.path.exists(USERS_FILE):
        users_columns = [
            'name', 'email', 'password', 'experience_level', 'age_group',
            'interests', 'skills', 'time_commitment', 'learning_style',
            'short_term_goals', 'long_term_goals', 'created_at', 'updated_at'
        ]
        users_df = pd.DataFrame(columns=users_columns)
        users_df.to_csv(USERS_FILE, index=False)
    
    # Initialize roadmaps file
    if not os.path.exists(ROADMAPS_FILE):
        roadmaps_columns = [
            'id', 'user_email', 'title', 'goal', 'timeline', 'difficulty_level',
            'content', 'progress', 'created_at', 'updated_at'
        ]
        roadmaps_df = pd.DataFrame(columns=roadmaps_columns)
        roadmaps_df.to_csv(ROADMAPS_FILE, index=False)
    
    # Initialize interactions file
    if not os.path.exists(INTERACTIONS_FILE):
        interactions_columns = [
            'id', 'user_email', 'interaction_type', 'details', 'timestamp'
        ]
        interactions_df = pd.DataFrame(columns=interactions_columns)
        interactions_df.to_csv(INTERACTIONS_FILE, index=False)
    
    # Initialize chat history file
    if not os.path.exists(CHAT_HISTORY_FILE):
        chat_columns = [
            'id', 'user_email', 'role', 'content', 'timestamp'
        ]
        chat_df = pd.DataFrame(columns=chat_columns)
        chat_df.to_csv(CHAT_HISTORY_FILE, index=False)
    
    # Initialize progress file
    if not os.path.exists(PROGRESS_FILE):
        progress_columns = [
            'id', 'user_email', 'progress_type', 'description', 'time_spent',
            'difficulty_rating', 'skills_gained', 'next_steps', 'timestamp'
        ]
        progress_df = pd.DataFrame(columns=progress_columns)
        progress_df.to_csv(PROGRESS_FILE, index=False)

def load_users() -> pd.DataFrame:
    """Load users from CSV file."""
    try:
        df = pd.read_csv(USERS_FILE)
        # Ensure all string columns don't have NaN values
        string_columns = ['name', 'email', 'experience_level', 'age_group', 'interests', 'skills', 'learning_style', 'short_term_goals', 'long_term_goals']
        for col in string_columns:
            if col in df.columns:
                df[col] = df[col].fillna('')
        return df
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame()

def save_user(user_data: Dict[str, Any]) -> bool:
    """Save a new user to CSV file."""
    try:
        users_df = load_users()
        
        # Create new user record
        new_user = pd.DataFrame([user_data])
        
        # Append to existing users
        users_df = pd.concat([users_df, new_user], ignore_index=True)
        
        # Save to CSV
        users_df.to_csv(USERS_FILE, index=False)
        return True
    
    except Exception as e:
        print(f"Error saving user: {str(e)}")
        return False

def save_user_profile(user_data: Dict[str, Any]) -> bool:
    """Update user profile in CSV file."""
    try:
        users_df = load_users()
        
        if users_df.empty:
            return False
        
        # Find user by email
        user_index = users_df[users_df['email'] == user_data['email']].index
        
        if len(user_index) == 0:
            return False
        
        # Update user data
        for key, value in user_data.items():
            if key in users_df.columns:
                users_df.loc[user_index[0], key] = value
        
        # Save updated data
        users_df.to_csv(USERS_FILE, index=False)
        return True
    
    except Exception as e:
        print(f"Error updating user profile: {str(e)}")
        return False

def save_roadmap(roadmap_data: Dict[str, Any]) -> int:
    """Save a learning roadmap to CSV file."""
    try:
        roadmaps_df = pd.read_csv(ROADMAPS_FILE) if os.path.exists(ROADMAPS_FILE) else pd.DataFrame()
        
        # Generate ID
        roadmap_id = len(roadmaps_df) + 1
        roadmap_data['id'] = roadmap_id
        roadmap_data['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        roadmap_data['updated_at'] = roadmap_data['created_at']
        
        # Ensure all string fields are properly set
        for key in ['title', 'content', 'goal']:
            if key not in roadmap_data or pd.isna(roadmap_data[key]):
                roadmap_data[key] = ''
        
        # Create new roadmap record
        new_roadmap = pd.DataFrame([roadmap_data])
        
        # Append to existing roadmaps
        roadmaps_df = pd.concat([roadmaps_df, new_roadmap], ignore_index=True)
        
        # Save to CSV
        roadmaps_df.to_csv(ROADMAPS_FILE, index=False)
        return roadmap_id
    
    except Exception as e:
        print(f"Error saving roadmap: {str(e)}")
        return 0

def load_user_roadmaps(user_email: str) -> pd.DataFrame:
    """Load roadmaps for a specific user."""
    try:
        roadmaps_df = pd.read_csv(ROADMAPS_FILE) if os.path.exists(ROADMAPS_FILE) else pd.DataFrame()
        
        if roadmaps_df.empty:
            return pd.DataFrame()
        
        # Ensure string columns don't have NaN values
        string_columns = ['title', 'content', 'goal']
        for col in string_columns:
            if col in roadmaps_df.columns:
                roadmaps_df[col] = roadmaps_df[col].fillna('')
        
        return roadmaps_df[roadmaps_df['user_email'] == user_email]
    
    except Exception as e:
        print(f"Error loading user roadmaps: {str(e)}")
        return pd.DataFrame()

def save_user_interaction(interaction_data: Dict[str, Any]) -> bool:
    """Save user interaction to CSV file."""
    try:
        interactions_df = pd.read_csv(INTERACTIONS_FILE) if os.path.exists(INTERACTIONS_FILE) else pd.DataFrame()
        
        # Generate ID
        interaction_data['id'] = len(interactions_df) + 1
        interaction_data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Create new interaction record
        new_interaction = pd.DataFrame([interaction_data])
        
        # Append to existing interactions
        interactions_df = pd.concat([interactions_df, new_interaction], ignore_index=True)
        
        # Save to CSV
        interactions_df.to_csv(INTERACTIONS_FILE, index=False)
        return True
    
    except Exception as e:
        print(f"Error saving interaction: {str(e)}")
        return False

def load_user_interactions(user_email: str) -> pd.DataFrame:
    """Load interactions for a specific user."""
    try:
        interactions_df = pd.read_csv(INTERACTIONS_FILE) if os.path.exists(INTERACTIONS_FILE) else pd.DataFrame()
        
        if interactions_df.empty:
            return pd.DataFrame()
        
        # Ensure string columns don't have NaN values
        string_columns = ['interaction_type', 'details']
        for col in string_columns:
            if col in interactions_df.columns:
                interactions_df[col] = interactions_df[col].fillna('')
        
        return interactions_df[interactions_df['user_email'] == user_email]
    
    except Exception as e:
        print(f"Error loading user interactions: {str(e)}")
        return pd.DataFrame()

def save_chat_message(message_data: Dict[str, Any]) -> bool:
    """Save chat message to CSV file."""
    try:
        chat_df = pd.read_csv(CHAT_HISTORY_FILE) if os.path.exists(CHAT_HISTORY_FILE) else pd.DataFrame()
        
        # Generate ID
        message_data['id'] = len(chat_df) + 1
        message_data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Create new message record
        new_message = pd.DataFrame([message_data])
        
        # Append to existing messages
        chat_df = pd.concat([chat_df, new_message], ignore_index=True)
        
        # Save to CSV (keep only last 1000 messages to prevent file from growing too large)
        chat_df = chat_df.tail(1000)
        chat_df.to_csv(CHAT_HISTORY_FILE, index=False)
        return True
    
    except Exception as e:
        print(f"Error saving chat message: {str(e)}")
        return False

def load_chat_history(user_email: str) -> pd.DataFrame:
    """Load chat history for a specific user."""
    try:
        chat_df = pd.read_csv(CHAT_HISTORY_FILE) if os.path.exists(CHAT_HISTORY_FILE) else pd.DataFrame()
        
        if chat_df.empty:
            return pd.DataFrame()
        
        # Ensure string columns don't have NaN values
        string_columns = ['role', 'content']
        for col in string_columns:
            if col in chat_df.columns:
                chat_df[col] = chat_df[col].fillna('')
        
        return chat_df[chat_df['user_email'] == user_email]
    
    except Exception as e:
        print(f"Error loading chat history: {str(e)}")
        return pd.DataFrame()

def save_progress_entry(progress_data: Dict[str, Any]) -> bool:
    """Save progress entry to CSV file."""
    try:
        progress_df = pd.read_csv(PROGRESS_FILE) if os.path.exists(PROGRESS_FILE) else pd.DataFrame()
        
        # Generate ID
        progress_data['id'] = len(progress_df) + 1
        if 'timestamp' not in progress_data:
            progress_data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Create new progress record
        new_progress = pd.DataFrame([progress_data])
        
        # Append to existing progress
        progress_df = pd.concat([progress_df, new_progress], ignore_index=True)
        
        # Save to CSV
        progress_df.to_csv(PROGRESS_FILE, index=False)
        return True
    
    except Exception as e:
        print(f"Error saving progress entry: {str(e)}")
        return False

def load_progress_entries(user_email: str) -> pd.DataFrame:
    """Load progress entries for a specific user."""
    try:
        progress_df = pd.read_csv(PROGRESS_FILE) if os.path.exists(PROGRESS_FILE) else pd.DataFrame()
        
        if progress_df.empty:
            return pd.DataFrame()
        
        # Ensure string columns don't have NaN values
        string_columns = ['progress_type', 'details', 'time_spent']
        for col in string_columns:
            if col in progress_df.columns:
                progress_df[col] = progress_df[col].fillna('')
        
        user_progress = progress_df[progress_df['user_email'] == user_email]
        if not user_progress.empty and len(user_progress) > 0:
            try:
                return user_progress.sort_values('timestamp', ascending=False)
            except:
                return user_progress
        return pd.DataFrame()
    
    except Exception as e:
        print(f"Error loading progress entries: {str(e)}")
        return pd.DataFrame()

def get_user_stats(user_email: str) -> Dict[str, Any]:
    """Get comprehensive stats for a user."""
    try:
        stats = {
            'total_roadmaps': 0,
            'total_interactions': 0,
            'total_chat_messages': 0,
            'total_progress_entries': 0,
            'join_date': None,
            'last_activity': None
        }
        
        # Load user data
        users_df = load_users()
        user_data = users_df[users_df['email'] == user_email]
        
        if not user_data.empty:
            stats['join_date'] = user_data.iloc[0]['created_at']
        
        # Count roadmaps
        roadmaps_df = load_user_roadmaps(user_email)
        stats['total_roadmaps'] = len(roadmaps_df)
        
        # Count interactions
        interactions_df = load_user_interactions(user_email)
        stats['total_interactions'] = len(interactions_df)
        
        # Count chat messages
        chat_df = load_chat_history(user_email)
        stats['total_chat_messages'] = len(chat_df[chat_df['role'] == 'user'])
        
        # Count progress entries
        progress_df = load_progress_entries(user_email)
        stats['total_progress_entries'] = len(progress_df)
        
        # Find last activity
        last_activities = []
        
        if not interactions_df.empty:
            last_activities.append(interactions_df['timestamp'].max())
        
        if not chat_df.empty:
            last_activities.append(chat_df['timestamp'].max())
        
        if not progress_df.empty:
            last_activities.append(progress_df['timestamp'].max())
        
        if last_activities:
            stats['last_activity'] = max(last_activities)
        
        return stats
    
    except Exception as e:
        print(f"Error getting user stats: {str(e)}")
        return {}
