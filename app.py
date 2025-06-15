import streamlit as st
import pandas as pd
from datetime import datetime

# Function Definitions
def calculate_on_time_score(required_qty, deliveries, expected_date):
    on_time_qty = sum(qty for date, qty in deliveries if date <= expected_date)
    on_time_percentage = (on_time_qty / required_qty) * 100
    on_time_score = (on_time_percentage / 100) * 10
    return min(round(on_time_score, 2), 10)

def calculate_capacity_score(supplier, month, item_name, required_qty):
    supplier_capacity = supplier_capacity_data.get(supplier, {}).get(month, {}).get(item_name, 0)
    if supplier_capacity == 0:
        return 0
    capacity_score = (supplier_capacity / required_qty) * 10
    return min(round(capacity_score, 2), 10)

def calculate_handling_score(deliveries):
    handling_scores = []
    for delivery in deliveries:
        damaged_items, total_delivered = delivery[4], delivery[1]
        handling_percentage = (damaged_items / total_delivered) * 100
        handling_score = (handling_percentage / 100) * 10
        final_handling_score = 10 - handling_score
        handling_scores.append(final_handling_score)
    return min(round(sum(handling_scores) / len(handling_scores), 2), 10)

def calculate_supplier_defects_score(deliveries):
    defects_scores = []
    for delivery in deliveries:
        defective_items, total_delivered = delivery[5], delivery[1]
        defects_percentage = (defective_items / total_delivered) * 100
        defects_score = (defects_percentage / 100) * 10
        final_supplier_defects_score = 10 - defects_score
        defects_scores.append(final_supplier_defects_score)
    return min(round(sum(defects_scores) / len(defects_scores), 2), 10)

def calculate_issue_resolution_score(capa_issues, closed_issues):
    if capa_issues == 0:  # Avoid division by zero
        return 0
    resolution_percentage = (closed_issues / capa_issues) * 100
    resolution_score = (resolution_percentage / 100) * 10
    return min(round(resolution_score, 2), 10)

def calculate_in_full_score(required_qty, deliveries):
    total_delivered_qty = sum(qty for _, qty, _, _, _, _ in deliveries)
    in_full_percentage = (total_delivered_qty / required_qty) * 100
    in_full_score = (in_full_percentage / 100) * 10
    return min(round(in_full_score, 2), 10)

def calculate_pricing_score(item_name, supplier_price, six_month_avg_price):
    standard_price = standard_pricing_data.get(item_name, 0)
    if standard_price == 0:  # Avoid division by zero
        return 0
    avg_price_ratio = six_month_avg_price / standard_price
    supplier_price_ratio = supplier_price / standard_price
    pricing_score = (avg_price_ratio / supplier_price_ratio) * 10
    return min(round(pricing_score, 2), 10)

def update_six_month_avg_price(current_avg, new_price, num_months=6):
    return ((current_avg * (num_months - 1)) + new_price) / num_months

# Pricing Data
six_month_avg_pricing_data = {
    'Tom': {'Oil': 99.83, 'Chemicals': 111.67, 'Jerry Can': 103.33},
    'Harry': {'Oil': 103.5, 'Chemicals': 112.5, 'Jerry Can': 102.33}
}

standard_pricing_data = {
    'Jerry Can': 120,
    'Chemicals': 100,
    'Oil': 90
}

# Supplier capacity data
supplier_capacity_data = {
    'Tom': {
        1: {'Jerry Can': 97, 'Chemicals': 101, 'Oil': 92},
        2: {'Jerry Can': 134, 'Chemicals': 144, 'Oil': 122},
        3: {'Jerry Can': 110, 'Chemicals': 92, 'Oil': 94},
        4: {'Jerry Can': 117, 'Chemicals': 113, 'Oil': 148},
        5: {'Jerry Can': 91, 'Chemicals': 136, 'Oil': 118},
        6: {'Jerry Can': 116, 'Chemicals': 141, 'Oil': 96},
    },
    'Harry': {
        1: {'Jerry Can': 95, 'Chemicals': 101, 'Oil': 103},
        2: {'Jerry Can': 117, 'Chemicals': 107, 'Oil': 126},
        3: {'Jerry Can': 127, 'Chemicals': 130, 'Oil': 118},
        4: {'Jerry Can': 97, 'Chemicals': 112, 'Oil': 142},
        5: {'Jerry Can': 132, 'Chemicals': 104, 'Oil': 130},
        6: {'Jerry Can': 103, 'Chemicals': 129, 'Oil': 141},
    }
}

# Streamlit Interface
st.title("Supplier Performance Scoring")

# Input Fields
duration_months = st.number_input("Duration in Months", 1, 12, 6)
num_suppliers = st.number_input("Number of Suppliers", 1, 10, 2)
supplier_names = [st.text_input(f"Supplier {i+1} Name", f"Supplier {i+1}") for i in range(num_suppliers)]

# Monthly Inputs
monthly_data = []
updated_six_month_avg_pricing_data = six_month_avg_pricing_data.copy()

