#!/usr/bin/env python3
"""
Script to create the seed Excel file for shipments data
"""
import pandas as pd
from datetime import datetime, timedelta

# Sample shipment data
data = {
    'title': [
        'Electronics Package',
        'Office Supplies',
        'Medical Equipment',
        'Furniture Delivery',
        'Books and Media',
        'Automotive Parts',
        'Clothing Shipment',
        'Food Products',
        'Industrial Materials',
        'Pharmaceuticals'
    ],
    'destination': [
        'New York, NY',
        'Los Angeles, CA',
        'Chicago, IL',
        'Miami, FL',
        'Seattle, WA',
        'Detroit, MI',
        'Atlanta, GA',
        'Denver, CO',
        'Houston, TX',
        'Boston, MA'
    ],
    'eta': [
        '2024-01-15',
        '2024-01-20',
        '2024-01-25',
        '2024-01-30',
        '2024-02-05',
        '2024-02-10',
        '2024-02-15',
        '2024-02-20',
        '2024-02-25',
        '2024-03-01'
    ],
    'status': [
        'pending',
        'agreed',
        'pending',
        'pending',
        'agreed',
        'pending',
        'agreed',
        'pending',
        'pending',
        'agreed'
    ]
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel file
df.to_excel('backend/data/seed_shipments.xlsx', index=False)
print("✅ Created backend/data/seed_shipments.xlsx with 10 sample shipments")
print("\nSample data:")
print(df.head())
