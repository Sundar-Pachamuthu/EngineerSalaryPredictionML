import streamlit as st
import pandas as pd
import numpy as np
import joblib
import sqlite3
from sklearn.preprocessing import LabelEncoder

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Engineer Salary Prediction & Career Tracker",
    page_icon="💰",
    layout="wide"
)

# ============================================================
# LOAD MODEL
# ============================================================
model = joblib.load("RanForParCol.joblib")

# ============================================================
# DATABASE CONNECTION
# ============================================================
def get_connection():
    return sqlite3.connect("career_data.db", check_same_thread=False)

def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT,
        password TEXT,
        date TEXT,
        discipline TEXT,
        experience REAL,
        location TEXT,
        company TEXT,
        category TEXT,
        salary REAL
    )
    """)
    conn.commit()
    conn.close()

create_table()

# ============================================================
# DATABASE FUNCTIONS
# ============================================================
def insert_data(username, password, date, discipline, experience, location, company, category, salary):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (username, password, str(date), discipline, experience, location, company, category, salary))
    conn.commit()
    conn.close()

def fetch_user(username, password):
    conn = get_connection()
    query = "SELECT * FROM users WHERE username=? AND password=?"
    df = pd.read_sql_query(query, conn, params=(username, password))
    conn.close()
    return df

def delete_record(username, password, date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    DELETE FROM users WHERE username=? AND password=? AND date=?
    """, (username, password, str(date)))
    conn.commit()
    conn.close()

# ============================================================
# NAVIGATION
# ============================================================
page = st.sidebar.selectbox("Navigation", ["Predict Salary", "Career Tracker"])

# ============================================================
# 🔹 SALARY PREDICTION
# ============================================================
if page == "Predict Salary":

    st.title("💰 Engineer Salary Prediction")

    df_raw = pd.read_csv("EngineerVis.csv")
    df = df_raw.copy()

    le_dict = {}
    for col in df.select_dtypes(include='object').columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        le_dict[col] = le

    discipline = st.selectbox("Engineering Discipline", df_raw['Engineering Discipline'].unique())
    experience = st.number_input("Years of Experience", 0, 20)
    location = st.selectbox("Location", df_raw['Location'].unique())
    company = st.selectbox("Company", df_raw['Company'].unique())
    category = st.selectbox("Category", df_raw['Category'].unique())

    if st.button("Predict Salary"):

        input_data = [
            le_dict['Engineering Discipline'].transform([discipline])[0],
            experience,
            le_dict['Location'].transform([location])[0],
            le_dict['Company'].transform([company])[0],
            le_dict['Category'].transform([category])[0]
        ]

        input_df = pd.DataFrame([input_data], columns=[
            'Engineering Discipline',
            'Years of Experience',
            'Location',
            'Company',
            'Category'
        ])

        prediction = model.predict(input_df)[0]

        st.success(f"💰 Annual Salary: ₹ {int(prediction):,}")
        st.success(f"📅 Monthly Salary: ₹ {round(prediction/12, 2):,}")

# ============================================================
# 🔹 CAREER TRACKER
# ============================================================
elif page == "Career Tracker":

    st.title("📊 Career Tracker")

    option = st.radio("Choose Action", ["Track Career", "Add Career Record", "Delete Record"])

    # ========================================================
    # TRACK CAREER
    # ========================================================
    if option == "Track Career":

        username = st.text_input("Username").strip()
        password = st.text_input("Password", type="password").strip()

        if st.button("Track Career"):

            user_data = fetch_user(username, password)

            if user_data.empty:
                st.error("❌ User not found")
            else:
                st.success(f"Showing data for {username}")

                user_data['date'] = pd.to_datetime(user_data['date'])
                user_data = user_data.sort_values('date')

                st.dataframe(user_data)

                # Internship insight
                if "Internship" in user_data['category'].values:
                    due = user_data[user_data['category'] == 'Internship']
                    exp = due['experience'].max()
                    st.write(f"### {username} completed Internship for {round(exp,1)} Years")

                st.write("### 📈 Salary Growth")
                st.line_chart(user_data.set_index('date')['salary'])

                st.write("### 📊 Experience Growth")
                st.line_chart(user_data.set_index('date')['experience'])

    # ========================================================
    # ADD RECORD
    # ========================================================
    elif option == "Add Career Record":

        base_df = pd.read_csv("EngineerVis.csv")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        discipline = st.selectbox("Engineering Discipline", base_df['Engineering Discipline'].unique())
        experience = st.number_input("Years of Experience", 0.0, 30.0)
        location = st.selectbox("Location", base_df['Location'].unique())
        company = st.text_input("Company")
        category = st.selectbox("Category", base_df['Category'].unique())
        salary = st.number_input("Salary", 0)
        date = st.date_input("Date")

        if st.button("Add Record"):

            if username == "" or password == "":
                st.warning("⚠️ Username & Password required")
            else:
                insert_data(username, password, date, discipline, experience, location, company, category, salary)
                st.success("✅ Record Saved Permanently!")

    # ========================================================
    # DELETE RECORD
    # ========================================================
    elif option == "Delete Record":

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        user_data = fetch_user(username, password)

        if user_data.empty:
            st.error("❌ User not found")
        else:
            user_data['date'] = pd.to_datetime(user_data['date'])
            user_data = user_data.sort_values('date')

            st.dataframe(user_data)

            selected_date = st.selectbox("Select record date", user_data['date'])

            if st.button("Delete Record"):
                delete_record(username, password, selected_date)
                st.success("✅ Record Deleted!")
