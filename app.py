import streamlit as st

USERNAME = "admin"
PASSWORD = "123"

def login():
    st.title("تسجيل الدخول - منصة فيصل")
    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")

    if st.button("دخول"):
        if username == USERNAME and password == PASSWORD:
            st.session_state.logged_in = True
            st.success("تم تسجيل الدخول بنجاح")
        else:
            st.error("كلمة المرور غير صحيحة")

def main_app():
    st.title("مرحباً بك في منصة الأسهم الذكية - فيصل")
    st.write("كل البيانات والوظائف الخاصة ستظهر هنا بعد تسجيل الدخول.")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
else:
    main_app()
