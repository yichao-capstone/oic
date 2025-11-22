from __future__ import annotations
import streamlit as st
import json
import pandas as pd
import os
from typing import List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

# Load secrets from Streamlit secrets management
try:
    OPENAI_API_KEY = st.secrets["openai"]["api_key"]
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
except KeyError as e:
    st.error(f"⚠️ Missing secret configuration: {e}. Please check your .streamlit/secrets.toml file.")
    st.stop()

# 页面标题
st.title("Universities")
st.markdown("Explore universities from the UK, Canada, Australia, and New Zealand")

# 初始化 session state
if "selected_country" not in st.session_state:
    st.session_state.selected_country = None

# 国家卡片样式
st.markdown("""
<style>
.country-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 15px;
    padding: 2rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    border: 3px solid transparent;
    height: 200px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.country-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 12px rgba(0,0,0,0.2);
}

.country-card.selected {
    border-color: #007958;
    box-shadow: 0 8px 20px rgba(0,121,88,0.4);
}

.country-card.uk {
    background: linear-gradient(135deg, #4169E1 0%, #6495ED 100%);
}

.country-card.canada {
    background: linear-gradient(135deg, #dc143c 0%, #ff1744 100%);
}

.country-card.australia {
    background: linear-gradient(135deg, #007958 0%, #00a86b 100%);
}

.country-card.newzealand {
    background: linear-gradient(135deg, #1E90FF 0%, #4A90E2 100%);
}

.country-flag {
    font-size: 3rem;
    margin-bottom: 1rem;
}

.country-name {
    font-size: 1.5rem;
    font-weight: 700;
    color: white;
    margin: 0;
}

.country-subtitle {
    font-size: 0.9rem;
    color: rgba(255,255,255,0.9);
    margin-top: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# 国家信息
COUNTRIES = {
    "UK": {
        "name": "United Kingdom",
        "flag": "🇬🇧",
        "subtitle": "World-class education system"
    },
    "Canada": {
        "name": "Canada",
        "flag": "🇨🇦",
        "subtitle": "High-quality universities"
    },
    "Australia": {
        "name": "Australia",
        "flag": "🇦🇺",
        "subtitle": "Top-ranked institutions"
    },
    "New Zealand": {
        "name": "New Zealand",
        "flag": "🇳🇿",
        "subtitle": "Excellence in education"
    }
}

# 显示国家选择卡片
st.markdown("### Select a Country")
col1, col2, col3, col4 = st.columns(4)

countries_list = ["UK", "Canada", "Australia", "New Zealand"]
cols = [col1, col2, col3, col4]

for idx, country_key in enumerate(countries_list):
    country = COUNTRIES[country_key]
    is_selected = st.session_state.selected_country == country_key
    
    with cols[idx]:
        # 显示卡片内容
        country_class = country_key.lower().replace(" ", "")
        card_class = f"country-card {country_class}"
        if is_selected:
            card_class += " selected"
        
        st.markdown(f"""
        <div class="{card_class}">
            <div class="country-flag">{country['flag']}</div>
            <div class="country-name">{country['name']}</div>
            <div class="country-subtitle">{country['subtitle']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 按钮用于选择
        if st.button(f"Select {country['name']}", key=f"select_{country_key}", 
                    use_container_width=True, 
                    type="primary" if is_selected else "secondary"):
            st.session_state.selected_country = country_key
            st.rerun()

# QS Top 大学数据模型
class QSUniversity(BaseModel):
    rank: int = Field(..., description="QS World University Ranking")
    university_name: str = Field(..., description="University name")
    location: str = Field(..., description="City/Location")
    qs_score: float = Field(None, description="QS Score if available")

class QSUniversityList(BaseModel):
    country: str
    universities: List[QSUniversity]

# 获取 QS Top 大学的函数
def get_qs_top_universities(country: str, top_n: int = 20) -> List[dict]:
    """使用 AI 获取指定国家的 QS Top 大学列表"""
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    system_prompt = """You are an expert in international higher education rankings. 
    You MUST provide ACCURATE QS World University Rankings data (2024 or 2025).
    CRITICAL: Verify rankings before returning. Use the most recent available data (2024 or 2025).
    Return ONLY valid JSON, no explanations or additional text."""
    
    user_prompt = f"""Provide the top {top_n} universities in {country} based on QS World University Rankings (2024 or 2025, global ranking, not country-specific ranking).

    IMPORTANT: 
    - Use QS World University Rankings 2024 or 2025 data (whichever is most recent and accurate)
    - The rank must be the GLOBAL WORLD RANKING position, not country-specific
    - Use accurate and verified rankings
    - If 2025 data is not available or uncertain, use 2024 data
    
    For each university, include:
    - rank: QS World University Ranking (GLOBAL RANK, integer) - this is the worldwide ranking position
    - university_name: Full official name
    - location: City name
    - qs_score: QS Score if available (float, optional)
    
    Return as JSON array with this structure:
    [
        {{
            "rank": 14,
            "university_name": "Australian National University",
            "location": "Canberra",
            "qs_score": 95.2
        }},
        ...
    ]
    
    IMPORTANT: Use accurate QS rankings (2024 or 2025). Return JSON only, no other text."""
    
    try:
        response = llm.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])
        
        content = response.content.strip()
        
        # 调试：显示原始响应（仅在开发时）
        if not content:
            st.error("❌ OpenAI API returned empty response. Please check your API key and network connection.")
            return []
        
        # 提取 JSON
        start = content.find('[')
        end = content.rfind(']') + 1
        if start != -1 and end > start:
            json_str = content[start:end]
            try:
                data = json.loads(json_str)
                if isinstance(data, list) and len(data) > 0:
                    return data
                else:
                    st.warning(f"⚠️ API returned empty list or invalid format. Response preview: {content[:200]}...")
                    return []
            except json.JSONDecodeError as je:
                st.error(f"❌ Failed to parse JSON response: {je}")
                st.error(f"Response preview: {content[:500]}...")
                return []
        else:
            # 尝试直接解析整个内容
            try:
                data = json.loads(content)
                if isinstance(data, list):
                    return data
                else:
                    st.warning(f"⚠️ API returned non-list data. Response preview: {content[:200]}...")
                    return []
            except json.JSONDecodeError:
                st.error(f"❌ Could not find JSON array in response. Response preview: {content[:500]}...")
                return []
    except Exception as e:
        error_msg = str(e)
        st.error(f"❌ Error fetching QS rankings: {error_msg}")
        
        # 提供更具体的错误信息
        if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
            st.error("🔑 Please check your OpenAI API key in .streamlit/secrets.toml")
        elif "rate limit" in error_msg.lower() or "quota" in error_msg.lower():
            st.error("⏱️ API rate limit exceeded. Please try again later.")
        elif "network" in error_msg.lower() or "connection" in error_msg.lower():
            st.error("🌐 Network error. Please check your internet connection.")
        else:
            st.error(f"💡 Error type: {type(e).__name__}")
        
        return []

