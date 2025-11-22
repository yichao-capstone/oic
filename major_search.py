import streamlit as st
import pandas as pd
from supabase_client import get_supabase_client
from datetime import datetime
import json
import os
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import List
import re

# 大学域名映射（常见大学）
UNIVERSITY_DOMAINS = {
    "University of Sydney": "sydney.edu.au",
    "University of Melbourne": "unimelb.edu.au",
    "Australian National University": "anu.edu.au",
    "University of New South Wales": "unsw.edu.au",
    "Monash University": "monash.edu",
    "University of Queensland": "uq.edu.au",
    "University of Western Australia": "uwa.edu.au",
    "University of Adelaide": "adelaide.edu.au",
    "University of Technology Sydney": "uts.edu.au",
    "University of Oxford": "ox.ac.uk",
    "University of Cambridge": "cam.ac.uk",
    "Imperial College London": "imperial.ac.uk",
    "University College London": "ucl.ac.uk",
    "London School of Economics": "lse.ac.uk",
    "University of Toronto": "utoronto.ca",
    "University of British Columbia": "ubc.ca",
    "McGill University": "mcgill.ca",
    "University of Auckland": "auckland.ac.nz",
    "University of Otago": "otago.ac.nz",
}

def get_university_url(university_name: str, major_name: str = "") -> str:
    """获取大学官网课程页面链接"""
    # 首先检查映射表
    for uni_name, domain in UNIVERSITY_DOMAINS.items():
        if uni_name.lower() in university_name.lower() or university_name.lower() in uni_name.lower():
            # 构建课程搜索页面URL
            if "edu.au" in domain:
                return f"https://www.{domain}/study/courses"
            elif "ac.uk" in domain:
                return f"https://www.{domain}/study"
            elif "ca" in domain:
                return f"https://www.{domain}/programs"
            elif "ac.nz" in domain:
                return f"https://www.{domain}/study"
    
    # 如果没有找到，使用AI生成链接
    # 或者返回一个通用的搜索格式
    return f"https://www.{university_name.lower().replace(' ', '').replace('university', 'edu')}.edu.au/study"

# Load secrets from Streamlit secrets management
try:
    OPENAI_API_KEY = st.secrets["openai"]["api_key"]
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
except KeyError as e:
    st.error(f"⚠️ Missing secret configuration: {e}. Please check your .streamlit/secrets.toml file.")
    st.stop()

# 获取 Supabase 客户端
supabase = get_supabase_client()

# 大学域名映射（常见大学）
UNIVERSITY_DOMAINS = {
    "University of Sydney": "sydney.edu.au",
    "University of Melbourne": "unimelb.edu.au",
    "Australian National University": "anu.edu.au",
    "University of New South Wales": "unsw.edu.au",
    "Monash University": "monash.edu",
    "University of Queensland": "uq.edu.au",
    "University of Western Australia": "uwa.edu.au",
    "University of Adelaide": "adelaide.edu.au",
    "University of Technology Sydney": "uts.edu.au",
    "University of Oxford": "ox.ac.uk",
    "University of Cambridge": "cam.ac.uk",
    "Imperial College London": "imperial.ac.uk",
    "University College London": "ucl.ac.uk",
    "London School of Economics": "lse.ac.uk",
    "University of Toronto": "utoronto.ca",
    "University of British Columbia": "ubc.ca",
    "McGill University": "mcgill.ca",
    "University of Auckland": "auckland.ac.nz",
    "University of Otago": "otago.ac.nz",
}

