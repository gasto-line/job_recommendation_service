import streamlit as st
import pandas as pd
import random, requests
from requests.exceptions import RequestException
import matplotlib.pyplot as plt
from supabase import create_client, Client
from datetime import datetime, timedelta, timezone


# ---------------------------------------------------------
# Supabase client setup
# ---------------------------------------------------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_ANON_KEY"]

def init_supabase():
    if "supabase" not in st.session_state:
        st.session_state.supabase = create_client(
            SUPABASE_URL,
            SUPABASE_KEY
        )

    supabase = st.session_state.supabase

    if "supabase_session" in st.session_state and st.session_state.supabase_session:
        supabase.auth.set_session(
            st.session_state.supabase_session.access_token,
            st.session_state.supabase_session.refresh_token
        )

    return supabase

supabase = init_supabase()

st.set_page_config(layout="centered")
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

def call_api(api_host, input, input_type: str, method):
    api_url = f"http://{api_host}:8080/{input_type}"
    try:
        if method == "GET":
            response = requests.get(api_url, json=input)
        elif method == "POST":
            response = requests.post(api_url, json=input)
        else:
            raise ValueError("Unsupported HTTP method")
        response.raise_for_status()  # Raise an error for bad status codes
        print("API call successful")
        return response.json()
    except RequestException as e:
        raise RuntimeError(f"API call failed: {e}")

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
            st.session_state["supabase_session"] = response.session
            st.success("You are now logged in!")
            st.rerun()

        except Exception as e:
            st.error(f"Invalid credentials or error: {e}")

    # Password reset
    if st.button("Forgot your password?"):
        if not email:
            st.error("Please enter your email first.")
        else:
            supabase.auth.reset_password_for_email(
                email,
                options={"redirect_to": "https://gasto-line.github.io/job_recommendation_service/reset_pwd/"}
            )
            st.success("Password reset link sent! Check your email.")

