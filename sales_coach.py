import pandas as pd
import datetime
import numpy as np
import os
import streamlit as st
from pathlib import Path

st.header("Sales Rep Review")

files_dict = {}

# Streamlit file uploader
uploaded_files = st.file_uploader("Upload your files", accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        filename = Path(uploaded_file.name).stem  # Get filename without extension
        
        try:
            # Load file based on extension
            if uploaded_file.name.endswith('.csv'):
                files_dict[filename] = pd.read_csv(uploaded_file, encoding='cp1252')
            elif uploaded_file.name.endswith(('.xls', '.xlsx')):
                files_dict[filename] = pd.read_excel(uploaded_file)
            elif uploaded_file.name.endswith('.txt'):
                files_dict[filename] = pd.read_csv(uploaded_file, delimiter='\t', encoding='cp1252')
            elif uploaded_file.name.endswith('.json'):
                files_dict[filename] = pd.read_json(uploaded_file)
            else:
                st.warning(f"Unsupported file type for {uploaded_file.name}")
                continue
                
            st.success(f"Successfully loaded: {filename}")
            
        except Exception as e:
            st.error(f"Error loading {filename}: {str(e)}")

# Display the loaded dataframes
dfs = []
for name, df in files_dict.items():
    st.write(f"### {name}")
    st.dataframe(df)
    dfs.append(df)

if len(dfs)>0:
    df = dfs[0]
    df['Completed Date'] = pd.to_datetime(df['Completed Date'], errors="coerce")
    df['Date First Bill'] = pd.to_datetime(df['Date First Bill'], errors="coerce")
    df['Week Completed'] = df['Completed Date'].dt.isocalendar().week
    df['Day Completed'] = df['Completed Date'].dt.day_name()
    df['Year Billed'] = df ['Date First Bill'].dt.year
    df['Never Billed'] = df['Date First Bill'].isna()
    df["Apt Set"] = df["Results"].str.contains("Appointment Set", case="False",na=False)
    df["MPC"] = df["Results"].str.contains("MPC", case="False",na=False)

    clients = df.groupby("Company Name").agg(Count=("Results",'size')).sort_values(by=['Count'], ascending=False)
    single_clients = clients[clients["Count"] == 1]
    week_days = df.groupby("Day Completed").agg(Count=("Results",'size')).sort_values(by=['Count'], ascending=False)
    weeks = df.groupby("Week Completed").agg(Count=("Results",'size')).sort_values(by=['Week Completed'], ascending=True)
    apt_set_audit = df[df["Apt Set"]].sort_values("Company Name")

    territories = df.groupby("Territory").agg(Count=("Results",'size')).sort_values(by=['Territory'], ascending=True)
    territories["Ratio"] = territories["Count"] / len(df.index)

    prospect = df.groupby("Never Billed").agg(Count=("Results",'size')).sort_values(by=['Count'], ascending=False)
    prospect["Ratio"] = prospect["Count"] / len(df.index)

    apt_sets = df.groupby("Apt Set").agg(Count=("Results",'size')).sort_values(by=['Count'], ascending=False)
    apt_sets["Ratio"] = prospect["Count"] / len(df.index)

    mpc = df.groupby("MPC").agg(Count=("Results",'size')).sort_values(by=['Count'], ascending=False)

    mutlti_apt_aduit = apt_set_audit.groupby("Company Name").agg(Count=("Results",'size')).sort_values(by=['Count'], ascending=False)


    ## Global Variables
    client_count = len(clients)
    weeks_for_avg = len(weeks)
    single_clients_count = len(single_clients)
    single_client_ratio = round(single_clients_count / client_count,2)
    all_calls = len(df)
    apt_set_calls = len(apt_set_audit)
    mpc_calls = len(mpc)


    ## Visualization
    st.subheader("Top Contacted Clients")
    col1, col2, col3= st.columns(3)
    col1.metric("All Calls", all_calls, delta=None, delta_color="normal", help=None, label_visibility="visible", border=False)
    col2.metric("Clients Contacted", client_count, delta=None, delta_color="normal", help=None, label_visibility="visible", border=False)
    col3.metric("Single Contact Ratio", single_client_ratio, delta=None, delta_color="normal", help="Ratio of clients have only been contacted once.", label_visibility="visible", border=False)
    st.dataframe(clients)

    st.subheader("Timeline")
    col1, col2, col3= st.columns(3)
    col1.metric("Weeks Tracked", weeks_for_avg, delta=None, delta_color="normal", help=None, label_visibility="visible", border=False)
    col2.metric("Calls Per Week", all_calls/weeks_for_avg, delta=None, delta_color="normal", help=None, label_visibility="visible", border=False)
    col3.metric("Clients Per Week", client_count/weeks_for_avg, delta=None, delta_color="normal", help=None, label_visibility="visible", border=False)
    st.write("Calls per Week")
    st.bar_chart(weeks, x_label="Week Number", y_label="Call Count")
    st.write("Documented Days")
    st.bar_chart(week_days, x_label="Day", y_label="Call Count")

    st.subheader("Call Audit")
    col1, col2, col3= st.columns(3)
    col1.metric("All Calls", all_calls, delta=None, delta_color="normal", help=None, label_visibility="visible", border=False)
    col2.metric("Appointment Sets", apt_set_calls, delta=None, delta_color="normal", help=None, label_visibility="visible", border=False)
    col3.metric("MPC", mpc_calls, delta=None, delta_color="normal", help=None, label_visibility="visible", border=False)
    st.write("Appointment Set Audit")
    st.dataframe(apt_set_audit)
    st.write("Clients with Multiple Appointments")
    st.dataframe(mutlti_apt_aduit)





