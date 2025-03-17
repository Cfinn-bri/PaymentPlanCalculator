import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

def load_course_data(uploaded_file):
    try:
        df = pd.read_excel(uploaded_file, engine='openpyxl')  # Ensure openpyxl is used
        return df
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        return None

def calculate_payment_plan(course_start_date_str, course_end_date_str, total_cost, num_payments, course_started):
    today = datetime.today()
    course_start_date = datetime.strptime(course_start_date_str, "%d-%m-%Y")
    course_end_date = datetime.strptime(course_end_date_str, "%d-%m-%Y")
    
    finance_fee = 149
    late_fee = 49 if course_started else 0
    downpayment = 499 if course_started else 199
    remaining_balance = total_cost - downpayment + finance_fee + late_fee
    
    # First payment always on the 1st of the course start month
    first_payment_date = datetime(course_start_date.year, course_start_date.month, 1)
    
    payment_schedule = [("Immediate Downpayment", f"£{downpayment:.2f}")]
    if course_started:
        payment_schedule.append(("+£49 Late Fee", ""))
    
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

if uploaded_file is not None:
    df = load_course_data(uploaded_file)
    
    # Ensure required columns exist
    required_columns = ["Product Name", "Course Start Date", "Course End Date"]
    if df is not None and all(col in df.columns for col in required_columns):
        
        # Dropdown for selecting a course
        course_name = st.selectbox("Select Course", df["Product Name"].unique())
        
        # Get selected course details
        selected_course = df[df["Product Name"] == course_name].iloc[0]
        course_start_date = selected_course["Course Start Date"].strftime("%d-%m-%Y")
        course_end_date = selected_course["Course End Date"].strftime("%d-%m-%Y")
        
        st.write(f"**Start Date:** {course_start_date}")
        st.write(f"**End Date:** {course_end_date}")
        
        total_cost = st.number_input("Total Course Cost (£)", min_value=0)
        
        # Convert course_start_date to datetime before comparison
        course_started = datetime.strptime(course_start_date, "%d-%m-%Y") < datetime.today()
        
        # Determine available installment options (must fit within 12 months before course end)
        course_end_dt = datetime.strptime(course_end_date, "%d-%m-%Y")
        months_until_end = (course_end_dt.year - datetime.today().year) * 12 + (course_end_dt.month - datetime.today().month)
        available_installments = list(range(1, min(12, months_until_end + 1) + 1))
        num_payments = st.selectbox("Select Number of Installments", available_installments)
        
        if st.button("Calculate Payment Plan"):
            if total_cost > 0:
                payment_plan = calculate_payment_plan(course_start_date, course_end_date, total_cost, num_payments, course_started)
                st.subheader("Payment Schedule:")
                for date, amount in payment_plan:
                    st.write(f"{date}: {amount}")
            else:
                st.error("Please enter a valid total course cost.")
    else:
        st.error("Uploaded file is missing required columns: Product Name, Course Start Date, Course End Date.")
