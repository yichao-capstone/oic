import os
import json
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
from pydantic import BaseModel
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
from supabase import create_client, Client
from supabase_client import get_supabase_client

# Load secrets from Streamlit secrets management
try:
    OPENAI_API_KEY = st.secrets["openai"]["api_key"]
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
except KeyError as e:
    st.error(f"⚠️ Missing secret configuration: {e}. Please check your .streamlit/secrets.toml file.")
    st.stop()

supabase = get_supabase_client()

# 初始化认证状态
if "auth_user" not in st.session_state:
    st.session_state.auth_user = None
if "auth_session" not in st.session_state:
    st.session_state.auth_session = None

# 检查当前会话
def check_session():
    """检查 Supabase 认证会话"""
    try:
        # 尝试从 session_state 获取会话
        if st.session_state.auth_session:
            # 使用会话的 access_token 获取用户信息
            try:
                # 设置会话到客户端
                supabase.auth.set_session(
                    access_token=st.session_state.auth_session.access_token,
                    refresh_token=st.session_state.auth_session.refresh_token
                )
                user = supabase.auth.get_user()
                if user and user.user:
                    return user.user, st.session_state.auth_session
            except Exception:
                # 会话可能已过期，清除它
                st.session_state.auth_session = None
                st.session_state.auth_user = None
        return None, None
    except Exception:
        return None, None

# 登录函数
def sign_in(email: str, password: str):
    """使用 Supabase Auth 登录"""
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        if response.user and response.session:
            st.session_state.auth_user = response.user
            st.session_state.auth_session = response.session
            return True, "Login successful!"
        return False, "Login failed. Please check your credentials."
    except Exception as e:
        error_msg = str(e)
        if "Invalid login credentials" in error_msg:
            return False, "❌ Invalid email or password."
        elif "Email not confirmed" in error_msg:
            return False, "❌ Please verify your email address first."
        else:
            return False, f"❌ Error: {error_msg}"

# 注册函数
def sign_up(email: str, password: str):
    """使用 Supabase Auth 注册"""
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        if response.user:
            return True, "Registration successful! Please check your email to verify your account."
        return False, "Registration failed."
    except Exception as e:
        error_msg = str(e)
        if "User already registered" in error_msg:
            return False, "❌ This email is already registered. Please sign in instead."
        elif "Password should be at least" in error_msg:
            return False, "❌ Password must be at least 6 characters long."
        else:
            return False, f"❌ Error: {error_msg}"

# 找回密码函数
def reset_password(email: str):
    """发送密码重置邮件"""
    try:
        # Supabase 会发送密码重置邮件到指定邮箱
        supabase.auth.reset_password_for_email(email)
        return True, "Password reset email sent! Please check your email inbox (and spam folder)."
    except Exception as e:
        error_msg = str(e)
        # Supabase 出于安全考虑，即使邮箱不存在也会返回成功
        # 所以这里总是返回成功消息
        return True, "If an account exists with this email, a password reset link has been sent. Please check your email inbox (and spam folder)."

# 登出函数
def sign_out():
    """使用 Supabase Auth 登出"""
    try:
        supabase.auth.sign_out()
        st.session_state.auth_user = None
        st.session_state.auth_session = None
        return True
    except Exception as e:
        st.error(f"Logout error: {e}")
        return False

# 检查当前会话
current_user, current_session = check_session()
if current_user:
    st.session_state.auth_user = current_user
    st.session_state.auth_session = current_session

