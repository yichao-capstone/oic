import streamlit as st
import pandas as pd
from supabase_client import get_supabase_client

# 获取 Supabase 客户端
supabase = get_supabase_client()

# 页面标题
st.title("ANZSCO Occupation Classification")
st.markdown("Browse Australian and New Zealand Standard Classification of Occupations")

# ANZSCO Major Groups 定义
MAJOR_GROUPS = {
    "1": "Managers",
    "2": "Professionals",
    "3": "Technicians and Trades Workers",
    "4": "Community and Personal Service Workers",
    "5": "Clerical and Administrative Workers",
    "6": "Sales Workers",
    "7": "Machinery Operators and Drivers",
    "8": "Labourers"
}

# 初始化 session state
if "anzsco_data" not in st.session_state:
    st.session_state.anzsco_data = None
if "selected_major_group" not in st.session_state:
    st.session_state.selected_major_group = None

# 加载数据（自动加载，使用缓存提高性能）
@st.cache_data
def load_anzsco_data():
    try:
        response = (
            supabase.table("anzsco")
            .select("*")
            .execute()
        )
        return response.data
    except Exception as e:
        st.error(f"Error loading ANZSCO data: {e}")
        return None

# 自动加载数据（首次加载或缓存失效时）
if st.session_state.anzsco_data is None:
    with st.spinner("Loading ANZSCO data..."):
        st.session_state.anzsco_data = load_anzsco_data()
        if st.session_state.anzsco_data:
            st.success(f"✅ Loaded {len(st.session_state.anzsco_data)} occupations")

