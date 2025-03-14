import streamlit as st
from datetime import datetime
from dateutil.relativedelta import relativedelta

def calculate_payment_plan(course_start_date_str, course_end_date_str, total_cost, num_payments, course_started):
    today = datetime.today()
    course_start_date = datetime.strptime(course_start_date_str, "%d-%m-%Y")
    course_end_date = datetime.strptime(course_end_date_str, "%d-%m-%Y")
    
    finance_fee = 149
    late_fee = 49 if course_started else 0
    downpayment = 499 if course_started else 199
    remaining_balance = total_cost - downpayment + finance_fee + late_fee
    
    # Determine first payment date (1st of the following month from today's date)
    first_payment_date = datetime(today.year, today.month, 1) + relativedelta(months=1)
    
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

course_start_date = st.date_input("Course Start Date")
course_end_date = st.date_input("Course End Date", min_value=course_start_date)
total_cost = st.number_input("Total Course Cost (£)", min_value=0)

# Convert course_start_date to datetime before comparison
course_started = datetime.combine(course_start_date, datetime.min.time()) < datetime.today()

# Determine available installment options (must fit within 12 months before course end)
months_until_end = (course_end_date.year - course_start_date.year) * 12 + (course_end_date.month - course_start_date.month)
available_installments = list(range(1, min(12, months_until_end + 1) + 1))
num_payments = st.selectbox("Select Number of Installments", available_installments)

if st.button("Calculate Payment Plan"):
    if total_cost > 0:
        payment_plan = calculate_payment_plan(course_start_date.strftime("%d-%m-%Y"), course_end_date.strftime("%d-%m-%Y"), total_cost, num_payments, course_started)
        st.subheader("Payment Schedule:")
        for date, amount in payment_plan:
            st.write(f"{date}: {amount}")
    else:
        st.error("Please enter a valid total course cost.")