# 显示选中的国家
if st.session_state.selected_country:
    selected_country_info = COUNTRIES[st.session_state.selected_country]
    st.divider()
    st.markdown(f"### {selected_country_info['name']} - QS Top Universities")
    
    # 初始化缓存键
    cache_key = f"qs_universities_{st.session_state.selected_country}"
    
    # 获取或加载 QS Top 大学数据
    if cache_key not in st.session_state:
        with st.spinner(f"Loading QS Top Universities in {selected_country_info['name']} (with global rankings)..."):
            universities_data = get_qs_top_universities(selected_country_info['name'], top_n=20)
            if universities_data and len(universities_data) > 0:
                st.session_state[cache_key] = universities_data
            else:
                # 如果获取失败，不缓存空结果，以便重试
                st.session_state[cache_key] = []
    
    universities_data = st.session_state.get(cache_key, [])
    
    if universities_data and len(universities_data) > 0:
        # 创建 DataFrame 显示
        df_universities = pd.DataFrame(universities_data)
        
        # 显示统计信息
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Universities", len(df_universities))
        with col2:
            if 'qs_score' in df_universities.columns and df_universities['qs_score'].notna().any():
                avg_score = df_universities['qs_score'].mean()
                st.metric("Average QS Score", f"{avg_score:.1f}")
            else:
                top_rank = df_universities['rank'].min()
                st.metric("Best Global Rank", f"#{int(top_rank)}")
        with col3:
            if 'location' in df_universities.columns:
                unique_locations = df_universities['location'].nunique()
                st.metric("Cities", unique_locations)
        
        st.markdown("---")
        
        # 显示大学列表 - 每行5个卡片，显示3行
        st.markdown("#### 📋 University Rankings")
        st.caption("Rankings shown are QS World University Rankings (Global Ranking)")
        
        # 添加卡片样式
        st.markdown("""
        <style>
        .university-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            padding: 1rem;
            color: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            cursor: pointer;
            height: 100%;
            min-height: 140px;
            margin-bottom: 1rem;
        }
        .university-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 12px rgba(0,0,0,0.2);
        }
        .university-card-button {
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
            width: 100% !important;
            height: 100% !important;
        }
        .university-card-button > div {
            width: 100% !important;
            height: 100% !important;
        }
        .university-rank {
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 0.4rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .university-name {
            font-size: 0.9rem;
            font-weight: 600;
            margin-bottom: 0.4rem;
            line-height: 1.3;
            min-height: 2.2rem;
        }
        .university-location {
            font-size: 0.8rem;
            opacity: 0.9;
            margin-top: 0.4rem;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # 初始化选中的大学
        if "clicked_university" not in st.session_state:
            st.session_state.clicked_university = None
        
        # 添加JavaScript来处理卡片点击
        st.markdown("""
        <script>
        function handleCardClick(universityName) {
            // 使用Streamlit的setComponentValue来传递数据
            // 或者使用URL参数
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: universityName
            }, '*');
        }
        </script>
        """, unsafe_allow_html=True)
        
        # 将所有大学显示为卡片网格（每行5个，最多3行）
        universities_list = df_universities.to_dict('records')
        
        if universities_list:
            # 限制显示15个（3行 x 5个）
            display_list = universities_list[:15]
            
            # 显示3行，每行5个
            for row in range(3):
                row_start = row * 5
                row_end = min(row_start + 5, len(display_list))
                row_data = display_list[row_start:row_end]
                
                if row_data:
                    cols = st.columns(5, gap="small")
                    for idx, uni in enumerate(row_data):
                        with cols[idx]:
                            rank = uni.get('rank', 'N/A')
                            name = str(uni.get('university_name', 'N/A'))
                            location = str(uni.get('location', 'N/A'))
                            qs_score = uni.get('qs_score', None)
                            
                            score_text = f"<br><span style='font-size: 0.75rem; opacity: 0.8;'>Score: {qs_score:.1f}</span>" if qs_score and pd.notna(qs_score) else ""
                            
                            # 为每个卡片添加唯一的key
                            card_key = f"uni_card_{row}_{idx}"
                            
                            # 显示HTML卡片（仅显示信息，不点击）
                            score_display = f"<br><span style='font-size: 0.75rem; opacity: 0.9;'>Score: {qs_score:.1f}</span>" if qs_score and pd.notna(qs_score) else ""
                            
                            card_html = f"""
                            <div style="
                                background: linear-gradient(135deg, #1f77b4 0%, #4a90e2 100%);
                                border-radius: 12px;
                                padding: 1.2rem;
                                height: 140px;
                                min-height: 140px;
                                max-height: 140px;
                                color: white;
                                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                                text-align: center;
                                display: flex;
                                flex-direction: column;
                                justify-content: center;
                                align-items: center;
                                margin-bottom: 0.5rem;
                            ">
                                <div style="font-size: 1.5rem; font-weight: bold; margin-bottom: 0.5rem;">#{rank}</div>
                                <div style="font-size: 1rem; font-weight: 600; margin-bottom: 0.3rem; line-height: 1.3;">{name}</div>
                                <div style="font-size: 0.85rem; opacity: 0.95;">📍 {location}{score_display}</div>
                            </div>
                            """
                            st.markdown(card_html, unsafe_allow_html=True)
                            
                            # 在卡片下方放置美观的按钮
                            if st.button("View Details", key=card_key, use_container_width=True):
                                st.session_state.clicked_university = name
                                st.rerun()
                            
                            # 美化按钮样式
                            st.markdown(f"""
                            <style>
                            button[aria-label='{card_key}'] {{
                                background: linear-gradient(135deg, #4a90e2 0%, #1f77b4 100%) !important;
                                color: white !important;
                                border: none !important;
                                border-radius: 8px !important;
                                padding: 0.6rem 1rem !important;
                                font-weight: 600 !important;
                                font-size: 0.9rem !important;
                                transition: all 0.3s ease !important;
                                box-shadow: 0 2px 6px rgba(31, 119, 180, 0.3) !important;
                            }}
                            button[aria-label='{card_key}']:hover {{
                                background: linear-gradient(135deg, #5aa0f2 0%, #2f87c4 100%) !important;
                                transform: translateY(-2px) !important;
                                box-shadow: 0 4px 10px rgba(31, 119, 180, 0.4) !important;
                            }}
                            </style>
                            """, unsafe_allow_html=True)
                    
                    # 如果这一行不满5个，添加空列
                    if len(row_data) < 5:
                        for idx in range(len(row_data), 5):
                            with cols[idx]:
                                st.empty()
                    
                    # 添加行间距
                    if row < 2:  # 不是最后一行
                        st.markdown("<br>", unsafe_allow_html=True)
            
            # 显示大学详情（直接在下方显示）
            if st.session_state.clicked_university:
                selected_uni_name = st.session_state.clicked_university
                selected_uni_data = df_universities[df_universities['university_name'] == selected_uni_name]
                
                if not selected_uni_data.empty:
                    selected_uni_data = selected_uni_data.iloc[0]
                    
                    st.markdown("---")
                    st.markdown(f"### 🏫 {selected_uni_name}")
                    
                    # 获取或生成大学详情
                    cache_key_uni = f"uni_details_{selected_uni_name}_{selected_country_info['name']}"
                    
                    if cache_key_uni not in st.session_state:
                        with st.spinner(f"Loading detailed information for {selected_uni_name}..."):
                            try:
                                llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
                                
                                system_prompt = """You are an expert in international higher education. 
                                Provide comprehensive and accurate information about universities and their courses.
                                Return ONLY valid JSON, no explanations or additional text."""
                                
                                user_prompt = f"""Provide detailed information about {selected_uni_name} in {selected_country_info['name']}.

                                Include:
                                - overview: A comprehensive 2-3 paragraph overview of the university (history, reputation, strengths)
                                - location: Detailed location information
                                - qs_rank: QS World University Ranking (if known)
                                - strengths: List of 5-7 key strengths or notable features
                                - popular_courses: List of 8-10 popular/notable courses/majors offered, each with:
                                  - course_name: Full name of the course
                                  - field: Field of study (e.g., Engineering, Business, Science)
                                  - degree_level: Bachelor, Master, or PhD
                                  - brief_description: 1-2 sentence description

                                Return as JSON with this structure:
                                {{
                                    "overview": "Detailed overview...",
                                    "location": "City, Country",
                                    "qs_rank": 1,
                                    "strengths": ["Strength 1", "Strength 2", ...],
                                    "popular_courses": [
                                        {{
                                            "course_name": "Computer Science",
                                            "field": "Engineering",
                                            "degree_level": "Bachelor",
                                            "brief_description": "Description..."
                                        }},
                                        ...
                                    ]
                                }}

                                Return JSON only, no other text."""
                                
                                response = llm.invoke([
                                    {"role": "system", "content": system_prompt},
                                    {"role": "user", "content": user_prompt}
                                ])
                                
                                content = response.content.strip()
                                start = content.find('{')
                                end = content.rfind('}') + 1
                                if start != -1 and end > start:
                                    json_str = content[start:end]
                                    uni_details = json.loads(json_str)
                                    st.session_state[cache_key_uni] = uni_details
                                else:
                                    st.error("Could not parse university details.")
                                    st.session_state[cache_key_uni] = None
                            except Exception as e:
                                st.error(f"Error loading university details: {e}")
                                st.session_state[cache_key_uni] = None
                    else:
                        uni_details = st.session_state[cache_key_uni]
                    
                    if uni_details and uni_details is not None:
                        # 基本信息
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("QS World Rank", f"#{selected_uni_data.get('rank', 'N/A')}")
                        with col2:
                            st.metric("Location", selected_uni_data.get('location', 'N/A'))
                        with col3:
                            if 'qs_score' in selected_uni_data and pd.notna(selected_uni_data['qs_score']):
                                st.metric("QS Score", f"{selected_uni_data['qs_score']:.1f}")
                        
                        # 大学概述
                        st.markdown("#### 📖 Overview")
                        st.write(uni_details.get("overview", "No overview available."))
                        
                        # 大学优势
                        if "strengths" in uni_details and uni_details["strengths"]:
                            st.markdown("#### ✨ Key Strengths")
                            strengths = uni_details["strengths"]
                            if isinstance(strengths, list):
                                for strength in strengths:
                                    st.markdown(f"- {strength}")
                            else:
                                st.write(strengths)
                        
                        # 热门课程
                        if "popular_courses" in uni_details and uni_details["popular_courses"]:
                            st.markdown("#### 📚 Popular Courses & Programs")
                            courses = uni_details["popular_courses"]
                            
                            # 使用卡片布局显示课程
                            course_cols = st.columns(2)
                            for idx, course in enumerate(courses):
                                with course_cols[idx % 2]:
                                    st.markdown(f"""
                                    <div style="
                                        background: #f8f9fa;
                                        border-left: 4px solid #007958;
                                        padding: 1rem;
                                        margin-bottom: 1rem;
                                        border-radius: 5px;
                                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                                        min-height: 200px;
                                    ">
                                        <h4 style="color: #007958; margin-bottom: 0.5rem;">{course.get('course_name', 'N/A')}</h4>
                                        <p style="color: #666; margin: 0.3rem 0;"><strong>Field:</strong> {course.get('field', 'N/A')}</p>
                                        <p style="color: #666; margin: 0.3rem 0;"><strong>Level:</strong> {course.get('degree_level', 'N/A')}</p>
                                        <p style="color: #333; margin-top: 0.5rem;">{course.get('brief_description', 'No description available.')}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                        
                        # 关闭按钮
                        if st.button("Close", key=f"close_{selected_uni_name}"):
                            st.session_state.clicked_university = None
                            st.rerun()
        
        # 下载按钮
        csv = df_universities.to_csv(index=False)
        st.download_button(
            label="📥 Download QS Rankings (CSV)",
            data=csv,
            file_name=f"qs_rankings_{st.session_state.selected_country.lower().replace(' ', '_')}.csv",
            mime="text/csv"
        )
    else:
        st.warning(f"⚠️ Unable to load QS rankings for {selected_country_info['name']}. Please try again.")
        
        # 提供重试按钮
        if st.button("🔄 Retry Loading Rankings", key=f"retry_{cache_key}"):
            if cache_key in st.session_state:
                del st.session_state[cache_key]
            st.rerun()

