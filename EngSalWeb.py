import streamlit as st
import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import LabelEncoder


model = joblib.load("RanForParCol.joblib")


page = st.sidebar.selectbox("Navigation", ["Predict Salary", "Career Tracker"])


if page == "Predict Salary":

    st.title(" Engineer Salary Prediction Web Application")
    st.write("Enter details to predict salary")

    df_raw = pd.read_csv("EngineerVis.csv")
    df = df_raw.copy()

    le_dict = {}
    for col in df.select_dtypes(include='object').columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        le_dict[col] = le

  
    discipline = st.selectbox("Engineering Discipline", df_raw['Engineering Discipline'].unique())

    experience = st.number_input("Years of Experience", min_value=0, max_value=20, step=1)

    location = st.selectbox("Location", df_raw['Location'].unique())

    company = st.selectbox("Company", df_raw['Company'].unique())

    category = st.selectbox("Category", df_raw['Category'].unique())


    def encode_input():
        return [
            le_dict['Engineering Discipline'].transform([discipline])[0],
            experience,
            le_dict['Location'].transform([location])[0],
            le_dict['Company'].transform([company])[0],
            le_dict['Category'].transform([category])[0]
        ]

 
    if st.button("Predict Salary"):

        input_data = encode_input()

        input_df = pd.DataFrame([input_data], columns=[
            'Engineering Discipline',
            'Years of Experience',
            'Location',
            'Company',
            'Category'
        ])

        prediction = model.predict(input_df)[0]

        st.success(f" Annual Salary: ₹ {int(prediction):,}")
        st.success(f" Monthly Salary: ₹ {round(prediction/12, 2):,}")

#                                  CAREER TRACKER
elif page == "Career Tracker":

    st.title(" Career Tracker")

    file_path = "UserDataVis.csv"

    try:
        dfu = pd.read_csv(file_path)
        # st.dataframe(dfu)
        dfu = pd.read_csv(file_path)
        dfu['Password'] = dfu['Password'].astype(str)
        dfu['Date'] = pd.to_datetime(dfu['Date'])
    except:
        dfu = pd.DataFrame(columns=[
            'UserName', 'Password', 'Date',
            'Engineering Discipline', 'Years of Experience',
            'Location', 'Company', 'Category', 'Salary'
        ])

    if not dfu.empty:
        dfu['Date'] = pd.to_datetime(dfu['Date'])

    option = st.radio("Choose Action", ["Track Career", "Add Career Record", "Delete Record"])

    if option == "Track Career":

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Track Career"):

            user_data = dfu[
                (dfu['UserName'] == username) &
                (dfu['Password'] == password)
            ]

            if user_data.empty:
                st.error("❌ User not found")
            else:
                st.success(f"Showing data for {username}")

                user_data = user_data.sort_values('Date')

                st.dataframe(user_data)

                for inten in user_data['Category']:
                    if inten == "Intenship":
                        due = user_data[user_data['Category'] == 'Intenship']
                        st.write(f"### {username} done Intenship for period of {due['Years of Experience'][0]} Years")
                    # else:
                    #     st.write(f"### {username} dosen't")


                st.write("### Salary Growth")
                st.line_chart(user_data.set_index('Date')['Salary'])

                st.write("### Experience Growth")
                st.line_chart(user_data.set_index('Date')['Years of Experience'])


#                                  ADD CAREER 

    elif option == "Add Career Record":

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        base_df = pd.read_csv("EngineerVis.csv")

        discipline = st.selectbox("Engineering Discipline", base_df['Engineering Discipline'].unique())

        experience = st.number_input("Years of Experience", min_value=0.0, max_value=30.0, step=0.1)

        location = st.selectbox("Location", base_df['Location'].unique())

        company = st.text_input("Company")

        category = st.selectbox("Category", base_df['Category'].unique())

        salary = st.number_input("Salary", min_value=0, step=1000)

        date = st.date_input("Date")

        if st.button("Add Record"):

            if username == "" or password == "":
                st.warning(" Username & Password required")
            else:
                new_row = pd.DataFrame([{
                    'UserName': username,
                    'Password': password,
                    'Date': pd.to_datetime(date),
                    'Engineering Discipline': discipline,
                    'Years of Experience': experience,
                    'Location': location,
                    'Company': company,
                    'Category': category,
                    'Salary': salary
                }])

                dfu = pd.concat([dfu, new_row], ignore_index=True)
                dfu.to_csv(file_path, index=False)

                st.success("✅ Record Added Successfully!")

                st.dataframe(dfu.tail())
    elif option == "Delete Record":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        userdel_data = dfu[
            (dfu['UserName'] == username) &
            (dfu['Password'] == password)]
        if userdel_data.empty:
            st.error("❌ User not found")
        else:
            st.success(f"Showing data for {username}")

            userdel_data = userdel_data.sort_values('Date')

            st.dataframe(userdel_data)

         
            st.write("### Delete Record")

            record_index = st.selectbox(
                "Select record to delete (by index)",
                userdel_data.index
            )

            if st.button("Delete Selected Record"):

                dfu = dfu.drop(index=record_index)

                dfu.to_csv(file_path, index=False)

                st.success("✅ Record deleted successfully!")

                # st.experimental_rerun()
