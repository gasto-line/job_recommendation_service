import streamlit as st
import supabase


st.subheader("Reset your password")

new_password = st.text_input("New password", type="password")
confirm = st.text_input("Confirm password", type="password")

if st.button("Update password"):
    if new_password != confirm:
        st.error("Passwords do not match")
    else:
        supabase.auth.update_user({"password": new_password})
        st.success("Password updated successfully")
