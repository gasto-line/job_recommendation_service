import streamlit as st
import pandas as pd
from supabase import create_client, Client

# ---------------------------------------------------------
# Supabase client setup
# ---------------------------------------------------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_ANON_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


st.set_page_config(layout="wide")
st.markdown(
    """
    <style>
        .main .block-container {
            max-width: 1200px !important;
            padding-left: 2rem;
            padding-right: 2rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)

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
def signup_page():
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
def login_page():
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
            st.rerun()

        except Exception as e:
            st.error("Invalid credentials or error")

    # Password reset
    if st.button("Forgot your password?"):
        if not email:
            st.error("Please enter your email first.")
        else:
            supabase.auth.reset_password_for_email(
                email,
                options={"redirect_to": "https://job-recommendation-service.streamlit.app"}
            )
            st.success("Password reset link sent! Check your email.")

# ---------------------------------------------------------
# PROFILE PAGE
# ---------------------------------------------------------
def profile_page():
    st.title("Your Job Profile")
    st.info("We recommend filling honest answers to get the best job recommendations.")

    target_tab, skillset_tab, experience_tab = st.tabs(
    ["Target job", "Skills", "Experience"]
    )

    with target_tab:
        # Job titles
        st.subheader("Job Titles You're Considering")
        job_titles =st.data_editor(
            ["Title_1", "Title_2", "Title_3"],
            num_rows="dynamic")

        # Ideal job description
        st.subheader("Describe Your Ideal Job")
        ideal_job = st.text_area("Short description")

        # Preferred sectors
        st.subheader("Preferred Sectors")

        sector_table = pd.DataFrame([
        ["Natural Resources", "Extract from nature", "Farming, mining"],
        ["Energy & Utilities", "Essential utilities", "Power, water, waste"],
        ["Manufacturing", "Transform materials", "Pharma, automotive"],
        ["Infrastructure & Transport", "Build & move", "Logistics, construction"],
        ["ICT & Digital", "Digital systems", "Cloud, AI, telecom"],
        ["Services & Commerce", "Sell goods & services", "Consulting, retail"],
        ["Public & Social Systems", "Govern society", "Health, gov, research"]
        ], columns=["Category", "Core idea", "Examples"])

        st.dataframe(sector_table, hide_index=True)
        sectors = st.multiselect(
            "Select preferred sectors",
            sector_table["Category"].tolist()
        )

    with skillset_tab:
        # Technical skills - dynamic table
        st.subheader("Technical Skills distribution")
        st.info("Choose only your top technical skills (max 5) inluding programming languages, tools, frameworks, etc.")
        tech_df = st.data_editor(
            pd.DataFrame({
                "Category": ["Programming language", "Software", "Tool", "Framework", "Other"],
                "Weight (%)": [20, 20, 20, 20, 20]
            }),
            num_rows="dynamic"
            ,hide_index=True
        )
        tech_total = tech_df["Weight (%)"].sum()
        st.write(f"Total = **{tech_total}%**")

        if tech_total != 100:
            st.warning("Technical skills must total 100%.")

        # General skills
        general_skills_table = pd.DataFrame([
        ["Cognitive & Technical Skills",
        "Problem-solving, analysis, modeling, technical expertise, creativity"],
        ["Execution & Operational Skills",
        "Project management, planning, QA, documentation"],
        ["Social & Communication Skills",
        "Communication, collaboration, negotiation, empathy"],
        ["Business & Contextual Understanding",
        "Business acumen, industry knowledge, risk, strategy"]
        ], columns=["Category", "Includes"])

        st.subheader("Rate your general skills (must total 100%)")
        st.dataframe(general_skills_table, hide_index=True)

        st.caption("👉 Evaluate your relative strengths honestly — the goal is to compare *your own* skills to one another.")
        skill_families = general_skills_table["Category"].tolist()
        default_weights = [20, 20, 20, 20]
        weights = []

        cols = st.columns(2)  # 2 columns per row, more compact

        for i, family in enumerate(skill_families):
            col = cols[i % 2]
            with col:
                w = col.slider(family, 0, 100, default_weights[i], step=10)
                weights.append(w)

        total = sum(weights)
        st.write(f"### Total: **{total}%**")
        if total != 100:
            st.error("The total must be exactly 100%.")
        
        skill_df = pd.DataFrame({
            "Category": skill_families,
            "Weight (%)": weights
        })

    with experience_tab:
        # Education
        st.subheader("Equivalent relevant education level")
        education = st.selectbox(
            "Highest relevant education",
            ["None","Bachelor", "Master", "PhD"]
        )
        education_map = {
        "None": 0,
        "Bachelor": 1,
        "Master": 2,
        "PhD": 3
        }
        education_code = education_map[education]

        # Work experience
        st.subheader("Equivalent years of relevant work experience")
        experience = st.selectbox(
            "Select your range",
            ["0-6 months","1-2 years", "3-5 years", "6-10 years", "10+ years"]
        )
        experience_map = {
        "0-6 months": 0,
        "1-2 years": 1,
        "3-5 years": 2,
        "6-10 years": 3,
        "10+ years": 4
        }
        experience_code = experience_map[experience]

    if st.button("Save profile"):
        if tech_total != 100 or general_total != 100:
            st.error("Please correct the skill weights — totals must be 100%.")
            return

        supabase.table("profiles").upsert({
            "user_id": st.session_state["user"].id,
            "job_titles": job_titles,
            "ideal_job": ideal_job,
            "technical_skills": tech_df.to_dict("records"),
            "general_skills": skill_df.to_dict("records"),
            "education": education_code,
            "sectors": sectors,
            "experience": experience_code
        })
        st.success("Profile saved!")


# ---------------------------------------------------------
# MAIN NAVIGATION
# ---------------------------------------------------------
def main():
    if st.session_state["user"]:
        page = st.sidebar.radio("Navigation", ["Profile", "Top Job Selection"])

        if page == "Profile":
            profile_page()

        elif page == "Top Job Selection":
            st.write("Your job ranking app goes here.")

        st.sidebar.markdown("---")
        if st.sidebar.button("Logout"):
            supabase.auth.sign_out()
            st.session_state["user"] = None
            st.rerun()  

    else:
        page = st.sidebar.radio("Navigation", ["Login", "Sign Up"])
        if page == "Login":
            login_page()
        else:
            signup_page()

main()