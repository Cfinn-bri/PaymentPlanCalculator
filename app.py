import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

def calculate_payment_plan(first_payment_date_str, course_end_date_str, total_cost, num_payments, course_started):
    first_payment_date = datetime.strptime(first_payment_date_str, "%d-%m-%Y")
    course_end_date = datetime.strptime(course_end_date_str, "%d-%m-%Y")

    finance_fee = 149
    late_fee = 149 if course_started else 0
    downpayment = 499 if course_started else 199
    remaining_balance = total_cost - downpayment + finance_fee + late_fee

    payment_schedule = [("Immediate Downpayment", f"£{downpayment:.2f}")]
    if course_started:
        payment_schedule.append(("+£149 Late Fee", ""))

    for i in range(num_payments):
        payment_date = first_payment_date + relativedelta(months=i)

        if payment_date > course_end_date:
            break

        monthly_payment = round(remaining_balance / num_payments, 2) if num_payments > 1 else remaining_balance
        payment_schedule.append((payment_date.strftime("%d-%m-%Y"), f"£{monthly_payment:.2f}"))

    return payment_schedule

st.title("Payment Plan Calculator")

# Google Drive direct download link (converted from share link)
EXCEL_URL = "https://drive.google.com/uc?export=download&id=1egHxKEo1PfZZZDNe4oEkISgWwXzfPj93"

try:
    df = pd.read_excel(EXCEL_URL, engine="openpyxl")
    df.columns = df.columns.str.strip().str.lower()

    if all(col in df.columns for col in ["product name", "course start date", "course end date", "tuition pricing"]):
        # Category Selection
        categories = {
            "SQE1": df[df["product name"].str.contains("SQE1", case=False, na=False)],
            "SQE2": df[df["product name"].str.contains("SQE2", case=False, na=False)],
            "Complete SQE": df[df["product name"].str.contains("Complete SQE", case=False, na=False)]
        }

        selected_category = st.selectbox("Select a Category", list(categories.keys()))
        filtered_df = categories[selected_category]

        course_name = st.selectbox("Select a Course", filtered_df["product name"].unique())
        course_data = filtered_df[filtered_df["product name"] == course_name].iloc[0]
