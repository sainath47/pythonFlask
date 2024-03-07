from datetime import datetime

# Assuming user_id is known
user_id = 'your_user_id_here'

# Query to find the latest end date for the user
latest_end_date_query = "SELECT MAX(end_date) AS latest_end_date FROM subscriptions WHERE user_id = %s"
cursor.execute(latest_end_date_query, (user_id,))
latest_end_date_result = cursor.fetchone()
latest_end_date = latest_end_date_result['latest_end_date']

if latest_end_date:
    # If there is a latest end date, use it as the registration date
    registration_date = latest_end_date
else:
    # If no end date is found, use the created_at timestamp as the registration date
    registration_date_query = "SELECT created_at FROM user_details WHERE user_id = %s"
    cursor.execute(registration_date_query, (user_id,))
    registration_date_result = cursor.fetchone()
    registration_date = registration_date_result['created_at'] if registration_date_result else None

# Convert registration_date to a formatted string if needed
registration_date_str = registration_date.strftime('%Y-%m-%d %H:%M:%S') if registration_date else None

# Use registration_date_str as needed in your application
print("Registration Date:", registration_date_str)