# ---------------------------------------------------------
# PROFILE PAGE
# ---------------------------------------------------------
def profile_page():
    st.title("Your Job Profile")
    st.caption("👉 We recommend filling honest answers to get the best job recommendations.")

    target_tab, skillset_tab, experience_tab = st.tabs(
    ["Target job", "Skills", "Experience"]
    )

    with target_tab:
        # Job titles
        st.subheader("Job Titles You're Considering")
        if "job_titles" not in st.session_state:
            st.session_state.job_titles = ["Title 1", "Title 2"]
        for i, title in enumerate(st.session_state.job_titles):
            cols = st.columns([0.8, 0.2])
            st.session_state.job_titles[i] = cols[0].text_input(
                f"Job Title {i+1}", title, key=f"jt_{i}", label_visibility="collapsed"
            )
            if cols[1].button("❌", key=f"del_{i}"):
                st.session_state.job_titles.pop(i)
                st.rerun()

        if st.button("➕ Add a job title"):
            st.session_state.job_titles.append("")
            st.rerun()

        if "Title 1" or "Title 2" in st.session_state.job_titles:
            st.error("Please replace placeholder job titles with your actual target job titles.")
            job_titles= None
        job_titles = st.session_state.job_titles

        # Ideal job description
        st.subheader("Describe Your Ideal Job")
        ideal_job = st.text_area("Short description")

        # -------------------------
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

        categories = sector_table["Category"].tolist().copy()

        CATEGORY_ICONS = {
            "Natural Resources": "🌱",
            "Energy & Utilities": "⚡",
            "Manufacturing": "🏭",
            "Infrastructure & Transport": "🚚",
            "ICT & Digital": "💻",
            "Services & Commerce": "🛍️",
            "Public & Social Systems": "🏛️",
        }
        sector_table["Category"] = sector_table["Category"].apply(
            lambda c: f"{CATEGORY_ICONS[c]} {c}"
        )

        st.dataframe(sector_table.set_index("Category"), hide_index=False)
        sectors = st.multiselect(
            "Select preferred sectors",
            categories
        )

    with skillset_tab:
            
        COMPLEMENT_COLORS = ["#00202e",
                                "#003f5c",
                                    "#2c4875",
                                    "#8a508f",
                                        "#bc5090",
                                        "#ff6361",
                                            "#ff8531",
                                            "#ffa600",
                                                "#ffd380"
            ]
        # -------------------------
        # Technical skills - dynamic table
        st.subheader("Technical Skills distribution")
        st.caption("👉 Choose only your top technical skills (max 5) inluding programming languages, tools, frameworks, etc.")

        if "skills" not in st.session_state:
            st.session_state.skills = [
                {"name": "Python", "Weight (%)": 50},
                {"name": "Cloud", "Weight (%)": 40},
            ]
        for i, skill in enumerate(st.session_state.skills):
            cols = st.columns([0.5, 0.4, 0.1])
            st.session_state.skills[i]["name"] = cols[0].text_input(
                "Skill", skill["name"], key=f"skill_name_{i}", label_visibility="collapsed"
            )

            st.session_state.skills[i]["Weight (%)"] = cols[1].slider(
                "Weight (%)",
                0, 100,
                skill["Weight (%)"],
                step=10,
                key=f"skill_weight_{i}",
                label_visibility="collapsed"
            )

            if cols[2].button("❌", key=f"del_skill_{i}"):
                st.session_state.skills.pop(i)
                st.rerun()

        if st.button("➕ Add a new skill"):
            st.session_state.skills.append({"name": "", "Weight (%)": 0})
            st.rerun()

        tech_df = pd.DataFrame(st.session_state.skills)
        tech_total = tech_df["Weight (%)"].sum()
        #st.write(f"Total = **{tech_total}%**")
        if tech_total != 100:
            st.error("Total must be 100%" \
            "\ncurrent = " + str(tech_total) + "%")

        # Extract labels & values
        labels = [s["name"] for s in st.session_state.skills]
        sizes = [s["Weight (%)"] for s in st.session_state.skills]
        # Define complementary colors (or use random_colors(len(sizes)))
        colors = random.sample(COMPLEMENT_COLORS,len(sizes))
        # Matplotlib figure
        fig, ax = plt.subplots()
        ax.pie(
            sizes,
            labels=labels,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors
        )
        ax.axis('equal')  # Equal aspect ratio ensures the pie is circular.
        # Display in Streamlit
        st.pyplot(fig)

        # -------------------------
        # General skills
        st.subheader("General skills distribution")

        GENERAL_SKILL_ICONS = {
            "Cognitive & Technical": "🧠",
            "Execution & Operational": "🛠️",
            "Social & Communication": "💬",
            "Business & Contextual": "📊"
        }

        general_skills_table = pd.DataFrame([
        ["Cognitive & Technical",
        "Problem-solving, analysis, modeling, technical expertise, creativity"],
        ["Execution & Operational",
        "Project management, planning, QA, documentation"],
        ["Social & Communication",
        "Communication, collaboration, negotiation, empathy"],
        ["Business & Contextual",
        "Business acumen, industry knowledge, risk, strategy"]
        ], columns=["Category", "Includes"])
        skill_families = general_skills_table["Category"].tolist().copy()

        general_skills_table["Category"] = general_skills_table["Category"].apply(
            lambda c: f"{GENERAL_SKILL_ICONS[c]} {c}"
        )
        st.dataframe(general_skills_table, hide_index=True)

        default_weights = [20, 20, 20, 20]
        weights = []
        cols = st.columns(2)  # 2 columns per row, more compact
        for i, family in enumerate(skill_families):
            col = cols[i % 2]
            with col:
                w = col.slider(family, 0, 100, default_weights[i], step=10)
                weights.append(w)

        skill_total = sum(weights)
        st.write(f"Total: **{skill_total}%**")
        if skill_total != 100:
            st.error("Total must be 100%" \
            "\ncurrent = " + str(skill_total) + "%")
        
        skill_df = pd.DataFrame({
            "Category": skill_families,
            "Weight (%)": weights
        })

        # Visualize general skills pie chart
        # Extract labels & values
        labels = skill_families
        sizes = weights
        # Define complementary colors (or use random_colors(len(sizes)))
        colors = random.sample(COMPLEMENT_COLORS,len(sizes))
        # Matplotlib figure
        fig, ax = plt.subplots()
        ax.pie(
            sizes,
            labels=labels,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors
        )
        ax.axis('equal')  # Equal aspect ratio ensures the pie is circular.
        # Display in Streamlit
        st.pyplot(fig)

    with experience_tab:
        # Education
        st.subheader("Equivalent relevant education level")
        education = st.selectbox(
            "Highest relevant education",
            ["-- Select your education level --","None","Bachelor", "Master", "PhD"],
            index = 0,
            label_visibility="collapsed"
        )
        education_map = {
        "None": 0,
        "Bachelor": 1,
        "Master": 2,
        "PhD": 3
        }
        if education == "-- Select your education level --":
            education_code = None
        else:
            education_code = education_map[education]

        # Work experience
        st.subheader("Equivalent years of relevant work experience")
        experience = st.selectbox(
            "Select your range",
            ["-- Select your experience level --","0-6 months","1-2 years", "3-5 years", "6-10 years", "10+ years"],
            index=0,
            label_visibility="collapsed"
        )
        experience_map = {
        "0-6 months": 0,
        "1-2 years": 1,
        "3-5 years": 2,
        "6-10 years": 3,
        "10+ years": 4
        }
        if experience == "-- Select your experience level --":
            experience_code = None
        else:
            experience_code = experience_map[experience]

    # Do not allow profile saving if it was already done in the past 2 hours
    if "last_submission_time" not in st.session_state:
        st.session_state.last_submission_time = None
    COOLDOWN = timedelta(hours=2)
    now = datetime.now()

    # Create a condition to submit: cooldown + required fields filled
    can_submit = True
    if st.session_state.last_submission_time is None:
        pass
    else:
        elapsed = now - st.session_state.last_submission_time
        if elapsed < COOLDOWN:
            remaining = COOLDOWN - elapsed
            can_submit = False
            st.info(f"You can submit again in {remaining.seconds // 60} minutes.")
        else:
            pass
    if tech_total != 100 or skill_total != 100:
        st.error("Please correct the skill weights — totals must be 100%.")
        can_submit = False
    elif job_titles==None or ideal_job==None or sectors==None or education_code==None or experience_code==None:
        st.error("Please fill in all required fields.")
        can_submit = False
    else:
        pass

    submit = st.button("Save profile")
    st.caption("👉 You can update your profile every 2 hours...")

    if submit:
        if can_submit:
            try:
                last_update = datetime.now(timezone.utc).isoformat()
                user_profile={
                    "user_id": st.session_state["user"].id,
                    "job_titles": job_titles,
                    "ideal_job": ideal_job,
                    "technical_skills": tech_df.to_dict("records"),
                    "general_skills": skill_df.to_dict("records"),
                    "education": education_code,
                    "sectors": sectors,
                    "experience": experience_code,
                    "last_update": last_update
                    }
                response=supabase.table("user_profile").upsert(user_profile).execute()
                st.success("Profile saved successfully!")

                if call_api(api_host="api.silkworm.cloud", input=None, input_type="health", method="GET") == {"status": "ok"}:
                    st.success("The API is healthy. Proceeding to submit profile for embedding generation. It will take 10-15 minutes")
                    st.session_state.last_submission_time = datetime.now()
                    call_api(api_host="api.silkworm.cloud", input=user_profile, input_type="ideal_jobs_embeddings", method="POST")
                else:
                    st.error("The API is currently unreachable. Please try again later.")
                
            except Exception as e:
                st.error(f"Error saving profile: {e}")
        else: 
            st.error("Not allowed to submit: either some fields are missing or you are in cooldown period.")