for month in range(duration_months):
    st.subheader(f"Month {month + 1}")
    month_data = []
    for supplier in supplier_names:
        st.subheader(f"Data for {supplier}")
        po_date = st.date_input(f"PO Date for {supplier} in Month {month + 1}", datetime(2025, 2, 1))
        num_items = st.number_input(f"Number of Items in PO for {supplier} in Month {month + 1}", 1, 10, 3)
        items = []
        for i in range(num_items):
            item_name = st.text_input(f"Item {i+1} Name for {supplier} in Month {month + 1}", f"Item {i+1}")
            required_qty = st.number_input(f"Required Quantity for {item_name} for {supplier} in Month {month + 1}", 1, 10000, 100)
            expected_date = st.date_input(f"Expected Delivery Date for {item_name} for {supplier} in Month {month + 1}", datetime(2025, 2, 15))
            supplier_price = st.number_input(f"Price Charged for {item_name} by {supplier} in Month {month + 1}", 1.0, 10000.0, 50.0)

            # Update six-month average price
            current_avg_price = updated_six_month_avg_pricing_data.get(supplier, {}).get(item_name, 0)
            new_avg_price = update_six_month_avg_price(current_avg_price, supplier_price)
            if supplier not in updated_six_month_avg_pricing_data:
                updated_six_month_avg_pricing_data[supplier] = {}
            updated_six_month_avg_pricing_data[supplier][item_name] = new_avg_price

            # Calculate pricing score
            pricing_score = calculate_pricing_score(item_name, supplier_price, new_avg_price)

            deliveries = []
            num_deliveries = st.number_input(f"Number of Deliveries for {item_name} for {supplier} in Month {month + 1}", 1, 10, 3)
            for j in range(num_deliveries):
                delivery_date = st.date_input(f"Delivery {j + 1} Date for {item_name} for {supplier} in Month {month + 1}", datetime(2025, 2, 1))
                delivery_qty = st.number_input(f"Delivery {j + 1} Quantity for {item_name} for {supplier} in Month {month + 1}", 1, 10000, 40)
                accepted_items = st.number_input(f"Accepted Items for Delivery {j + 1} of {item_name} for {supplier} in Month {month + 1}", 0, 10000, 90)
                damaged_items = st.number_input(f"Damaged Items for Delivery {j + 1} of {item_name} for {supplier} in Month {month + 1}", 0, 10000, 10)
                defective_items = st.number_input(f"Defective Items for Delivery {j + 1} of {item_name} for {supplier} in Month {month + 1}", 0, 10000, 5)
                rejected_items = delivery_qty - accepted_items
                deliveries.append((delivery_date, delivery_qty, accepted_items, rejected_items, damaged_items, defective_items))
            items.append({
                'name': item_name,
                'required_qty': required_qty,
                'expected_date': expected_date,
                'deliveries': deliveries,
                'pricing_score': pricing_score
            })
        response_score = st.number_input(f"Response Score for {supplier} in Month {month + 1}", 0.0, 10.0, 5.0)
        reliability_score = st.number_input(f"Reliability Score for {supplier} in Month {month + 1}", 0.0, 10.0, 5.0)
        capa_issues = st.number_input(f"Total CAPA Issues for {supplier} in Month {month + 1}", 0, 100, 5)
        closed_issues = st.number_input(f"Closed CAPA Issues for {supplier} in Month {month + 1}", 0, capa_issues, 3)
        issue_resolution_score = calculate_issue_resolution_score(capa_issues, closed_issues)
        month_data.append({
            'supplier': supplier,
            'po_date': po_date,
            'items': items,
            'response_score': min(response_score, 10),
            'reliability_score': min(reliability_score, 10),
            'issue_resolution_score': issue_resolution_score
        })
    monthly_data.append(month_data)

# Weight Input
st.subheader("Weight for Final Score Calculation")
weight_on_time = st.number_input("Weight for On-time Score", 0.1, 0.9, 0.2)
weight_response = st.number_input("Weight for Response Score", 0.1, 0.9, 0.1)
weight_reliability = st.number_input("Weight for Reliability Score", 0.1, 0.9, 0.1)
weight_pricing = st.number_input("Weight for Pricing Score", 0.1, 0.9, 0.1)
weight_capacity = st.number_input("Weight for Capacity Score", 0.1, 0.9, 0.2)
weight_handling = st.number_input("Weight for Handling Score", 0.1, 0.9, 0.1)
weight_defects = st.number_input("Weight for Supplier Defects Score", 0.1, 0.9, 0.1)
weight_in_full = st.number_input("Weight for In-Full Score", 0.1, 0.9, 0.1)
weight_issue_resolution = st.number_input("Weight for Issue Resolution Score", 0.1, 0.9, 0.1)