# 如果未登录，显示登录/注册页面
if not st.session_state.auth_user:
    st.title("🔐 Login Required")
    st.markdown("---")
    st.info("Please log in with your email and password to access Personal Survey.")
    
    # 创建标签页：登录、注册和找回密码
    tab1, tab2, tab3 = st.tabs(["Login", "Sign Up", "Forgot Password"])
    
    with tab1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### Login")
            login_email = st.text_input(
                "Email Address", 
                placeholder="Enter your email address",
                key="login_email"
            )
            login_password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                key="login_password"
            )
            
            login_button = st.button("Login", type="primary", use_container_width=True, key="btn_login")
            
            # 忘记密码提示
            st.markdown("---")
            st.markdown("""
            <div style="text-align: center; color: #666; font-size: 0.9rem;">
                Forgot your password? Go to the "Forgot Password" tab above.
            </div>
            """, unsafe_allow_html=True)
            
            if login_button:
                if login_email.strip() and login_password:
                    success, message = sign_in(login_email.strip(), login_password)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("⚠️ Please enter both email and password.")
    
    with tab2:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### Create Account")
            signup_email = st.text_input(
                "Email Address", 
                placeholder="Enter your email address",
                key="signup_email"
            )
            signup_password = st.text_input(
                "Password",
                type="password",
                placeholder="Create a password (min. 6 characters)",
                key="signup_password"
            )
            signup_confirm_password = st.text_input(
                "Confirm Password",
                type="password",
                placeholder="Confirm your password",
                key="signup_confirm_password"
            )
            
            signup_button = st.button("Sign Up", type="primary", use_container_width=True, key="btn_signup")
            
            if signup_button:
                if signup_email.strip() and signup_password and signup_confirm_password:
                    if signup_password != signup_confirm_password:
                        st.error("❌ Passwords do not match.")
                    elif len(signup_password) < 6:
                        st.error("❌ Password must be at least 6 characters long.")
                    else:
                        success, message = sign_up(signup_email.strip(), signup_password)
                        if success:
                            st.success(message)
                            st.info("💡 After verifying your email, you can log in with your credentials.")
                        else:
                            st.error(message)
                else:
                    st.warning("⚠️ Please fill in all fields.")
    
    with tab3:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### Reset Password")
            st.info("Enter your email address and we'll send you a link to reset your password.")
            
            reset_email = st.text_input(
                "Email Address",
                placeholder="Enter your registered email address",
                key="reset_email"
            )
            
            reset_button = st.button("Send Reset Link", type="primary", use_container_width=True, key="btn_reset")
            
            if reset_button:
                if reset_email.strip():
                    # 验证邮箱格式
                    import re
                    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                    if not re.match(email_pattern, reset_email.strip()):
                        st.error("❌ Please enter a valid email address.")
                    else:
                        success, message = reset_password(reset_email.strip())
                        if success:
                            st.success(message)
                            st.info("📧 Please check your email inbox (and spam folder) for the password reset link.")
                        else:
                            st.error(message)
                else:
                    st.warning("⚠️ Please enter your email address.")
    
    st.stop()  # 阻止继续执行页面内容

# 如果已登录，显示页面内容和退出登录选项
st.title('Personal Profile')

# 在侧边栏显示用户信息和退出登录
with st.sidebar:
    if st.session_state.auth_user:
        st.markdown(f"**Logged in as:** {st.session_state.auth_user.email}")
        if st.button("Logout", type="secondary"):
            if sign_out():
                st.success("Logged out successfully!")
                st.rerun()

st.divider()

# 允许查询任何用户的邮箱地址
user_id = st.text_input(
    "User Email Address", 
    value="mark.m.2024@benendenguangzhou.cn",
    placeholder="Enter email address to query",
    help="You can enter any user's email address to view their survey results."
)