# ---------------------------------------------------------
# MAIN NAVIGATION
# ---------------------------------------------------------
def main():

    if st.session_state["user"]:
        page = st.sidebar.radio("Navigation", ["Profile", "Job Selection"])
        st.session_state["implementation"] = None
        st.sidebar.markdown("---")
        st.session_state["implementation"] = st.sidebar.selectbox(
            "Select implementation for job recommendations",
            ("FastText", "LLM")
        )
        if st.sidebar.button("Refresh selection"):
            #API call to the VM
            payload = { "user_id": st.session_state.user.id, "implementation": st.session_state.implementation}
            if call_api(api_host="api.silkworm.cloud", input=None, input_type="health", method="GET") == {"status": "ok"}:
                st.success("The API is healthy. Proceeding to submit profile for embedding generation. It will take 10-15 minutes for FastText and up to 5 minutes for LLM.")
                st.session_state.last_submission_time = datetime.now()
                call_api(api_host="api.silkworm.cloud", input=payload, input_type="ai_scoring", method="POST")
            else:
                st.error("The API is currently unreachable. Please try again later.")            
        if page == "Profile":
            profile_page()

        elif page == "Job Selection":
            job_ranking_page()

        st.sidebar.markdown("---")
        if st.sidebar.button("Logout"):
            supabase.auth.sign_out()
            st.session_state["user"] = None
            st.session_state["supabase_session"] = None
            st.rerun() 

    else:
        page = st.sidebar.radio("Navigation", ["Login", "Sign Up"])
        if page == "Login":
            login_page()
        else:
            signup_page()

