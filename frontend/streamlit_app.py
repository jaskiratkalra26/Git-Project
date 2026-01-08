"""
Streamlit Frontend Application

This module runs the user interface for the GitHub Project Generator. 
It communicates with the backend API to handle authentication, 
repository listing, connection, and project generation.
"""

import streamlit as st
import httpx
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="Multimodal RAG Generator", 
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Project Generator from GitHub")

# --- Session State Management ---
# Initialize session state variables to persist data across re-runs
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "user_info" not in st.session_state:
    st.session_state.user_info = None
if "repos_list" not in st.session_state:
    st.session_state.repos_list = []

# --- Sidebar: Authentication ---
with st.sidebar:
    st.header("🔐 Authentication")
    
    if not st.session_state.access_token:
        st.markdown("""
        To use this app, you need a Personal Access Token from GitHub.
        [Generate one here](https://github.com/settings/tokens) with `repo` scope.
        """)
        
        token_input = st.text_input("GitHub Access Token", type="password")
        
        if st.button("Login", type="primary"):
            if token_input:
                try:
                    headers = {"Authorization": f"Bearer {token_input}"}
                    # We send an empty body as the token is in the header
                    res = httpx.post(f"{API_BASE_URL}/auth/verify-token", headers=headers, json={})
                    
                    if res.status_code == 200:
                        st.session_state.access_token = token_input
                        st.session_state.user_info = res.json()
                        st.success(f"Welcome, {st.session_state.user_info.get('github_username', 'User')}!")
                        st.rerun()
                    else:
                        st.error(f"Login Failed ({res.status_code}): {res.text}")
                except httpx.ConnectError:
                    st.error("❌ Could not connect to API. Is the backend running on port 8000?")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
    else:
        # Logged In State
        user = st.session_state.user_info
        st.success(f"Logged in as **{user.get('github_username')}**")
        st.caption(f"ID: {user.get('github_id')}")
        
        if st.button("Logout"):
            st.session_state.access_token = None
            st.session_state.user_info = None
            st.session_state.repos_list = []
            st.rerun()

# --- Main App Logic ---
if st.session_state.access_token:
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    
    tab1, tab2 = st.tabs(["📂 1. Connect Repository", "⚡ 2. Generate Analysis"])
    
    # === TAB 1: CONNECT ===
    with tab1:
        st.header("Select a Repository")
        st.markdown("Fetch your repositories from GitHub and connect one to the local database.")
        
        col_fetch, col_status = st.columns([1, 2])
        with col_fetch:
            if st.button("🔄 Fetch Repositories"):
                try:
                    with st.spinner("Fetching from GitHub..."):
                        response = httpx.get(f"{API_BASE_URL}/repos/", headers=headers)
                        if response.status_code == 200:
                            st.session_state.repos_list = response.json()
                            st.toast(f"Fetched {len(st.session_state.repos_list)} repositories")
                        else:
                            st.error(f"Failed to fetch: {response.text}")
                except Exception as e:
                    st.error(f"Connection Error: {e}")

        # Dropdown selection
        if st.session_state.repos_list:
            repo_map = {f"{r['full_name']} ({r['private'] and 'Private' or 'Public'})": r['id'] for r in st.session_state.repos_list}
            selected_name = st.selectbox("Choose a repository:", options=list(repo_map.keys()))
            
            if st.button("🔌 Connect Repository"):
                github_repo_id = repo_map[selected_name]
                payload = {"github_repo_id": github_repo_id}
                
                try:
                    with st.spinner("Connecting to Database..."):
                        # Send connect request to backend
                        conn_res = httpx.post(f"{API_BASE_URL}/repos/connect", headers=headers, json=payload)
                        
                        if conn_res.status_code == 200:
                            repo_data = conn_res.json()
                            st.success(f"✅ Connected successfully! (Local ID: {repo_data['id']})")
                            st.session_state.last_connected_id = repo_data['id']
                            st.info(f"Go to **Tab 2** to generate the project for Local ID: **{repo_data['id']}**")
                        else:
                            st.error(f"Connection failed: {conn_res.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.info("Click 'Fetch Repositories' to start.")

    # === TAB 2: GENERATE ===
    with tab2:
        st.header("Generate AI Analysis")
        st.markdown("Parse the README and extract structured information using Llama 3.2.")
        
        # Input for Repo ID (Default to last connected if available)
        default_id = st.session_state.get("last_connected_id", 0)
        repo_id_input = st.number_input("Local Repository ID", min_value=1, value=default_id if default_id else 1)
        
        if st.button("🚀 Run Analysis"):
            try:
                # Custom timeout for long LLM inference
                timeout = httpx.Timeout(300.0, connect=60.0) 
                
                with st.spinner("🧠 Reading README and analyzing with Llama 3.2... (This can take up to 5 mins)"):
                    gen_res = httpx.post(
                        f"{API_BASE_URL}/projects/generate/{repo_id_input}", 
                        headers=headers, 
                        timeout=timeout
                    )
                    
                    if gen_res.status_code == 200:
                        project = gen_res.json()
                        st.balloons()
                        
                        # --- Result Display ---
                        st.subheader(f"🏷️ {project.get('project_name', 'Untitled')}")
                        st.markdown(f"_{project.get('description', 'No description extracted')}_")
                        
                        st.markdown("### ✨ Extracted Features")
                        features = project.get('features', [])
                        if features:
                            for f in features:
                                st.success(f"🔹 {f}")
                        else:
                            st.warning("No specific features detected.")
                            
                        with st.expander("🔍 View Raw JSON Response"):
                            st.json(project)
                            
                    elif gen_res.status_code == 404:
                         st.error("Repository not found in DB. Did you connect it in Tab 1?")
                    else:
                        st.error(f"Generation Failed ({gen_res.status_code}): {gen_res.text}")
                        
            except httpx.ReadTimeout:
                st.error("⏰ The model took too long to respond. The server might still be processing it.")
            except Exception as e:
                st.error(f"Error: {e}")

else:
    # Landing Page State (Not logged in)
    st.info("👈 Please enter your GitHub Token in the sidebar to begin.")
    st.markdown("### Features")
    col1, col2, col3 = st.columns(3)
    col1.metric("Secure", "Token Auth")
    col2.metric("Smart", "Llama 3.2 Inside")
    col3.metric("Fast", "Direct GitHub Sync")

