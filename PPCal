import streamlit as st
from datetime import datetime
from dateutil.relativedelta import relativedelta

def calculate_payment_plan(course_end_date_str, total_cost):
    today = datetime.today()
    course_end_date = datetime.strptime(course_end_date_str, "%Y-%m-%d")
    
    finance_fee = 149
    first_payment_date = datetime(today.year, today.month, 1)
    if today.day > 1:
        first_payment_date += relativedelta(months=1)
    
    months_available = (course_end_date.year - first_payment_date.year) * 12 + (course_end_date.month - first_payment_date.month) + 1
    num_payments = min(12, months_available)
    
    downpayment = 199
    remaining_balance = total_cost - downpayment + finance_fee
    
    if num_payments > 1:
        downpayment = 499
        remaining_balance = total_cost - downpayment + finance_fee
    
    monthly_payment = round(remaining_balance / num_payments, 2) if num_payments > 1 else remaining_balance

    payment_schedule = [("Immediate Downpayment", f"£{downpayment:.2f}")]
    for i in range(num_payments):
        payment_date = first_payment_date + relativedelta(months=i)
        payment_schedule.append((payment_date.strftime("%Y-%m-%d"), f"£{monthly_payment:.2f}"))
    
    return payment_schedule

# Streamlit UI
st.title("Payment Plan Calculator")

course_end_date = st.date_input("Course End Date", min_value=datetime.today())
total_cost = st.number_input("Total Course Cost (£)", min_value=0)

if st.button("Calculate Payment Plan"):
    if total_cost > 0:
        payment_plan = calculate_payment_plan(course_end_date.strftime("%Y-%m-%d"), total_cost)
        st.subheader("Payment Schedule:")
        for date, amount in payment_plan:
            st.write(f"{date}: {amount}")
    else:
        st.error("Please enter a valid total course cost.")