def get_university_url(university_name: str, major_name: str = "") -> str:
    """获取大学官网主页链接"""
    # 首先检查映射表
    for uni_name, domain in UNIVERSITY_DOMAINS.items():
        if uni_name.lower() in university_name.lower() or university_name.lower() in uni_name.lower():
            # 直接链接到大学主页
            return f"https://www.{domain}"
    
    # 如果没有找到，尝试从大学名称推断常见大学
    uni_lower = university_name.lower()
    if "sydney" in uni_lower and "university" in uni_lower:
        return "https://www.sydney.edu.au"
    elif "melbourne" in uni_lower and "university" in uni_lower:
        return "https://www.unimelb.edu.au"
    elif "monash" in uni_lower:
        return "https://www.monash.edu"
    elif "new south wales" in uni_lower or "unsw" in uni_lower:
        return "https://www.unsw.edu.au"
    elif "queensland" in uni_lower and "university" in uni_lower:
        return "https://www.uq.edu.au"
    elif "western australia" in uni_lower or "uwa" in uni_lower:
        return "https://www.uwa.edu.au"
    elif "adelaide" in uni_lower and "university" in uni_lower:
        return "https://www.adelaide.edu.au"
    elif "technology sydney" in uni_lower or "uts" in uni_lower:
        return "https://www.uts.edu.au"
    elif "australian national" in uni_lower or "anu" in uni_lower:
        return "https://www.anu.edu.au"
    elif "oxford" in uni_lower:
        return "https://www.ox.ac.uk"
    elif "cambridge" in uni_lower:
        return "https://www.cam.ac.uk"
    elif "imperial" in uni_lower:
        return "https://www.imperial.ac.uk"
    elif "university college london" in uni_lower or "ucl" in uni_lower:
        return "https://www.ucl.ac.uk"
    elif "london school" in uni_lower or "lse" in uni_lower:
        return "https://www.lse.ac.uk"
    elif "toronto" in uni_lower and "university" in uni_lower:
        return "https://www.utoronto.ca"
    elif "british columbia" in uni_lower or "ubc" in uni_lower:
        return "https://www.ubc.ca"
    elif "mcgill" in uni_lower:
        return "https://www.mcgill.ca"
    elif "auckland" in uni_lower and "university" in uni_lower:
        return "https://www.auckland.ac.nz"
    elif "otago" in uni_lower and "university" in uni_lower:
        return "https://www.otago.ac.nz"
    else:
        # 如果都找不到，返回Google搜索该大学
        return f"https://www.google.com/search?q={university_name.replace(' ', '+')}"

# 页面标题
st.title("🔍 Major & Course Search")
st.markdown("Search for majors and courses, or get AI-powered recommendations based on your career planning")

# 初始化 session state
if "search_history" not in st.session_state:
    st.session_state.search_history = []
if "search_results" not in st.session_state:
    st.session_state.search_results = None
if "recommended_majors" not in st.session_state:
    st.session_state.recommended_majors = None

# 创建标签页：搜索和推荐
tab1, tab2 = st.tabs(["🔍 Search Majors", "🎯 Recommended Majors"])

