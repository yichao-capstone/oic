import streamlit as st

st.set_page_config(
    page_title="OIC Education",
    layout="wide"
)

# 在侧边栏显示 Logo
with st.sidebar:
    st.image("Logo.svg")

# 定义页面
pages = [
    st.Page("./home.py", title="Home", icon="🏠"),
    st.Page("./person.py", title="Personal Survey", icon="📊"),
    st.Page("./ANZSCO.py", title="Australian Standard Classification of Education", icon="📚"),
    st.Page("./anzsco_browser.py", title="ANZSCO Classification", icon="💼"),
    st.Page("./unis.py", title="Universities", icon="🎓"),
]

# 使用 Streamlit 的内置导航
pg = st.navigation(pages)
pg.run()
