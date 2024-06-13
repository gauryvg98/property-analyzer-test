# import matplotlib.pyplot as plt

# def visualize_data(db_file):
#     conn = sqlite3.connect(db_file)
#     df = pd.read_sql_query("SELECT * FROM properties WHERE price IS NOT NULL AND bedrooms IS NOT NULL", conn)
#     conn.close()

#     # Distribution of property prices
#     plt.figure(figsize=(10, 6))
#     plt.hist(df['price'], bins=50, color='blue', alpha=0.7)
#     plt.title('Distribution of Property Prices')
#     plt.xlabel('Price')
#     plt.ylabel('Frequency')
#     plt.grid(True)
#     plt.show()

#     # Distribution of properties by number of bedrooms
#     plt.figure(figsize=(10, 6))
#     df['bedrooms'].value_counts().sort_index().plot(kind='bar', color='green', alpha=0.7)
#     plt.title('Distribution of Properties by Number of Bedrooms')
#     plt.xlabel('Number of Bedrooms')
#     plt.ylabel('Frequency')
#     plt.grid(True)
#     plt.show()

#     #Distribution of properties by zipcode

# # Usage
# visualize_data('real_estate.db')
