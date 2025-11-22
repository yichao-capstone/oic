import streamlit as st
import json
import pandas as pd
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from person import get_supabase_client

# 获取 Supabase 客户端
supabase = get_supabase_client()

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
            # 添加卡片样式
            st.markdown("""
            <style>
            .field-card {
                background: white;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                padding: 1.5rem;
                margin: 0.5rem 0;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .field-card:hover {
                border-color: #007958;
                box-shadow: 0 4px 8px rgba(0,121,88,0.2);
                transform: translateY(-2px);
            }
            .field-card.selected {
                border-color: #007958;
                background: #f0f9f7;
                box-shadow: 0 4px 12px rgba(0,121,88,0.3);
            }
            .field-code {
                font-size: 0.9rem;
                color: #666;
                margin-top: 0.5rem;
            }
            .field-title {
                font-size: 1.1rem;
                font-weight: 600;
                color: #333;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # 第一级：选择 Broad Field（卡片形式）
            st.markdown("### 1. Select Broad Field")
            
            # 初始化选中的 broad field
            if "selected_broad_code" not in st.session_state:
                st.session_state.selected_broad_code = None
            
            # 显示 broad fields 卡片
            broad_cols = st.columns(3)
            for idx, (_, row) in enumerate(ased_df.iterrows()):
                col_idx = idx % 3
                with broad_cols[col_idx]:
                    broad_code = str(row[code_column]).strip()
                    if len(broad_code) == 1:
                        broad_code = f"0{broad_code}"
                    broad_desc = str(row[description_column]) if description_column else broad_code
                    
                    is_selected = st.session_state.selected_broad_code == broad_code
                    card_class = "selected" if is_selected else ""
                    
                    if st.button(
                        f"**{broad_desc}**\n\n`{broad_code}`",
                        key=f"broad_{broad_code}",
                        use_container_width=True,
                        type="primary" if is_selected else "secondary"
                    ):
                        st.session_state.selected_broad_code = broad_code
                        # 清除下级选择
                        if "selected_narrow_code" in st.session_state:
                            del st.session_state.selected_narrow_code
                        st.rerun()
            
            selected_broad_code = st.session_state.selected_broad_code
            
            # 第二级：根据选择的 Broad Field 显示 Narrow Fields 卡片
            if selected_broad_code:
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
                            
                            # 初始化选中的 narrow field
                            if "selected_narrow_code" not in st.session_state:
                                st.session_state.selected_narrow_code = None
                            
                            st.markdown("---")
                            st.markdown("### 2. Select Narrow Field")
                            
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
                                        key=f"narrow_{narrow_code}",
                                        use_container_width=True,
                                        type="primary" if is_selected else "secondary"
                                    ):
                                        st.session_state.selected_narrow_code = narrow_code
                                        st.rerun()
                            
                            selected_narrow_code = st.session_state.selected_narrow_code
                            
                            # 第三级：根据选择的 Narrow Field 显示 Detailed Fields 卡片
                            if selected_narrow_code:
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
                                            st.markdown("---")
                                            st.markdown("### 3. Detailed Fields")
                                            
                                            # 显示 detailed fields 卡片（每行3个）
                                            detail_cols = st.columns(3)
                                            for idx, item in enumerate(detail_data):
                                                col_idx = idx % 3
                                                with detail_cols[col_idx]:
                                                    detail_code = str(item.get('detailed_field_code', '')).strip()
                                                    detail_desc = str(item.get('description', '')).strip()
                                                    
                                                    # 使用卡片样式显示
                                                    st.markdown(f"""
                                                    <div style="
                                                        background: white;
                                                        border: 2px solid #e0e0e0;
                                                        border-radius: 10px;
                                                        padding: 1rem;
                                                        margin-bottom: 1rem;
                                                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                                                    ">
                                                        <div style="font-weight: 600; color: #007958; margin-bottom: 0.5rem;">
                                                            {detail_code}
                                                        </div>
                                                        <div style="color: #666; font-size: 0.9rem;">
                                                            {detail_desc}
                                                        </div>
                                                    </div>
                                                    """, unsafe_allow_html=True)
                                        else:
                                            st.info(f"No detailed fields found for narrow field {selected_narrow_code}")
                                    else:
                                        st.info(f"No detailed fields available in ased_detail table")
                                except Exception as e:
                                    st.error(f"Error loading detailed fields: {str(e)}")
                        else:
                            st.info(f"No narrow fields found for broad field {selected_broad_code}")
                    else:
                        st.info(f"No narrow fields available in ased_narrow table")
                except Exception as e:
                    st.error(f"Error loading narrow fields: {str(e)}")
        
        st.divider()
except Exception as e:
    st.error(f"Error loading Australian Standard Classification of Education (ASCED) data: {e}")

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
st.session_state.anz=None
if run_btn:
    with st.spinner("Analysing"):
        result = one_call_unified(flat_list)

        st.session_state.anz=result
#st.write(st.session_state.anz)
data =st.session_state.anz
df = pd.DataFrame(data)
st.session_state.df_anz=df
st.dataframe(df)