# 如果有数据，显示分类
if st.session_state.anzsco_data:
    data = st.session_state.anzsco_data
    df = pd.DataFrame(data)
    
    # 检查列名
    code_col = None
    title_col = None
    
    for col in df.columns:
        col_lower = col.lower()
        if 'code' in col_lower or 'occupation_code' in col_lower:
            code_col = col
        if 'title' in col_lower or 'titles' in col_lower or 'occupation' in col_lower:
            title_col = col
    
    if not code_col or not title_col:
        st.warning(f"Could not find required columns. Available columns: {list(df.columns)}")
        st.dataframe(df.head())
    else:
        # 确保代码列为字符串类型，处理 NaN 和空值
        df[code_col] = df[code_col].fillna('').astype(str).str.strip()
        # 过滤掉空字符串和 'nan' 字符串
        df = df[(df[code_col] != '') & (df[code_col] != 'nan')]
        
        # 添加 Major Group 列
        def get_major_group(code):
            if not code or code == 'nan' or code == '':
                return None
            code_str = str(code).strip()
            if len(code_str) >= 1:
                first_digit = code_str[0]
                return first_digit if first_digit in MAJOR_GROUPS else None
            return None
        
        df['Major_Group'] = df[code_col].apply(get_major_group)
        df['Major_Group_Name'] = df['Major_Group'].map(MAJOR_GROUPS)
        
        # 过滤掉无效的数据
        df = df[df['Major_Group'].notna()]
        
        # 再次确保代码列是字符串类型（在过滤后）
        df[code_col] = df[code_col].astype(str)
        
        # 显示统计信息
        st.markdown("### 📊 Overview")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Occupations", len(df))
        
        with col2:
            st.metric("Major Groups", df['Major_Group'].nunique())
        
        with col3:
            # 使用 apply 方法提取前2位，避免 .str 访问器问题
            sub_major_codes = df[code_col].apply(lambda x: str(x)[:2] if x and str(x) != 'nan' else '')
            sub_major_count = sub_major_codes[sub_major_codes != ''].nunique()
            st.metric("Sub-Major Groups", sub_major_count)
        
        with col4:
            # 使用 apply 方法提取前4位，避免 .str 访问器问题
            unit_codes = df[code_col].apply(lambda x: str(x)[:4] if x and str(x) != 'nan' else '')
            unit_count = unit_codes[unit_codes != ''].nunique()
            st.metric("Unit Groups", unit_count)
        
        st.divider()
        
        # 按 Major Group 分类显示
        st.markdown("### 🗂️ Browse by Major Group")
        
        # 创建标签页，每个 Major Group 一个标签
        major_groups = sorted(df['Major_Group'].unique())
        tabs = st.tabs([f"{MAJOR_GROUPS.get(mg, 'Unknown')} ({mg})" for mg in major_groups])
        
        for idx, major_group in enumerate(major_groups):
            with tabs[idx]:
                group_df = df[df['Major_Group'] == major_group].copy()
                
                # 确保代码列为字符串类型（再次确认）
                group_df[code_col] = group_df[code_col].astype(str)
                
                # 添加 Sub-Major Group 列（使用 apply 避免 .str 访问器问题）
                group_df['Sub_Major_Group'] = group_df[code_col].apply(lambda x: str(x)[:2] if x and str(x) != 'nan' else '')
                
                # 添加 Unit Group 列（使用 apply 避免 .str 访问器问题）
                group_df['Unit_Group'] = group_df[code_col].apply(lambda x: str(x)[:4] if x and str(x) != 'nan' else '')
                
                st.markdown(f"#### {MAJOR_GROUPS.get(major_group, 'Unknown')} - {len(group_df)} occupations")
                
                # 搜索框
                search_term = st.text_input(
                    "🔍 Search occupations",
                    key=f"search_{major_group}",
                    placeholder="Enter occupation title or code..."
                )
                
                # 确保列为字符串类型
                filtered_df = group_df.copy()
                filtered_df[code_col] = filtered_df[code_col].astype(str)
                if title_col:
                    filtered_df[title_col] = filtered_df[title_col].fillna('').astype(str)
                
                # 过滤数据
                if search_term:
                    # 使用 apply 方法进行搜索，避免 .str 访问器问题
                    code_mask = filtered_df[code_col].apply(lambda x: search_term.lower() in str(x).lower() if x else False)
                    title_mask = filtered_df[title_col].apply(lambda x: search_term.lower() in str(x).lower() if x else False)
                    mask = code_mask | title_mask
                    filtered_df = filtered_df[mask]
                
                # 按 Sub-Major Group 分组显示
                sub_major_groups = sorted(filtered_df['Sub_Major_Group'].unique())
                
                for sub_major in sub_major_groups:
                    sub_df = filtered_df[filtered_df['Sub_Major_Group'] == sub_major]
                    
                    with st.expander(f"Sub-Major Group {sub_major} ({len(sub_df)} occupations)", expanded=False):
                        # 按 Unit Group 分组
                        unit_groups = sorted(sub_df['Unit_Group'].unique())
                        
                        for unit_group in unit_groups:
                            unit_df = sub_df[sub_df['Unit_Group'] == unit_group]
                            
                            st.markdown(f"**Unit Group {unit_group}** ({len(unit_df)} occupations)")
                            
                            # 显示职业列表
                            display_df = unit_df[[code_col, title_col]].copy()
                            display_df.columns = ['Code', 'Occupation Title']
                            display_df = display_df.sort_values('Code')
                            
                            st.dataframe(
                                display_df,
                                use_container_width=False,
                                hide_index=True,
                                height=min(200, len(display_df) * 30 + 40)
                            )
                            
                            st.markdown("<br>", unsafe_allow_html=True)
        
        st.divider()
        
        # 完整数据表格（可选）
        with st.expander("📋 View All Data", expanded=False):
            st.dataframe(
                df[[code_col, title_col, 'Major_Group_Name']].sort_values(code_col),
                use_container_width=False,
                height=400
            )
            
            # 下载按钮
            csv = df[[code_col, title_col, 'Major_Group_Name']].to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name="anzsco_data.csv",
                mime="text/csv"
            )

else:
    st.info("⏳ Loading ANZSCO data... Please wait.")

