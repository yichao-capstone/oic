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
    Provide accurate QS World University Rankings data for universities in the specified country.
    Return ONLY valid JSON, no explanations or additional text."""
    
    user_prompt = f"""Provide the top {top_n} universities in {country} based on the LATEST QS World University Rankings (global ranking, not country-specific ranking).
    
    IMPORTANT: Use the most recent QS World University Rankings data. The rank should be the GLOBAL WORLD RANKING, not a country-specific ranking.
    
    For each university, include:
    - rank: QS World University Ranking (GLOBAL RANK, integer) - this is the worldwide ranking position
    - university_name: Full official name
    - location: City name
    - qs_score: QS Score if available (float, optional)
    
    Return as JSON array with this structure:
    [
        {{
            "rank": 1,
            "university_name": "University Name",
            "location": "City",
            "qs_score": 95.5
        }},
        ...
    ]
    
    Return JSON only, no other text."""
    
    try:
        response = llm.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])
        
        content = response.content.strip()
        # 提取 JSON
        start = content.find('[')
        end = content.rfind(']') + 1
        if start != -1 and end > start:
            json_str = content[start:end]
            data = json.loads(json_str)
            return data
        else:
            # 尝试直接解析
            data = json.loads(content)
            return data if isinstance(data, list) else []
    except Exception as e:
        st.error(f"Error fetching QS rankings: {e}")
        return []

# 显示选中的国家
if st.session_state.selected_country:
    selected_country_info = COUNTRIES[st.session_state.selected_country]
    st.divider()
    st.markdown(f"### {selected_country_info['flag']} {selected_country_info['name']} - QS Top Universities")
    
    # 初始化缓存键
    cache_key = f"qs_universities_{st.session_state.selected_country}"
    
    # 获取或加载 QS Top 大学数据
    if cache_key not in st.session_state:
        with st.spinner(f"Loading QS Top Universities in {selected_country_info['name']} (with global rankings)..."):
            universities_data = get_qs_top_universities(selected_country_info['name'], top_n=20)
            st.session_state[cache_key] = universities_data
    
    universities_data = st.session_state[cache_key]
    
    if universities_data:
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
        
        # 显示大学列表
        st.markdown("#### 📋 University Rankings")
        st.caption("Rankings shown are QS World University Rankings (Global Ranking)")
        
        # 格式化显示
        display_df = df_universities[['rank', 'university_name', 'location']].copy()
        if 'qs_score' in df_universities.columns:
            display_df['qs_score'] = df_universities['qs_score'].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "N/A")
        
        # 确保排名列显示为全球排名
        display_df.columns = ['QS World Rank', 'University Name', 'Location', 'QS Score'] if 'qs_score' in display_df.columns else ['QS World Rank', 'University Name', 'Location']
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            height=600
        )
        
        # 下载按钮
        csv = df_universities.to_csv(index=False)
        st.download_button(
            label="📥 Download QS Rankings (CSV)",
            data=csv,
            file_name=f"qs_rankings_{st.session_state.selected_country.lower().replace(' ', '_')}.csv",
            mime="text/csv"
        )
    else:
        st.warning(f"Unable to load QS rankings for {selected_country_info['name']}. Please try again.")