def spider_chart_with_avg(
    scores: dict,
    avg_scores: dict = None,
    order="RIASEC",
    title="RIASEC Spider Chart with Average",
    show_fullname=True,
    bilingual=False,
    hover_font_size=16
):
    # --- 定义 RIASEC 全称与解释 ---
    desc_en = {
        "R": ("Realistic", "Practical, hands-on, and mechanical activities."),
        "I": ("Investigative", "Analytical, intellectual, and scientific tasks."),
        "A": ("Artistic", "Creative, expressive, and design-related activities."),
        "S": ("Social", "Helping, teaching, and cooperative interactions."),
        "E": ("Enterprising", "Leadership, persuasion, and business ventures."),
        "C": ("Conventional", "Organizing, planning, and data-oriented tasks.")

    }
    desc_cn = {
        "R": "现实型：喜欢实际操作、动手实验、机械工程类任务。",
        "I": "研究型：喜欢分析、思考、探索和科学研究。",
        "A": "艺术型：喜欢创意表达、设计、艺术与想象。",
        "S": "社会型：喜欢帮助他人、教学、合作与沟通。",
        "E": "企业型：喜欢领导、说服、管理与商业活动。",
        "C": "常规型：喜欢组织、记录、文书与数据管理。"
    }
    hlafps_desc = {
    "H": ("Hedonism", "Seeking enjoyment, pleasure, and creative life experiences; values freedom, aesthetics, and fun."),
    "P": ("Power & Status", "Aspiring to influence, leadership, and recognition; motivated by prestige and social standing."),
    "A": ("Altruism", "Driven by empathy, compassion, and a desire to help others or contribute to society."),
    "L": ("Learning & Achievement", "Motivated by curiosity, mastery, and personal growth through knowledge and accomplishment."),
    "F": ("Finance", "Focused on financial success, material stability, and economic independence."),
    "S": ("Security", "Prefers stability, predictability, and safety; values structured environments and long-term certainty.")
    }
    order_map = {"RIASEC": ["R","I","A","S","E","C"], "HLAFPS": ["H","L","A","F","P","S"]}
    axis = order_map.get(order.upper(), order_map["RIASEC"])

    labels, values, hover_texts = [], [], []
    for k in axis:
        if k not in scores:
            continue
        if order=='RIASEC':
            fullname, explanation = desc_en.get(k, (k, ""))
        else:
            fullname, explanation = hlafps_desc.get(k, (k, ""))
        if bilingual:
            explanation += f"<br><i>{desc_cn.get(k, '')}</i>"
        label = fullname if show_fullname else k
        labels.append(label)
        values.append(scores[k])
        hover_texts.append(f"<b>{fullname}</b><br>{explanation}<br><b>Score:</b> {scores[k]}")

    # 闭合图形
    labels_closed = labels + [labels[0]]
    values_closed = values + [values[0]]
    r_max = max(max(values), max(avg_scores.values()) if avg_scores else max(values)) * 1.3

    fig = go.Figure()

    # 如果提供平均值，先画平均层（灰色）
    if avg_scores:
        avg_vals = [avg_scores.get(k, 0) for k in axis if k in scores]
        avg_vals += [avg_vals[0]]
        fig.add_trace(go.Scatterpolar(
            r=avg_vals,
            theta=labels_closed,
            mode='lines+markers',
            line=dict(color='#ed2939', width=2),
            marker=dict(size=6, color='#ed2939'),
            fill='toself',
            name="Average",
            hovertemplate="<b>%{theta}</b><br>Average: %{r}<extra></extra>"
        ))


    # 用户个人得分层


    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=labels_closed,
        mode='lines+markers',
        
        line=dict(color='#007958', width=3),
        marker=dict(size=10, color='#007958', line=dict(width=1, color='white')),
        fill='toself',
        name="You",
        hovertext=hover_texts + [hover_texts[0]],
        hoverinfo="text"
    ))

    # 外圈 hover 捕捉
    fig.add_trace(go.Scatterpolar(
        r=[r_max for _ in labels],
        theta=labels,
        mode='markers',
        hovertext=hover_texts,
        hoverinfo="text",
        marker=dict(size=20, color='rgba(0,0,0,0)'),
        showlegend=False
    ))

    # 布局
    fig.update_layout(
        title=title,
        polar=dict(
            radialaxis=dict(visible=True, range=[0, r_max], showticklabels=False),
            angularaxis=dict(
                direction="clockwise",
                tickfont=dict(size=16, color="#222", family="Arial Black")
            )
        ),
        hoverlabel=dict(
            font_size=hover_font_size,
            font_family="Arial",
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor="#555"
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=40, r=40, t=60, b=60)
    )

    return fig


SYSTEM_PROMPT = """
You are a senior academic pathways adviser.

Please analyze the student's profile based on two psychological score models:

1) HLAFPS – value-based motivations:
   • H: Hedonism (enjoyment, pleasure)
   • L: Learning & Achievement (curiosity, mastery)
   • A: Altruism (helping, contributing)
   • F: Finance (financial success, stability)
   • P: Power & Status (leadership, recognition)
   • S: Security (stability, predictability)

2) RIASEC – interest and working style:
   • R: Realistic (hands-on, technical, practical)
   • I: Investigative (analytical, research-oriented)
   • A: Artistic (creative, expressive)
   • S: Social (helping, teaching, people-centered)
   • E: Enterprising (leadership, business, persuasion)
   • C: Conventional (structure, data, organization)

-------------------
TASKS:
-------------------
1. Interpret both models **holistically**:
   - Do NOT convert HLAFPS into RIASEC or vice versa.
   - RIASEC → what types of activities the student enjoys or excels in.
   - HLAFPS → what the student finds meaningful and rewarding.
   - Use both to understand interest + motivation.

2. Identify the top 2 highest-scoring letters from each model.
   - Format as: dominant_type = "RIASEC1-RIASEC2 + HLAFPS1-HLAFPS2"
   - Example: "Investigative-Social + Learning-Altruism"

3. Write a **2–3 sentence human-centered summary** that combines both:
   - Tone: supportive, age-appropriate, future-focused.
   - Show how their interests (RIASEC) and motivations (HLAFPS) complement each other.

-------------------
INPUT FORMAT:
HLAFPS scores (0–100): { "H": , "L": , "A": , "F": , "P": , "S": }
RIASEC scores (0–100): { "R": , "I": , "A": , "S": , "E": , "C": }

-------------------
OUTPUT FORMAT (no extra commentary):
{
  "dominant_type": "RIASEC1-RIASEC2 + HLAFPS1-HLAFPS2",
  "summary": "2–3 sentence synthesis combining both models."
}
"""

