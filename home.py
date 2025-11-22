import streamlit as st

st.set_page_config(
    page_title="OIC Education - Home",
    layout="wide"
)

# 自定义样式
st.markdown("""
<style>
    .hero-section {
        background: linear-gradient(135deg, #007958 0%, #00a876 100%);
        padding: 4rem 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 3rem;
    }
    .hero-title {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    .hero-subtitle {
        font-size: 1.5rem;
        opacity: 0.95;
        margin-bottom: 2rem;
    }
    .service-card {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        height: 100%;
        border: 1px solid #e0e0e0;
        display: flex;
        flex-direction: column;
        min-height: 280px;
    }
    .service-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 16px rgba(0,121,88,0.2);
    }
    .service-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        text-align: center;
        flex-shrink: 0;
    }
    .service-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #007958;
        margin-bottom: 1rem;
        text-align: center;
        flex-shrink: 0;
    }
    .service-description {
        color: #666;
        line-height: 1.6;
        text-align: center;
        flex-grow: 1;
        display: flex;
        align-items: center;
    }
    .stats-container {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
    }
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        color: #007958;
    }
    .stat-label {
        font-size: 1rem;
        color: #666;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class="hero-section">
    <div class="hero-title">Welcome to OIC Education</div>
    <div class="hero-subtitle">Your Pathway to Australian Higher Education</div>
    <p style="font-size: 1.2rem; opacity: 0.9;">Discover your perfect university match with AI-powered career and study recommendations</p>
</div>
""", unsafe_allow_html=True)

# Main Services Section
st.markdown("## 🎓 Our Services")

# 使用 equal heights 确保列对齐
st.markdown("""
<style>
    .stColumn > div {
        display: flex;
        flex-direction: column;
    }
    .stColumn > div > div {
        flex: 1;
    }
</style>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="service-card">
        <div class="service-icon">📊</div>
        <div class="service-title">Personal Survey</div>
        <div class="service-description">
            Complete our comprehensive personality and career assessment to discover your ideal study path. 
            Get personalized insights based on RIASEC and HLAFPS models.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="service-card">
        <div class="service-icon">📚</div>
        <div class="service-title">Australian Standard Classification of Education</div>
        <div class="service-description">
            Browse and explore Australian Standard Classification of Education fields. 
            Navigate through broad, narrow, and detailed education classifications to find your ideal study area.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="service-card">
        <div class="service-icon">🎯</div>
        <div class="service-title">University Recommendation</div>
        <div class="service-description">
            Get AI-powered university and course recommendations tailored to your profile. 
            Discover the best Australian universities for your career goals.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Quick Start Section
st.markdown("## 🚀 Quick Start")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ### Get Started in 3 Simple Steps
    
    1. **Complete Your Profile** 📝
       - Take our comprehensive personality and career assessment
       - Get insights into your interests, values, and working style
    
    2. **Explore Education Fields** 🔍
       - Browse ASCED education classifications
       - Understand different study fields and their pathways
    
    3. **Find Your University** 🎓
       - Receive personalized university and course recommendations
       - Get detailed information about programs, entry requirements, and career outcomes
    
    **Ready to begin your journey?** Use the navigation menu to start with Personal Survey!
    """)

with col2:
    st.markdown("""
    <div class="stats-container">
        <div class="stat-number">1000+</div>
        <div class="stat-label">Students Helped</div>
    </div>
    <br>
    <div class="stats-container">
        <div class="stat-number">50+</div>
        <div class="stat-label">Universities</div>
    </div>
    <br>
    <div class="stats-container">
        <div class="stat-number">200+</div>
        <div class="stat-label">Career Paths</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Features Section
st.markdown("## ✨ Key Features")

feature_col1, feature_col2 = st.columns(2)

with feature_col1:
    st.markdown("""
    ### 🧠 AI-Powered Analysis
    - Advanced personality profiling using RIASEC and HLAFPS models
    - Machine learning algorithms for accurate career matching
    - Personalized recommendations based on your unique profile
    
    ### 📚 Comprehensive Database
    - Complete ASCED education classification system
    - Australian university and course information
    - Education field mapping and study pathways
    """)

with feature_col2:
    st.markdown("""
    ### 🎯 Personalized Guidance
    - Tailored study field recommendations
    - University and course matching
    - Career path exploration and planning
    
    ### 🌏 Australian Focus
    - Specialized knowledge of Australian education system
    - Australian Standard Classification of Education (ASCED) classification expertise
    - Local university and industry insights
    """)

st.markdown("<br>", unsafe_allow_html=True)

# Call to Action
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem;">
    <h2>Ready to Discover Your Future?</h2>
    <p style="font-size: 1.2rem; color: #666; margin-bottom: 2rem;">
        Start your journey today with our comprehensive assessment and get personalized recommendations
    </p>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; color: #666;">
    <p><strong>OIC Education</strong> - Your trusted partner in Australian higher education</p>
    <p>© 2024 OIC Education. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)