# ---------------------------------------------------------
# JOB RANKING
# ---------------------------------------------------------
def job_ranking_page():
    """implementation = st.radio("Choose implementation", ["FastText", "LLM"])"""
    st.title("Job Recommendations")
    jobs_df = pd.DataFrame()

    if st.session_state.implementation == "FastText":
        jobs_list= supabase.rpc("get_fasttext_topjob",{"p_user_id": st.session_state["user"].id}).execute()
        jobs_df = pd.DataFrame(jobs_list.data)
    elif st.session_state.implementation == "LLM":
        jobs_list= supabase.rpc("get_llm_topjobs",{"p_user_id": st.session_state["user"].id}).execute()
        jobs_df = pd.DataFrame(jobs_list.data)
    else:
        st.error("Unknown implementation selected.")
    if jobs_df.empty:
        st.warning("No job data found.")
        return

    st.subheader("Rate the Jobs")
    scores = {}
    justifications = {}
    applications = {}

    for idx, row in jobs_df.iterrows():
        job_title = row.get("title", "Unknown Title")
        company = row.get("company", "Unknown Company")
        job_url = row.get("url", "#")

        with st.expander(f"{job_title} at {company}"):
            st.write(f"[{job_url}]({job_url})")
            st.write(f"**Location**: {row.get('location', 'N/A')}")
            st.write(f"**Description**: {row.get('description', 'No description available.')[:500]}...")

            # Enable rating this job
            wants_to_rate = st.checkbox("Rate this job?", key=f"rate_{idx}")

            if wants_to_rate:

                # Score input
                score = st.slider(f"Score this job", 1, 10, 5, key=f"score_{idx}")
                scores[idx] = score

                # Justification input
                justification = st.text_area("Optional justification", key=f"justif_{idx}")
                justifications[idx] = justification

                # Application checkbox
                applied = st.checkbox("Tick if you applied", key=f"applied_{idx}")
                applications[idx] = applied

    if st.button("Submit Scores"):
        insert_df= jobs_df.loc[list(scores.keys())]

        insert_df["score"] = insert_df.index.map(scores.get)
        insert_df["comment"] = insert_df.index.map(justifications.get)
        insert_df["applied"] = insert_df.index.map(applications.get)

        insert_df= insert_df[["job_hash", "score", "applied", "comment"]]
        insert_df["user_id"]= st.session_state["user"].id
        
        insert_records= insert_df.to_dict("records")

        try:
            response=supabase.table("user_review").upsert(insert_records).execute()
            st.success("Profile saved successfully!")
        except Exception as e:
            st.error(f"Error saving profile: {e}")

main()