def brf_smry_streaming(holland: Dict[str, float],
                       riasec: Dict[str, float],
                       model: str = "gpt-5-nano",
                       placeholder=None):
    """流式显示 dominant type 分析"""
    llm = ChatOpenAI(model_name=model, temperature=0.000001, streaming=True)
    user_prompt = f"""
HLAFPS scores (H/L/A/F/P/S): {holland}
RIASEC scores (R/I/A/S/E/C): {riasec}
 Write a **2–3 sentence human-centered summary** that combines both:
   - Tone: supportive, age-appropriate, future-focused.
   - Show how their interests (RIASEC) and motivations (HLAFPS) complement each other.
Return strict JSON matching the schema.
"""
    
    # 收集流式响应（静默收集，不显示过程）
    full_text = ""
    
    # 流式调用
    for chunk in llm.stream([("system", SYSTEM_PROMPT), ("user", user_prompt)]):
        if hasattr(chunk, 'content') and chunk.content:
            full_text += chunk.content
    
    text = full_text.strip()

    # Robust JSON extraction
    try:
        result = json.loads(text)
        return result
    except Exception:
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1 and end > start:
            result = json.loads(text[start:end+1])
            return result
        raise ValueError("Model did not return valid JSON.\n" + text)

def brf_smry (holland: Dict[str, float],
                     riasec: Dict[str, float],
                     model: str = "gpt-5-nano") -> dict:
    """非流式版本（用于缓存）"""
    llm = ChatOpenAI(model_name=model, temperature=0.000001)
    user_prompt = f"""
HLAFPS scores (H/L/A/F/P/S): {holland}
RIASEC scores (R/I/A/S/E/C): {riasec}
 Write a **2–3 sentence human-centered summary** that combines both:
   - Tone: supportive, age-appropriate, future-focused.
   - Show how their interests (RIASEC) and motivations (HLAFPS) complement each other.
Return strict JSON matching the schema.
"""
    resp = llm.invoke([("system", SYSTEM_PROMPT), ("user", user_prompt)])
    text = resp.content.strip()

    # Robust JSON extraction
    try:
        return json.loads(text)
    except Exception:
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start:end+1])
        raise ValueError("Model did not return valid JSON.\n" + text)

st.session_state.exs=None
if st.button("My Survey Result"):
    if not user_id.strip():
        st.warning("Please enter a valid User_id.")
    else:
        try:
            # Query the survey_processed table
            response = (
                supabase.table("survey_processed")
                .select("*")
                .eq("Username", user_id)
                .execute()
            )
            
            data = response.data
            if not data:
                st.info("No matching records found.")
            else:
                df = pd.DataFrame(data)
                h_vals = {k: float(v) for k, v in (item.split(":") for item in df.loc[0, "Holland_Scores"].replace(" ", "").split(","))}
                r_vals = {k: float(v) for k, v in (item.split(":") for item in df.loc[0, "RIASEC_Scores"].replace(" ", "").split(","))}
                st.success(f"Found {len(df)} record(s) for {user_id}")
                st.session_state.h_vals=h_vals
                st.session_state.r_vals=r_vals
                # 清除该用户的 dominant type 缓存，以便重新分析
                dominant_type_key = f"dominant_type_{user_id}"
                if dominant_type_key in st.session_state:
                    del st.session_state[dominant_type_key]
                 
        except Exception as e:
            st.error(f"Error querying Supabase: {e}")


st.divider()


