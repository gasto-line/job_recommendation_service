import streamlit as st
from supabase import create_client, Client

# ---------------------------------------------------------
# Supabase client setup
# ---------------------------------------------------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_ANON_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------------------------------------------------
# Helper: store session in Streamlit
# ---------------------------------------------------------
def init_session():
    if "user" not in st.session_state:
        st.session_state["user"] = None

init_session()

# ---------------------------------------------------------
# Sign up page (user registration)
# ---------------------------------------------------------
def signup():
    st.subheader("Create an account")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm = st.text_input("Confirm Password", type="password")

    if st.button("Sign up"):
        if password != confirm:
            st.error("Passwords do not match.")
            return

        try:
            response = supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            st.success("Account created! Please log in.")
        except Exception as e:
            st.error(f"Signup error: {e}")

# ---------------------------------------------------------
# Login page
# ---------------------------------------------------------
def login():
    st.subheader("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            st.session_state["user"] = response.user
            st.success("You are now logged in!")

        except Exception as e:
            st.error("Invalid credentials or error")

# ---------------------------------------------------------
# Protected dashboard
# ---------------------------------------------------------
def dashboard():
    st.title("Private dashboard")
    st.write(f"Welcome, **{st.session_state['user'].email}**!")

    if st.button("Logout"):
        supabase.auth.sign_out()
        st.session_state["user"] = None

# ---------------------------------------------------------
# Main navigation logic
# ---------------------------------------------------------
if st.session_state["user"]:
    dashboard()
else:
    menu = st.sidebar.radio("Navigation", ["Login", "Sign up"])

    if menu == "Login":
        login()
    else:
        signup()
