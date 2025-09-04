# AI Learning Mentor

## Overview

AI Learning Mentor is a personalized AI-powered learning companion built with Streamlit. The application provides users with intelligent project suggestions, customized learning roadmaps, and 24/7 AI mentorship through an integrated chatbot. The system tracks user progress and adapts recommendations based on individual learning profiles, experience levels, and interests.

The application follows a multi-page architecture where users can register, set up detailed profiles, generate AI-powered project suggestions, create learning roadmaps, chat with an AI mentor, and track their learning progress through an interactive dashboard.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit-based web application with multi-page navigation
- **UI Components**: Custom CSS styling with feature cards, hero sections, and responsive layouts
- **Page Structure**: Main app.py landing page with dedicated pages for login, profile setup, project suggestions, roadmaps, chatbot, and progress tracking
- **State Management**: Streamlit session state for user authentication, data persistence across pages, and chat message history

### Backend Architecture
- **Authentication System**: Custom email/password authentication with SHA256 password hashing
- **Data Processing**: Pandas-based data manipulation for user profiles, project suggestions, and progress tracking
- **AI Integration**: Google Gemini API client for generating personalized project suggestions, learning roadmaps, and chatbot interactions
- **File-based Storage**: CSV files for persistent data storage across all application entities

### Data Storage Solutions
- **Storage Type**: File-based CSV storage system
- **Data Files**: 
  - users.csv for authentication and profile data
  - roadmaps.csv for learning path storage
  - interactions.csv for user activity tracking
  - chat_history.csv for conversation persistence
  - progress.csv for achievement tracking
- **Data Management**: Centralized data manager utility with functions for loading, saving, and initializing data files
- **User Data**: Comprehensive profile system including experience level, interests, skills, learning preferences, and goals

### Authentication and Authorization
- **Authentication Method**: Email and password-based system with hashed passwords
- **Session Management**: Streamlit session state for maintaining authentication status
- **Access Control**: Page-level authentication requirements with automatic redirection to login
- **User Registration**: Multi-step registration with profile completion

## External Dependencies

### AI Services
- **Google Gemini API**: Primary AI service for generating project suggestions, learning roadmaps, and powering the chatbot mentor functionality
- **API Configuration**: Environment variable-based API key management

### Python Libraries
- **streamlit**: Core web application framework for UI and routing
- **pandas**: Data manipulation and CSV file operations
- **plotly**: Interactive charts and visualizations for progress tracking dashboard
- **google-genai**: Official Google Gemini API client library

### Data Visualization
- **Plotly Express & Graph Objects**: Interactive charts for learning progress visualization, activity tracking, and achievement metrics

### Development Environment
- **File System**: Local CSV-based storage requiring read/write permissions to data directory
- **Environment Variables**: GEMINI_API_KEY for AI service authentication