if "h_vals" in st.session_state:

    h_vals = st.session_state.h_vals
    r_vals = st.session_state.r_vals
    col1, col2 = st.columns(2)
    with col1:

        fig = spider_chart_with_avg(r_vals,{'R': 21.13, 'I': 19.85, 'A': 29.34, 'S': 22.68, 'E': 24.25, 'C': 18.72}, order="RIASEC", title='YOUR RIASEC TYPE')
        st.plotly_chart(fig)
    with col2:
        fig = spider_chart_with_avg(h_vals,{'H': 31.25, 'L': 22.48, 'A': 18.73, 'F': 27.10, 'P': 25.87, 'S': 29.55}, order="HLAFPS", title="YOUR HLAFPS TYPE")
        st.plotly_chart(fig)
    
    # 只在第一次分析时计算 Dominant Type，避免重复分析
    dominant_type_key = f"dominant_type_{user_id}"
    if dominant_type_key not in st.session_state:
        # 使用流式分析（静默模式，不显示过程）
        with st.spinner("Analyzing Dominant Type..."):
            bs = brf_smry_streaming(
                holland=h_vals,
                riasec=r_vals,
                model="gpt-5-nano",
                placeholder=None
            )
        st.session_state[dominant_type_key] = bs
    else:
        bs = st.session_state[dominant_type_key]

    def color_text_dynamic(text):
        # 定义 RIASEC + HLAFPS 对应颜色（包含完整名称和缩写）
        color_map = {
            # RIASEC 类型
            "Investigative": "#1f77b4",
            "Realistic": "#9467bd",
            "Artistic": "#e377c2",
            "Social": "#2ca02c",
            "Enterprising": "#ff7f0e",
            "Conventional": "#8c564b",
            # HLAFPS 类型 - 完整名称优先
            "Learning & Achievement": "#17becf",
            "Power & Status": "#7f7f7f",
            "Hedonism": "#d62728",
            "Altruism": "#2ca02c",
            "Finance": "#bcbd22",
            "Security": "#1f9d55",
            # HLAFPS 类型 - 缩写/部分名称（用于匹配）
            "Learning": "#17becf",
            "Power": "#7f7f7f",
        }

        # 先匹配完整名称（包含 & 的），再匹配单个词
        # 按照长度降序排列，确保先匹配长的名称
        sorted_items = sorted(color_map.items(), key=lambda x: len(x[0]), reverse=True)
        
        for word, color in sorted_items:
            # 转义特殊字符用于正则表达式
            escaped_word = re.escape(word)
            # 匹配完整词，不替换单词的一部分
            text = re.sub(
                rf"\b{escaped_word}\b",
                f"<span style='color:{color}; font-weight:600;'>{word}</span>",
                text,
                flags=re.IGNORECASE
            )
        return text
    
    st.divider()
    st.header("Your Dominant Type")
    colored = color_text_dynamic(bs.get("dominant_type", "N/A"))
    st.markdown(colored, unsafe_allow_html=True)
    st.write(bs.get("summary", "N/A"))
    st.divider()

    # asced= (
    #             supabase.table("ased_detail")
    #             .select("detailed_field_code,description")
    #             .execute()
    #             )
                
    # fields = asced.data














# API key is now loaded from secrets.toml at the top of the file















asced= (
                supabase.table("ased_detail")
                .select("detailed_field_code,description")
                .execute()
                )
                

fields = asced.data



run_btn = st.button('🤖 AI-Powered Study Field Recommendation')

