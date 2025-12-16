import streamlit as st
from supabase import create_client

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_ANON_KEY"]
supabase = create_client(
            SUPABASE_URL,
            SUPABASE_KEY
        )

st.subheader("Reset your password")

new_password = st.text_input("New password", type="password")
confirm = st.text_input("Confirm password", type="password")

if st.button("Update password"):
    if new_password != confirm:
        st.error("Passwords do not match")
    else:
        supabase.auth.update_user({"password": new_password})
        st.success("Password updated successfully")
