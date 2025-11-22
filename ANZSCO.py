import streamlit as st
import json
import pandas as pd
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from person import get_supabase_client

# 获取 Supabase 客户端
supabase = get_supabase_client()

# 页面标题
st.title("Australian Standard Classification of Education")

# 查询 ased_broad 表并在主要内容区域显示
try:
    ased_response = (
        supabase.table("ased_broad")
        .select("*")
        .execute()
    )
    ased_broad_data = ased_response.data
    if ased_broad_data:
        st.markdown("### Australian Standard Classification of Education (ASCED) Classification Browser")
        ased_df = pd.DataFrame(ased_broad_data)
        
        # 获取 broad_code 字段名（可能是 broad_code, code, 或其他）
        code_column = None
        description_column = None
        
        for col in ased_df.columns:
            if 'code' in col.lower():
                code_column = col
            if 'description' in col.lower() or 'name' in col.lower() or 'title' in col.lower():
                description_column = col
        
        # 如果找到了 code 列，创建多级卡片选择器
        if code_column:
            # 添加弹出框样式
            st.markdown("""
            <style>
            /* 弹出框遮罩层 */
            .modal-overlay {
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                z-index: 10000;
                justify-content: center;
                align-items: center;
            }
            
            .modal-overlay.active {
                display: flex;
            }
            
            /* 弹出框内容 */
            .modal-content {
                background: white;
                border-radius: 15px;
                padding: 2rem;
                max-width: 800px;
                max-height: 80vh;
                overflow-y: auto;
                box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                position: relative;
            }
            
            .modal-header {
                font-size: 1.5rem;
                font-weight: 700;
                color: #007958;
                margin-bottom: 1.5rem;
                padding-bottom: 1rem;
                border-bottom: 3px solid #007958;
            }
            
            .modal-close {
                position: absolute;
                top: 1rem;
                right: 1rem;
                background: #f0f0f0;
                border: none;
                border-radius: 50%;
                width: 30px;
                height: 30px;
                cursor: pointer;
                font-size: 1.2rem;
                color: #666;
            }
            
            .modal-close:hover {
                background: #e0e0e0;
            }
            
            /* 选择卡片样式 */
            .selection-card {
                background: white;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                padding: 1.5rem;
                margin: 0.5rem;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .selection-card:hover {
                border-color: #007958;
                box-shadow: 0 4px 8px rgba(0,121,88,0.2);
                transform: translateY(-2px);
            }
            
            .selection-card.selected {
                border-color: #007958;
                background: #f0f9f7;
                box-shadow: 0 4px 12px rgba(0,121,88,0.3);
            }
            
            /* 当前选择显示 */
            .current-selection {
                background: linear-gradient(135deg, #f0f9f7 0%, #ffffff 100%);
                padding: 1.5rem;
                border-radius: 10px;
                margin: 1rem 0;
                border-left: 5px solid #007958;
            }
            
            .selection-label {
                font-size: 0.9rem;
                color: #666;
                margin-bottom: 0.5rem;
            }
            
            .selection-value {
                font-size: 1.2rem;
                font-weight: 600;
                color: #007958;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # 初始化弹出框状态
            if "show_broad_modal" not in st.session_state:
                st.session_state.show_broad_modal = False
            if "show_narrow_modal" not in st.session_state:
                st.session_state.show_narrow_modal = False
            if "show_detail_modal" not in st.session_state:
                st.session_state.show_detail_modal = False
            
            # 初始化选中的字段
            if "selected_broad_code" not in st.session_state:
                st.session_state.selected_broad_code = None
            if "selected_broad_desc" not in st.session_state:
                st.session_state.selected_broad_desc = None
            if "selected_narrow_code" not in st.session_state:
                st.session_state.selected_narrow_code = None
            if "selected_narrow_desc" not in st.session_state:
                st.session_state.selected_narrow_desc = None
            
            # 显示当前选择
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### 1. Broad Field")
                if st.session_state.selected_broad_code:
                    st.markdown(f"""
                    <div class="current-selection">
                        <div class="selection-label">Selected:</div>
                        <div class="selection-value">{st.session_state.selected_broad_code} - {st.session_state.selected_broad_desc}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("Not selected")
                if st.button("Select Broad Field", key="btn_broad", use_container_width=True, type="primary" if not st.session_state.selected_broad_code else "secondary"):
                    st.session_state.show_broad_modal = True
                    st.rerun()
            
            with col2:
                st.markdown("### 2. Narrow Field")
                if st.session_state.selected_narrow_code:
                    st.markdown(f"""
                    <div class="current-selection">
                        <div class="selection-label">Selected:</div>
                        <div class="selection-value">{st.session_state.selected_narrow_code} - {st.session_state.selected_narrow_desc}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("Not selected")
                if st.button("Select Narrow Field", key="btn_narrow", use_container_width=True, 
                           type="primary" if not st.session_state.selected_narrow_code else "secondary",
                           disabled=not st.session_state.selected_broad_code):
                    if st.session_state.selected_broad_code:
                        st.session_state.show_narrow_modal = True
                        st.rerun()
            
            with col3:
                st.markdown("### 3. Detailed Field")
                if st.button("View Details", key="btn_detail", use_container_width=True,
                           disabled=not st.session_state.selected_narrow_code):
                    if st.session_state.selected_narrow_code:
                        st.session_state.show_detail_modal = True
                        st.rerun()
            
            # 弹出框：选择 Broad Field
            if st.session_state.show_broad_modal:
                with st.expander("🔍 Select Broad Field", expanded=True):
                    st.markdown("### Select a Broad Field")
                    # 显示 broad fields 选择卡片
                    broad_cols = st.columns(3)
                    for idx, (_, row) in enumerate(ased_df.iterrows()):
                        col_idx = idx % 3
                        with broad_cols[col_idx]:
                            broad_code = str(row[code_column]).strip()
                            if len(broad_code) == 1:
                                broad_code = f"0{broad_code}"
                            broad_desc = str(row[description_column]) if description_column else broad_code
                            
                            is_selected = st.session_state.selected_broad_code == broad_code
                            
                            if st.button(
                                f"**{broad_desc}**\n\n`{broad_code}`",
                                key=f"modal_broad_{broad_code}",
                                use_container_width=True,
                                type="primary" if is_selected else "secondary"
                            ):
                                st.session_state.selected_broad_code = broad_code
                                st.session_state.selected_broad_desc = broad_desc
                                st.session_state.show_broad_modal = False
                                # 清除下级选择
                                st.session_state.selected_narrow_code = None
                                st.session_state.selected_narrow_desc = None
                                st.rerun()
                    
                    if st.button("Close", key="close_broad_modal"):
                        st.session_state.show_broad_modal = False
                        st.rerun()
            
            selected_broad_code = st.session_state.selected_broad_code
            
            # 弹出框：选择 Narrow Field
            if st.session_state.show_narrow_modal and selected_broad_code:
                with st.expander("🔍 Select Narrow Field", expanded=True):
                    st.markdown(f"### Select a Narrow Field (Broad: {selected_broad_code})")
                    try:
                        narrow_response = (
                            supabase.table("ased_narrow")
                            .select("*")
                            .execute()
                        )
                        narrow_all = narrow_response.data
                        
                        if narrow_all:
                            # 过滤出 narrow_field_code 的前两位等于 broad_code 的记录
                            narrow_data = [
                                item for item in narrow_all
                                if len(str(item.get('narrow_field_code', ''))) >= 2 and
                                str(item.get('narrow_field_code', ''))[:2] == selected_broad_code
                            ]
                            
                            if narrow_data:
                                narrow_df = pd.DataFrame(narrow_data)
                                
                                # 获取描述列
                                narrow_desc_col = None
                                for col in narrow_df.columns:
                                    if 'description' in col.lower() or 'name' in col.lower() or 'title' in col.lower():
                                        narrow_desc_col = col
                                        break
                                
                                # 显示 narrow fields 卡片（每行3个）
                                narrow_cols = st.columns(3)
                                for idx, (_, row) in enumerate(narrow_df.iterrows()):
                                    col_idx = idx % 3
                                    with narrow_cols[col_idx]:
                                        narrow_code = str(row['narrow_field_code']).strip()
                                        narrow_desc = str(row[narrow_desc_col]) if narrow_desc_col else narrow_code
                                        
                                        is_selected = st.session_state.selected_narrow_code == narrow_code
                                        
                                        if st.button(
                                            f"**{narrow_desc}**\n\n`{narrow_code}`",
                                            key=f"modal_narrow_{narrow_code}",
                                            use_container_width=True,
                                            type="primary" if is_selected else "secondary"
                                        ):
                                            st.session_state.selected_narrow_code = narrow_code
                                            st.session_state.selected_narrow_desc = narrow_desc
                                            st.session_state.show_narrow_modal = False
                                            st.rerun()
                                
                                if st.button("Close", key="close_narrow_modal"):
                                    st.session_state.show_narrow_modal = False
                                    st.rerun()
                            else:
                                st.info(f"No narrow fields found for broad field {selected_broad_code}")
                        else:
                            st.info(f"No narrow fields available in ased_narrow table")
                    except Exception as e:
                        st.error(f"Error loading narrow fields: {str(e)}")
            
            selected_narrow_code = st.session_state.selected_narrow_code
            
            # 弹出框：显示 Detailed Fields
            if st.session_state.show_detail_modal and selected_narrow_code:
                with st.expander(f"📋 Detailed Fields for {selected_narrow_code}", expanded=True):
                    st.markdown(f"### Detailed Fields (Narrow: {selected_narrow_code})")
                    try:
                        detail_response = (
                            supabase.table("ased_detail")
                            .select("detailed_field_code, description")
                            .execute()
                        )
                        detail_all = detail_response.data
                        
                        if detail_all:
                            # 过滤出 detailed_field_code 的前几位等于 narrow_field_code 的记录
                            detail_data = [
                                item for item in detail_all
                                if str(item.get('detailed_field_code', '')).startswith(selected_narrow_code)
                            ]
                            
                            if detail_data:
                                # 显示 detailed fields 卡片（每行3个）
                                detail_cols = st.columns(3)
                                for idx, item in enumerate(detail_data):
                                    col_idx = idx % 3
                                    with detail_cols[col_idx]:
                                        detail_code = str(item.get('detailed_field_code', '')).strip()
                                        detail_desc = str(item.get('description', '')).strip()
                                        
                                        # 使用卡片样式显示
                                        st.markdown(f"""
                                        <div class="selection-card">
                                            <div style="font-weight: 600; color: #007958; margin-bottom: 0.5rem;">
                                                {detail_code}
                                            </div>
                                            <div style="color: #666; font-size: 0.9rem; line-height: 1.4;">
                                                {detail_desc}
                                            </div>
                                        </div>
                                        """, unsafe_allow_html=True)
                                
                                if st.button("Close", key="close_detail_modal"):
                                    st.session_state.show_detail_modal = False
                                    st.rerun()
                            else:
                                st.info(f"No detailed fields found for narrow field {selected_narrow_code}")
                        else:
                            st.info(f"No detailed fields available in ased_detail table")
                    except Exception as e:
                        st.error(f"Error loading detailed fields: {str(e)}")
        
        st.divider()
except Exception as e:
    st.error(f"Error loading Australian Standard Classification of Education (ASCED) data: {e}")

# 初始化 exs 如果不存在
if "exs" not in st.session_state:
    st.session_state.exs = None

if st.session_state.exs:
    flat_list = [job for sublist in st.session_state.exs for job in sublist]
    #st.write(flat_list)
run_btn = st.sidebar.button("GET ANZSCO", type="primary")
SYSTEM_PROMPT = """
You are an expert classifier for the Australian and New Zealand Standard Classification of Occupations (ANZSCO 2021).

Your task: Given one or more occupation titles, identify the most appropriate ANZSCO occupation.

Output policy:
- Always return ONE best-matching occupation for each input title as valid JSON (no prose, no preface, no explanations before/after the JSON).
- Find assessing authority if you can.
- Find skill level if you can.
- Do not ask the user questions. Do not return multiple alternatives. Choose one.

Schema (for each title):
{
"anzsco_title": string,           // official title or closest reasonable label if best-guess
  "anzsco_code": string,            // 6-digit code; if unknown, return "UNKNOWN"
  "assessing_authority": string | "" 
}

Return a JSON array of objects, one per input title.

Example input:
["Hospital Administrator", "UX Designer", "Mechanical Engineer"]

Expected output:
{
  {
   
    "anzsco_code": "111211",
    "anzsco_title": "Corporate General Manager",
   
    "assessing_authority": "IML (Institute of Managers and Leaders)"
  },
  {
   
    "anzsco_code": "232413",
    "anzsco_title": "Multimedia Designer",
  
    "assessing_authority": "VETASSESS"
  },
  {
  
    "anzsco_code": "233512",
    "anzsco_title": "Mechanical Engineer",
    "assessing_authority": "Engineers Australia"
  }
}
"""
# if anz_btn:
#     supabase = get_supabase_client()
#     try:
#             # Query the survey_processed table
#         response = (
#             supabase.table("anzsco")
#             .select("Occupation_Code,Titles")
#             .execute()
#             )
            
#         data = response.data
#         st.write(data)
#     except Exception as e:
#         st.error(f"Error querying Supabase: {e}")






def one_call_unified(jobs: list[str],
                     model: str = "gpt-5-nano") -> dict:
    llm = ChatOpenAI(model_name=model, temperature=0.00001)
    user_prompt = f"""
Titles: "{jobs}"
Return JSON only. No extra text.

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
if "anz" not in st.session_state:
    st.session_state.anz = None

if run_btn:
    with st.spinner("Analysing"):
        result = one_call_unified(flat_list)
        st.session_state.anz = result

# 只有当 anz 存在且不为空时才显示
if st.session_state.anz is not None:
    data = st.session_state.anz
    if data:  # 确保 data 不为空
        df = pd.DataFrame(data)
        st.session_state.df_anz = df
        st.dataframe(df)
