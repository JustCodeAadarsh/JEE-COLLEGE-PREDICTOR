import streamlit as st
import pandas as pd
import numpy as np

# 1. Page Config
st.set_page_config(page_title="JEE College Predictor", layout="wide")
st.title("🎓 JEE Mains & Advanced College Predictor")
st.write("Goooood Luck. ╰(*°▽°*)╯")

st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #059669 !important; /* Green background */
        color: white !important;              /* White text */
        border: none !important;
    }
    div.stButton > button:first-child:hover {
        background-color: #047857 !important; /* Darker green on hover */
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Data Loader Engine
@st.cache_data
def load_and_prep_data():
    df = pd.read_csv("data.csv")
    
    # Map Excel headers to system variables
    df = df.rename(columns={
        "Institute": "institute",
        "Academic Program Name": "program",
        "Seat Type": "category",
        "Gender": "gender",
        "Closing Rank": "closing_rank"
    })
    
    df["closing_rank"] = pd.to_numeric(df["closing_rank"], errors='coerce')
    df = df.dropna(subset=["closing_rank"])
    
    # Route IITs to Advanced, others to Main
    df["exam_type"] = df["institute"].apply(
        lambda x: "JEE Advanced" if "INDIAN INSTITUTE OF TECHNOLOGY" in str(x).upper() else "JEE Main"
    )
    return df

try:
    df = load_and_prep_data()

    # 3. Sidebar Inputs
    st.sidebar.header("🎯 Enter Your Details")
    
    exam_choice = st.sidebar.selectbox("Select Exam Type:", ["JEE Main", "JEE Advanced (IIT)"])
    target_exam = "JEE Advanced" if "Advanced" in exam_choice else "JEE Main"
    
    user_rank = st.sidebar.number_input(f"Enter your {target_exam} Rank:", min_value=1, value=10000, step=1)
    
    categories = sorted(df["category"].unique())
    selected_category = st.sidebar.selectbox("Category:", categories)
    
    genders = sorted(df["gender"].unique())
    selected_gender = st.sidebar.selectbox("Gender Pool:", genders)

    # 4. Processing Analytics
    base_mask = (
        (df["exam_type"] == target_exam) & 
        (df["category"] == selected_category) & 
        (df["gender"] == selected_gender)
    )
    filtered_df = df[base_mask].copy()
    
    # Add the submit button to the sidebar form
    search_submitted = st.sidebar.button("Predict Colleges", type="primary", )

    # Only run analytics and show tables IF the button is clicked
    if search_submitted:
        if not filtered_df.empty:
            # Define Safety Windows
            conditions = [
                (filtered_df["closing_rank"] >= user_rank * 1.10),
                (filtered_df["closing_rank"] >= user_rank * 0.90) & (filtered_df["closing_rank"] < user_rank * 1.10),
                (filtered_df["closing_rank"] >= user_rank * 0.85) & (filtered_df["closing_rank"] < user_rank * 0.90)
            ]
            choices = ["🔴 Reach", "🟡 Moderate", "🟢 Safe"]
            filtered_df["Chances"] = np.select(conditions, choices, default="Unlikely")
            
            # Drop unrealistic options
            results_df = filtered_df[filtered_df["Chances"] != "Unlikely"].copy()
            
            # Sort with descending=True so the borderline target ranks (Reach) appear at the top
            results_df = results_df.sort_values(by="closing_rank", ascending=False)

            # UI Result Layout Grid
            st.subheader("📊 Your College Admission guesser")
            
            # Create three distinct side-by-side layout containers
            col_reach, col_mod, col_safe = st.columns(3)
            
            def render_column_bucket(dataframe, chance_label):
                bucket_df = dataframe[dataframe["Chances"] == chance_label]
                
                if bucket_df.empty:
                    st.info(f"No options fall into this category.")
                    return
                
                # Format clean tables for column view
                display_df = bucket_df[["institute", "program", "closing_rank"]].copy()
                display_df.columns = ["Institute", "Branch / Program", "Cutoff"]
                st.dataframe(display_df, width="stretch", hide_index=True)

            # Column 1: Ambitious Targets (Reach)
            with col_reach:
                st.markdown("### 🔴 Reach (Ambitious)")
                render_column_bucket(results_df, "🔴 Reach")

            # Column 2: Competitive Matches (Moderate)
            with col_mod:
                st.markdown("### 🟡 Moderate (Match)")
                render_column_bucket(results_df, "🟡 Moderate")

            # Column 3: High Probability Backups (Safe)
            with col_safe:
                st.markdown("### 🟢 Safe (Secure)")
                render_column_bucket(results_df, "🟢 Safe")
                
        else:
            st.warning("No data rows matched your combination of Category and Gender.")
    else:
        st.info("👈 Configure your profile indicators in the left sidebar pane and click 'Predict Colleges' to generate your report matrix.")

except Exception as e:
    st.error(f"Error loading system: {e}")