# ---------------------------
# Single-call LLM function
# ---------------------------
schema_bloack="""
{
  "top_recommendations": [
    {
      "field_name": "string",                     // e.g., "Computer Science & Data"
      "asced_broad_code": "string|null",          // optional if you use ASCED mapping (e.g., "02")
      "asced_narrow_code": "string|null",         // optional (e.g., "0201")
      "why_fit": "1 sentences",
      "sample_university_majors": ["string", "..."],
      "suggested_high_school_subjects": ["string", "..."],
      "useful_extracurriculars": ["string", "..."],
      "possible_career_paths": ["string", "..."],
      "cautions": ["string", "..."],
      "Universities": ["string", "..."],
      "Courses": ["string", "..."],       
      }
    }
  ],
  "notes": "short global note (e.g., portfolio/math intensity/subject prerequisites)."
}
"""
SYSTEM_PROMPT_2 = f"""
You are an academic pathways adviser. Based on two score models—
1) HLAFPS: H (Hedonism), L (Learning & Achievement), A (Altruism), F (Finance), P (Power & Status), S (Security)
2) RIASEC: R (Realistic), I (Investigative), A (Artistic), S (Social), E (Enterprising), C (Conventional)

Recommend suitable fields of study for a high school student. Be concise, age-appropriate, practical, and culturally neutral. 
Do not reveal step-by-step reasoning; provide only short, decision-relevant rationales.

RULES:
- Consider both models; default weights: RIASEC 60%, HLAFPS 40%. If user provides custom weights, use them.
- Interpret peaks and meaningful pairs/triads:
  • R → engineering, trades, applied tech, environmental fieldwork
  • I → science, mathematics, CS, data, research
  • A → design, media, performing arts, architecture
  • S → education, nursing, psychology, social work, community services
  • E → business, entrepreneurship, management, law-adjacent, communications
  • C → accounting, finance ops, information systems, administration, library/info mgmt
  • H (Hedonism high) → creative, experiential, hands-on or project-based settings
  • L (Learning & Achievement) → research-intensive, academic rigor, competitions/olympiads
  • A (Altruism) → health, education, social impact, sustainability
  • F (Finance) → business, economics, accounting, fintech, quantitative fields
  • P (Power & Status) → leadership tracks, policy, law, management, debating/public speaking
  • S (Security) → regulated/stable careers: healthcare, civil service, accounting, infrastructure
- Break ties with HLAFPS emphasis and the student’s constraints/interests if provided.
- university in australia has higher priority in uni recommendation 
- Provide 2–3 top fields only select from {fields}. For each, include “why it fits”, sample university majors, suggested high-school subjects, helpful extracurriculars, and 2–3 career pathways, university and courses recommendation.
- Keep cautions pragmatic (e.g., “heavy math load”, “portfolio required”).
- Output strictly in JSON matching the schema below. No extra text.

INPUT:
HLAFPS scores : 
RIASEC scores :
OUTPUT JSON SCHEMA:
{schema_bloack}
"""

def one_call_unified(holland: Dict[str, float],
                     riasec: Dict[str, float],
                     model: str = "gpt-5-nano") -> dict:    
    llm = ChatOpenAI(model_name=model, temperature=0.00001)
    user_prompt = f"""
HLAFPS scores (H/L/A/F/P/S): {holland}
RIASEC scores (R/I/A/S/E/C): {riasec}

Return strict JSON matching the schema.
"""
    resp = llm.invoke([("system", SYSTEM_PROMPT_2), ("user", user_prompt)])
    text = resp.content.strip()

    # Robust JSON extraction
    try:
        return json.loads(text)
    except Exception:
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start:end+1])
        raise ValueError("Model did not return valid JSON.\n" + text)

# ---------------------------
# Run & render
# ---------------------------


if run_btn:
    with st.spinner("Analysing"):
        
        result = one_call_unified(
            holland=h_vals,
            riasec=r_vals,
            model="gpt-5-nano"
        )

    # Notes removed - no longer showing blue info box

# 遍历每一个推荐专业
    for idx, rec in enumerate(result.get("top_recommendations", []), start=1):
        with st.expander(f"✅ {idx}. {rec.get('field_name', 'Unnamed Field')}"):
            st.markdown(f"**Why it fits:** {rec.get('why_fit', '')}")

            # 以两列形式展示
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**🎓 Sample University Majors:**")
                for major in rec.get("sample_university_majors", []):
                    st.markdown(f"- {major}")

                st.markdown("**📘 Suggested High School Subjects:**")
                for subject in rec.get("suggested_high_school_subjects", []):
                    st.markdown(f"- {subject}")

            with col2:
                st.markdown("**🛠 Useful Extracurriculars:**")
                for ext in rec.get("useful_extracurriculars", []):
                    st.markdown(f"- {ext}")

                st.markdown("**💼 Possible Career Paths:**")
                for career in rec.get("possible_career_paths", []):
                    st.markdown(f"- {career}")

            # 注意事项
            st.markdown("**⚠ Cautions:**")
            for c in rec.get("cautions", []):
                st.markdown(f"- {c}")

            # Fit signals 显示
            fit = rec.get("fit_signals", {})
            st.markdown("---")
            st.markdown("**Universit Recommendation:**")
            for uni in rec.get("Universities", []):
                    st.markdown(f"- {uni}")
            st.markdown("**Courses Recommendation:**")       
            for course in rec.get("Courses", []):
                    st.markdown(f"- {course}")
            if "notes" in fit:
                st.write(f"- **Note:** {fit['notes']}")


else:
    st.info ('Please click the button for AI-Powered study field analysis')