# Calculations
if st.button("Calculate Scores"):
    supplier_scores = {supplier: [] for supplier in supplier_names}
    
    for month, month_data in enumerate(monthly_data):
        for data in month_data:
            supplier = data['supplier']
            items = data['items']
            response_score = data['response_score']
            reliability_score = data['reliability_score']
            issue_resolution_score = data['issue_resolution_score']

            on_time_scores = []
            capacity_scores = []
            handling_scores = []
            defects_scores = []
            pricing_scores = []
            in_full_scores = []

            for item in items:
                on_time_score = calculate_on_time_score(item['required_qty'], [(date, qty) for date, qty, _, _, _, _ in item['deliveries']], item['expected_date'])
                on_time_scores.append(on_time_score)
                capacity_score = calculate_capacity_score(supplier, month + 1, item['name'], item['required_qty'])
                capacity_scores.append(capacity_score)
                handling_score = calculate_handling_score(item['deliveries'])
                handling_scores.append(handling_score)
                defects_score = calculate_supplier_defects_score(item['deliveries'])
                defects_scores.append(defects_score)
                pricing_scores.append(item['pricing_score'])
                in_full_score = calculate_in_full_score(item['required_qty'], item['deliveries'])
                in_full_scores.append(in_full_score)

            avg_on_time_score = sum(on_time_scores) / len(on_time_scores) if on_time_scores else 0
            avg_capacity_score = sum(capacity_scores) / len(capacity_scores) if capacity_scores else 0
            avg_handling_score = sum(handling_scores) / len(handling_scores) if handling_scores else 0
            avg_defects_score = sum(defects_scores) / len(defects_scores) if defects_scores else 0
            avg_pricing_score = sum(pricing_scores) / len(pricing_scores) if pricing_scores else 0
            avg_in_full_score = sum(in_full_scores) / len(in_full_scores) if in_full_scores else 0

            supplier_scores[supplier].append({
                'month': month + 1,
                'on_time_score': avg_on_time_score,
                'capacity_score': avg_capacity_score,
                'handling_score': avg_handling_score,
                'defects_score': avg_defects_score,
                'response_score': response_score,
                'reliability_score': reliability_score,
                'pricing_score': avg_pricing_score,
                'in_full_score': avg_in_full_score,
                'issue_resolution_score': issue_resolution_score
            })
    
    for supplier, scores in supplier_scores.items():
        st.write(f"**Supplier: {supplier}**")
        df = pd.DataFrame(scores)
        df.rename(columns={
            'on_time_score': 'On-time Score',
            'handling_score': 'Quality - Handling (Transportation) Score',
            'defects_score': 'Quality - Supplier Defects Score',
            'issue_resolution_score': 'Issue Resolution Score',
            'reliability_score': 'Reliability Score',
            'in_full_score': 'In-Full Score'
        }, inplace=True)
        st.table(df[['month', 'On-time Score', 'capacity_score', 
                     'Quality - Handling (Transportation) Score', 
                     'Quality - Supplier Defects Score', 
                     'response_score', 'Reliability Score', 'In-Full Score', 'pricing_score', 'Issue Resolution Score']])
        
        avg_on_time_score = df['On-time Score'].mean()
        avg_capacity_score = df['capacity_score'].mean()
        avg_handling_score = df['Quality - Handling (Transportation) Score'].mean()
        avg_defects_score = df['Quality - Supplier Defects Score'].mean()
        avg_response_score = df['response_score'].mean()
        avg_reliability_score = df['Reliability Score'].mean()
        avg_in_full_score = df['In-Full Score'].mean()
        avg_pricing_score = df['pricing_score'].mean()
        avg_issue_resolution_score = df['Issue Resolution Score'].mean()

        total_weight = weight_on_time + weight_response + weight_reliability + weight_pricing + weight_capacity + weight_handling + weight_defects + weight_in_full + weight_issue_resolution
        final_weighted_avg_score = (
            (avg_on_time_score * weight_on_time) +
            (avg_capacity_score * weight_capacity) +
            (avg_handling_score * weight_handling) +
            (avg_defects_score * weight_defects) +
            (avg_response_score * weight_response) +
            (avg_reliability_score * weight_reliability) +
            (avg_in_full_score * weight_in_full) +
            (avg_pricing_score * weight_pricing) +
            (avg_issue_resolution_score * weight_issue_resolution)
        ) / total_weight

        st.write(f"**Average On-time Score: {round(avg_on_time_score, 2)}**")
        st.write(f"**Average Capacity Score: {round(avg_capacity_score, 2)}**")
        st.write(f"**Average Quality - Handling (Transportation) Score: {round(avg_handling_score, 2)}**")
        st.write(f"**Average Quality - Supplier Defects Score: {round(avg_defects_score, 2)}**")
        st.write(f"**Average Response Score: {round(avg_response_score, 2)}**")
        st.write(f"**Average Reliability Score: {round(avg_reliability_score, 2)}**")
        st.write(f"**Average In-Full Score: {round(avg_in_full_score, 2)}**")
        st.write(f"**Average Pricing Score: {round(avg_pricing_score, 2)}**")
        st.write(f"**Average Issue Resolution Score: {round(avg_issue_resolution_score, 2)}**")
        st.write(f"**Final Weighted Average Score: {round(final_weighted_avg_score, 2)}**")