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
        st.markdown("### ASCED Broad Fields")
        ased_df = pd.DataFrame(ased_broad_data)
        st.dataframe(ased_df, use_container_width=True)
        st.divider()
except Exception as e:
    st.error(f"Error loading ASCED data: {e}")

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
