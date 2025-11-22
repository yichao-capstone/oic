import streamlit as st
import os
from supabase import create_client, Client

# Load secrets from Streamlit secrets management
try:
    SUPABASE_URL = st.secrets["supabase"]["url"]
    SUPABASE_KEY = st.secrets["supabase"]["key"]
except KeyError as e:
    st.error(f"⚠️ Missing Supabase configuration: {e}. Please check your .streamlit/secrets.toml file.")
    st.stop()

@st.cache_resource
def get_supabase_client() -> Client:
    """获取 Supabase 客户端（不需要登录）"""
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except KeyError as e:
        st.error(f"⚠️ Missing Supabase configuration: {e}. Please check your .streamlit/secrets.toml file.")
        st.stop()

