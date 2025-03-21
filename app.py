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

uploaded_file = st.file_uploader("Upload Course Excel File", type=["xls", "xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, engine="openpyxl")
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

            course_start_date = pd.to_datetime(course_data["course start date"], dayfirst=True)
            course_end_date = pd.to_datetime(course_data["course end date"], dayfirst=True)
            total_cost = float(course_data["tuition pricing"])

            today = datetime.today()
            first_payment_date = datetime(today.year, today.month, 1) + relativedelta(months=1)
            downpayment_is_499 = today >= datetime.combine(course_start_date, datetime.min.time())
            course_started = today > datetime.combine(course_start_date, datetime.min.time())

            months_until_exam = (course_end_date.year - first_payment_date.year) * 12 + (course_end_date.month - first_payment_date.month)
            months_until_exam = max(months_until_exam, 0)
            available_installments = list(range(1, min(12, months_until_exam + 1) + 1))

            st.write(f"**Start Date:** {course_start_date.strftime('%d-%m-%Y')}")
            st.write(f"**Exam Month:** {course_end_date.strftime('%B %Y')}")
            st.write(f"**Tuition Pricing:** £{total_cost:.2f}")

            if available_installments:
                num_payments = st.selectbox("Select Number of Installments", available_installments)

                if st.button("Calculate Payment Plan"):
                    payment_plan = calculate_payment_plan(
                        first_payment_date.strftime("%d-%m-%Y"),
                        course_end_date.strftime("%d-%m-%Y"),
                        total_cost,
                        num_payments,
                        downpayment_is_499
                    )
                    st.subheader("Payment Schedule:")
                    for date, amount in payment_plan:
                        st.write(f"{date}: {amount}")
            else:
                st.warning("No available payment months before the exam month.")
        else:
            st.error("Excel file must contain columns: Product Name, Course Start Date, Course End Date, Tuition Pricing")
    except Exception as e:
        st.error(f"Failed to process the Excel file: {e}")