with tab1:
    st.markdown("### Search for Majors and Courses")
    st.markdown("Enter keywords or use filters to find majors and courses that match your interests.")
    
    # 搜索表单
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input(
            "Search Keywords",
            placeholder="e.g., Computer Science, Engineering, Business...",
            help="Enter keywords to search for majors or courses"
        )
    
    with col2:
        search_button = st.button("🔍 Search", type="primary", use_container_width=True)
    
    # 筛选条件
    with st.expander("🔽 Advanced Filters", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            country_filter = st.selectbox(
                "Country",
                ["All", "Australia", "UK", "Canada", "New Zealand"],
                help="Filter by country"
            )
        
        with col2:
            field_filter = st.selectbox(
                "Field of Study",
                ["All", "Engineering", "Business", "Science", "Arts", "Medicine", "Education"],
                help="Filter by field of study"
            )
        
        with col3:
            degree_level = st.selectbox(
                "Degree Level",
                ["All", "Bachelor", "Master", "PhD"],
                help="Filter by degree level"
            )
    
    # 定义数据模型
    class MajorResult(BaseModel):
        major_name: str = Field(..., description="Name of the major/course")
        university: str = Field(..., description="University name")
        country: str = Field(..., description="Country where the university is located")
        degree_level: str = Field(..., description="Degree level (Bachelor, Master, PhD)")
        description: str = Field(..., description="Brief description of the major")
        field_of_study: str = Field(..., description="Field of study category")
    
    class MajorSearchResults(BaseModel):
        results: List[MajorResult] = Field(..., description="List of major search results")
    
    # 执行搜索
    if search_button or search_query:
        if search_query.strip():
            with st.spinner("Searching for majors and courses using AI..."):
                try:
                    llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
                    
                    # 构建搜索提示
                    system_prompt = """You are an expert in international higher education. 
                    Provide accurate information about majors and courses at universities in Australia, UK, Canada, and New Zealand.
                    Return ONLY valid JSON, no explanations or additional text."""
                    
                    filters_text = ""
                    if country_filter != "All":
                        filters_text += f" in {country_filter}"
                    if field_filter != "All":
                        filters_text += f" in {field_filter} field"
                    if degree_level != "All":
                        filters_text += f" at {degree_level} level"
                    
                    user_prompt = f"""Search for majors and courses related to: "{search_query}"{filters_text if filters_text else ""}.

                    Provide 10-15 relevant major/course results. For each result, include:
                    - major_name: Full name of the major/course
                    - university: University name (prefer Australian universities, but include UK, Canada, New Zealand if relevant)
                    - country: Country name (Australia, UK, Canada, or New Zealand)
                    - degree_level: Bachelor, Master, or PhD
                    - description: Brief 1-2 sentence description
                    - field_of_study: Category (Engineering, Business, Science, Arts, Medicine, Education, etc.)

                    Return as JSON array with this structure:
                    {{
                        "results": [
                            {{
                                "major_name": "Computer Science",
                                "university": "University of Sydney",
                                "country": "Australia",
                                "degree_level": "Bachelor",
                                "description": "A comprehensive program covering software development, algorithms, and computer systems.",
                                "field_of_study": "Engineering"
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
                    
                    # 提取 JSON
                    start = content.find('{')
                    end = content.rfind('}') + 1
                    if start != -1 and end > start:
                        json_str = content[start:end]
                        data = json.loads(json_str)
                        
                        if "results" in data and isinstance(data["results"], list):
                            search_results = data["results"]
                            st.session_state.search_results = search_results
                            
                            # 记录搜索历史
                            search_history_entry = {
                                "query": search_query,
                                "timestamp": datetime.now().isoformat(),
                                "result_count": len(search_results)
                            }
                            st.session_state.search_history.insert(0, search_history_entry)
                            
                            # 保存搜索历史到数据库（如果用户已登录）
                            try:
                                if st.session_state.get("auth_user"):
                                    user_email = st.session_state.auth_user.email
                                    # 从 users 表获取 user_id
                                    user_response = (
                                        supabase.table("users")
                                        .select("id")
                                        .eq("username", user_email)
                                        .execute()
                                    )
                                    
                                    if user_response.data:
                                        user_id = user_response.data[0]["id"]
                                        
                                        # 保存到 search_history 表
                                        try:
                                            supabase.table("search_history").insert({
                                                "user_id": user_id,
                                                "search_query": search_query,
                                                "result_count": len(search_results),
                                                "filters": json.dumps({
                                                    "country": country_filter,
                                                    "field": field_filter,
                                                    "degree_level": degree_level
                                                })
                                            }).execute()
                                        except Exception as e:
                                            # 如果表不存在，只记录在 session_state
                                            pass
                            except:
                                pass
                            
                            st.success(f"Found {len(search_results)} result(s)")
                        else:
                            st.error("Invalid response format from AI.")
                            st.session_state.search_results = None
                    else:
                        st.error("Could not parse AI response.")
                        st.session_state.search_results = None
                        
                except json.JSONDecodeError as e:
                    st.error(f"Error parsing AI response: {e}")
                    st.info("💡 The AI response was not in valid JSON format. Please try again.")
                except Exception as e:
                    st.error(f"Error searching: {e}")
                    st.exception(e)
        else:
            st.warning("Please enter a search query.")
    
    # 显示搜索结果
    if st.session_state.search_results:
        st.markdown("---")
        st.markdown("### Search Results")
        
        for idx, result in enumerate(st.session_state.search_results, 1):
            with st.container():
                col1, col2 = st.columns([1, 3])
                
                # 获取专业名称（在col1中使用）
                name = result.get("major_name") or result.get("name") or result.get("course_name", "N/A")
                
                with col1:
                    # 显示可点击的大学链接卡片（放在左边）
                    if "university" in result:
                        university = result.get('university', 'N/A')
                        # 获取大学官网链接
                        university_url = get_university_url(university, name)
                        st.markdown(
                            f'<a href="{university_url}" target="_blank" style="text-decoration: none; display: block;">'
                            f'<div style="background: #1a365d; '
                            f'color: #ffffff; padding: 1.2rem; border-radius: 8px; text-align: center; '
                            f'margin-bottom: 0.5rem; cursor: pointer; transition: transform 0.2s, box-shadow 0.2s; '
                            f'border: 2px solid #2c5282; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">'
                            f'<strong style="font-size: 1.1rem; color: #ffffff; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); font-weight: 700;">🏫<br>{university}</strong><br>'
                            f'<span style="font-size: 0.9rem; color: #e2e8f0; font-weight: 600; text-shadow: 1px 1px 2px rgba(0,0,0,0.4);">View Courses →</span>'
                            f'</div></a>',
                            unsafe_allow_html=True
                        )
                    if "country" in result:
                        country_emoji = {
                            "Australia": "🇦🇺",
                            "UK": "🇬🇧",
                            "Canada": "🇨🇦",
                            "New Zealand": "🇳🇿"
                        }
                        emoji = country_emoji.get(result.get('country', ''), "🌍")
                        st.caption(f"{emoji} {result.get('country', 'N/A')}")
                
                with col2:
                    # 显示专业/课程信息（不包含University链接）
                    st.markdown(f"#### {idx}. {name}")
                    
                    if "description" in result:
                        st.write(result["description"])
                    
                    info_cols = st.columns(2)
                    with info_cols[0]:
                        if "country" in result:
                            st.write(f"**🌍 Country:** {result['country']}")
                    with info_cols[1]:
                        if "degree_level" in result:
                            st.write(f"**🎓 Level:** {result['degree_level']}")
                    
                    if "field_of_study" in result:
                        st.caption(f"📚 Field: {result['field_of_study']}")
                
                st.divider()
        
        # 显示搜索历史
        if st.session_state.search_history:
            with st.expander("📜 Recent Search History", expanded=False):
                for history in st.session_state.search_history[:10]:  # 显示最近10条
                    st.write(f"**{history['query']}** - {history['result_count']} results - {history['timestamp'][:19]}")

with tab2:
    st.markdown("### AI-Powered Major Recommendations")
    st.markdown("Get personalized major recommendations based on your career planning profile.")
    
    # 检查用户是否已登录
    if not st.session_state.get("auth_user"):
        st.info("🔐 Please log in to get personalized major recommendations based on your career planning.")
        st.markdown("Go to **Personal Survey** page to log in.")
    else:
        user_email = st.session_state.auth_user.email
        
        # 获取用户的职业规划数据
        try:
            # 从 users 表获取 user_id
            user_response = (
                supabase.table("users")
                .select("id")
                .eq("username", user_email)
                .execute()
            )
            
            if user_response.data:
                user_id = user_response.data[0]["id"]
                
                # 获取用户的最新职业规划
                try:
                    career_response = (
                        supabase.table("career_planning")
                        .select("*")
                        .eq("user_id", user_id)
                        .order("created_at", desc=True)
                        .limit(1)
                        .execute()
                    )
                    
                    if career_response.data and len(career_response.data) > 0:
                        career_plan = career_response.data[0]
                        
                        st.success("Found your career planning profile!")
                        st.markdown(f"**Latest Career Plan:** {career_plan.get('plan_name', 'N/A')}")
                        
                        # 显示推荐按钮
                        if st.button("🎯 Get Recommended Majors", type="primary"):
                            with st.spinner("Generating personalized major recommendations using AI..."):
                                try:
                                    # 使用AI生成推荐
                                    llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
                                    
                                    system_prompt = """You are an expert academic pathways adviser. 
                                    Based on a student's career planning profile, recommend 9 suitable majors.
                                    Each major should correspond to a different university.
                                    Return ONLY valid JSON, no explanations or additional text."""
                                    
                                    # 构建职业规划信息
                                    plan_info = f"Career Plan: {career_plan.get('plan_name', 'N/A')}"
                                    if "recommended_fields" in career_plan:
                                        fields = career_plan.get("recommended_fields")
                                        if isinstance(fields, str):
                                            try:
                                                fields = json.loads(fields)
                                            except:
                                                pass
                                        if isinstance(fields, list):
                                            plan_info += f"\nRecommended Fields: {', '.join(fields[:5])}"
                                    
                                    user_prompt = f"""Based on this career planning profile:
                                    {plan_info}
                                    
                                    Recommend exactly 9 majors/courses. Each major should:
                                    - Be from a different university (prefer Australian universities)
                                    - Match the student's career planning profile
                                    - Include diverse fields and universities
                                    
                                    Return as JSON with this structure:
                                    {{
                                        "recommendations": [
                                            {{
                                                "major": "Computer Science",
                                                "university": "University of Sydney",
                                                "country": "Australia",
                                                "why_fit": "Brief explanation why this major fits the student's profile"
                                            }},
                                            ...
                                        ]
                                    }}
                                    
                                    Return exactly 9 recommendations. Return JSON only, no other text."""
                                    
                                    response = llm.invoke([
                                        {"role": "system", "content": system_prompt},
                                        {"role": "user", "content": user_prompt}
                                    ])
                                    
                                    content = response.content.strip()
                                    
                                    # 提取 JSON
                                    start = content.find('{')
                                    end = content.rfind('}') + 1
                                    if start != -1 and end > start:
                                        json_str = content[start:end]
                                        data = json.loads(json_str)
                                        
                                        if "recommendations" in data and isinstance(data["recommendations"], list):
                                            recommendations = data["recommendations"][:9]  # 确保只有9个
                                            st.session_state.recommended_majors = recommendations
                                            st.success(f"Generated {len(recommendations)} personalized recommendations!")
                                        else:
                                            st.error("Invalid response format from AI.")
                                    else:
                                        st.error("Could not parse AI response.")
                                        
                                except json.JSONDecodeError as e:
                                    st.error(f"Error parsing AI response: {e}")
                                except Exception as e:
                                    st.error(f"Error generating recommendations: {e}")
                                    st.exception(e)
                    else:
                        st.info("💡 No career planning found. Complete a career planning assessment to get personalized recommendations.")
                        st.markdown("Go to **Personal Survey** page to complete your assessment.")
                        
                except Exception as e:
                    if "relation" in str(e).lower() or "does not exist" in str(e).lower():
                        st.info("💡 Career planning feature is not yet available. Complete a career planning assessment first.")
                    else:
                        st.error(f"Error loading career planning: {e}")
            else:
                st.warning("User not found in database.")
                
        except Exception as e:
            st.error(f"Error: {e}")
    
    # 显示推荐的专业
    if st.session_state.recommended_majors:
        st.markdown("---")
        st.markdown("### Recommended Majors (9 Majors)")
        
        # 使用3列布局显示9个推荐
        cols = st.columns(3)
        
        for idx, rec in enumerate(st.session_state.recommended_majors):
            with cols[idx % 3]:
                with st.container():
                    major = rec.get("major") or rec.get("major_name", "N/A")
                    university = rec.get("university", "N/A")
                    country = rec.get("country", "N/A")
                    why_fit = rec.get("why_fit", "")
                    
                    country_emoji = {
                        "Australia": "🇦🇺",
                        "UK": "🇬🇧",
                        "Canada": "🇨🇦",
                        "New Zealand": "🇳🇿"
                    }
                    emoji = country_emoji.get(country, "🌍")
                    
                    # 获取大学官网链接
                    university_url = get_university_url(university, major)
                    
                    st.markdown(f"""
                    <a href="{university_url}" target="_blank" style="text-decoration: none; display: block;">
                    <div style="
                        background: #2d3748;
                        border-radius: 10px;
                        padding: 1.5rem;
                        margin-bottom: 1rem;
                        color: white;
                        min-height: 200px;
                        cursor: pointer;
                        transition: transform 0.2s, box-shadow 0.2s;
                        border: 2px solid #1a202c;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.4);
                    " onmouseover="this.style.transform='translateY(-5px)'; this.style.boxShadow='0 8px 16px rgba(0,0,0,0.5)';" 
                       onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 6px rgba(0,0,0,0.4)';">
                        <h4 style="color: #ffffff; margin-bottom: 0.8rem; font-size: 1.2rem; font-weight: 700; text-shadow: 2px 2px 4px rgba(0,0,0,0.6);">{major}</h4>
                        <p style="color: #ffffff; margin: 0.5rem 0; font-size: 1rem; font-weight: 600; text-shadow: 1px 1px 3px rgba(0,0,0,0.5);"><strong>🏫 {university}</strong></p>
                        <p style="color: #e2e8f0; margin: 0.5rem 0; font-size: 0.95rem; font-weight: 500; text-shadow: 1px 1px 2px rgba(0,0,0,0.4);">{emoji} {country}</p>
                        {f'<p style="color: #cbd5e0; font-size: 0.9rem; margin-top: 0.8rem; margin-bottom: 0.8rem; line-height: 1.4; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">{why_fit}</p>' if why_fit else ''}
                        <p style="color: #ffffff; font-size: 1rem; margin-top: 1rem; margin-bottom: 0; font-weight: 700; text-decoration: underline; text-shadow: 1px 1px 3px rgba(0,0,0,0.5);">View Courses →</p>
                    </div>
                    </a>
                    """, unsafe_allow_html=True)

