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

        # Stop adding payments if the next one would be after the course end date
        if payment_date > course_end_date:
            break

        monthly_payment = round(remaining_balance / num_payments, 2) if num_payments > 1 else remaining_balance
        payment_schedule.append((payment_date.strftime("%d-%m-%Y"), f"£{monthly_payment:.2f}"))

    return payment_schedule

# Streamlit UI
st.title("Payment Plan Calculator")

uploaded_file = st.file_uploader("Upload Course Excel File", type=["xls", "xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, engine="openpyxl")
        df.columns = df.columns.str.strip().str.lower()

        if all(col in df.columns for col in ["product name", "course start date", "course end date", "total cost"]):
            course_name = st.selectbox("Select a Course", df["product name"].unique())
            course_data = df[df["product name"] == course_name].iloc[0]

            # Convert string dates to datetime if needed
            course_start_date = pd.to_datetime(course_data["course start date"])
            course_end_date_raw = pd.to_datetime(course_data["course end date"])
            total_cost = course_data["total cost"]

            st.write(f"**Start Date:** {course_start_date.strftime('%d-%m-%Y')}")
            st.write(f"**Default Total Cost:** £{total_cost}")

            # Generate month options for up to 2 years after the start date
            max_end_date = course_start_date + relativedelta(years=2)
            month_options = [
                (course_start_date + relativedelta(months=i)).strftime("%B %y")
                for i in range((max_end_date.year - course_start_date.year) * 12 + (max_end_date.month - course_start_date.month) + 1)
            ]

            selected_end_month = st.selectbox("Exam Month", month_options)

            # Convert selected month to last day of that month
            selected_end_date = datetime.strptime(selected_end_month, "%B %y")
            course_end_date = datetime(selected_end_date.year, selected_end_date.month, 1) + relativedelta(day=31)

            # First payment is 1st of next month from today
            today = datetime.today()
            first_payment_date = datetime(today.year, today.month, 1) + relativedelta(months=1)

            # Determine if course has started (downpayment changes only if today >= course start)
            downpayment_is_499 = today >= datetime.combine(course_start_date, datetime.min.time())

            # Determine if course has started (late fee applies if today > course start)
            course_started = today > datetime.combine(course_start_date, datetime.min.time())

            # Allow manual adjustment of total cost if needed
            total_cost = st.number_input("Total Course Cost (£)", min_value=0.0, value=float(total_cost))

            # Determine months available between first payment and exam month
            months_until_exam = (course_end_date.year - first_payment_date.year) * 12 + (course_end_date.month - first_payment_date.month)
            months_until_exam = max(months_until_exam, 0)
            available_installments = list(range(1, min(12, months_until_exam + 1) + 1))

            if available_installments:
                num_payments = st.selectbox("Select Number of Installments", available_installments)

                if st.button("Calculate Payment Plan"):
                    if total_cost > 0:
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
                        st.error("Please enter a valid total course cost.")
            else:
                st.warning("No available payment months before the exam month. Please choose a different exam month.")
        else:
            st.error("Excel file must contain columns: Product Name, Course Start Date, Course End Date, Total Cost")
    except Exception as e:
        st.error(f"Failed to process the Excel file: {e}")
