from __future__ import annotations
import streamlit as st
import json
import pandas as pd
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
import os
from typing import List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI



st.dataframe(st.session_state.df_anz)
if st.session_state.anz:
    df=st.session_state.df_anz
run_btn = st.sidebar.button("GET unis", type="primary")


class UniItem(BaseModel):
    university: str = Field(..., description="Australian university name")
    example_degrees: List[str] = Field(..., description="1–2 example degree names offered by this university")

class Recommendation(BaseModel):
    anzsco_code: str
    anzsco_title: str
    recommended_majors: List[str]
    recommended_universities: List["UniItem"]  # Use string annotation for forward reference
    rationale: str

# ---------- Core prompt template ----------
SYSTEM_PROMPT = """
You are an Australian higher-education advisor. 
Your task is to map ANZSCO occupations to suitable Australian university majors and institutions.

Guidelines:
- Use only Australian universities and nationally recognised degree titles.
- Recommend majors aligned with the occupation’s skills and knowledge base.
- Recommend universities that clearly offer those programs (no guesses).
- If uncertain, provide your best professional inference.
- No filler text, URLs, or migration/visa comments.

Output rules:
- Return valid JSON conforming to the schema.
- No explanations or commentary outside JSON.
"""

USER_PROMPT_TEMPLATE = """
For the following ANZSCO occupation, recommend up to {major_count} majors and exactly {uni_count} Australian universities.

Input:
- Code: {anzsco_code}
- Title: {anzsco_title}

Output schema:
{{
  "anzsco_code": "string",
  "anzsco_title": "string",
  "recommended_majors": ["string", ...],
  "recommended_universities": [
    {{"university": "string", "example_degrees": ["string", ...]}}, ...
  ],
  "rationale": "string"
}}
Return JSON only.
"""

# ---------- Model wrapper ----------
def recommend_for_row(anzsco_code: str, anzsco_title: str, major_count=5, uni_count=5) -> Recommendation:
    llm = ChatOpenAI(model="gpt-5", temperature=0)
    
    user_prompt = USER_PROMPT_TEMPLATE.format(
        anzsco_code=anzsco_code,
        anzsco_title=anzsco_title,
        major_count=major_count,
        uni_count=uni_count
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

    response = llm.invoke(messages)
    content = response.content.strip()

    # Parse JSON safely
    try:
        data = json.loads(content)
        return Recommendation(**data)
    except Exception as e:
        raise ValueError(f"Invalid JSON output: {e}\nRaw: {content}")

# ---------- Batch processing ----------
def recommend_for_df(df: pd.DataFrame, major_count=5, uni_count=5) -> pd.DataFrame:
    rows = []
    for _, row in df.iterrows():
        rec = recommend_for_row(
            str(row["anzsco_code"]),
            str(row["anzsco_title"]),
            major_count=major_count,
            uni_count=uni_count
        )
        rows.append({
            "anzsco_code": rec.anzsco_code,
            "anzsco_title": rec.anzsco_title,
            "recommended_majors": rec.recommended_majors,
            "recommended_universities": [u.model_dump() for u in rec.recommended_universities],
            "rationale": rec.rationale
        })
    return pd.DataFrame(rows)
if run_btn:
     with st.spinner("Analysing"):

        df_out = recommend_for_df(df)
        st.dataframe(df_out)