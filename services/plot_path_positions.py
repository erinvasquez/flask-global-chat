import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine

# Database connection details
DB_NAME = "leveltimes"
DB_USER = "fresnousers"
DB_PASSWORD = "maze"
DB_HOST = "localhost"
DB_PORT = "5432"

# Connect to PostgreSQL database using SQLAlchemy
#conn = psycopg2.connect(f"dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} host={DB_HOST}")
engine = create_engine(f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

# Query to extract X, Z, and time
query = """
SELECT
    path_positions_item ->> 'x' AS x,
    path_positions_item ->> 'z' AS z,
    path_times_item AS time
FROM
    path_position_time_lists,
    jsonb_array_elements(path_positions) AS path_positions_item,
    jsonb_array_elements(path_times::jsonb) AS path_times_item
WHERE
    jsonb_array_length(path_positions) = jsonb_array_length(path_times::jsonb)
ORDER BY time;
"""
try:
    # Load data into dataframe
    df = pd.read_sql_query(query, engine)

    # Convert Data types and check for empty DataFrame
    df['x'] = pd.to_numeric(df['x'], errors='coerce') #df['x'].astype(float)
    df['z'] = pd.to_numeric(df['z'], errors='coerce') #df['z'].astype(float)
    df['time'] = pd.to_numeric(df['time'], errors='coerce') #df['time'].astype(float)

    # Check for empty dataframe
    if df.empty:
        print("The DataFrame is empty. No data to plot.")
    else:
        # Print DataFrame details
        print("Dataframe info:")
        print(df.info())
        print("\nFirst few rows of the DataFrame: ")
        print(df.head())
        print("/nDataFrame statistics:")
        print(df.describe())

        #print("\nData for plotting:")
        #print(df)

        # Plot the scatter plot
        plt.figure(figsize=(12, 6))
        plt.subplot(1, 2, 1)
        plt.scatter(df['x'], df['z'] ,c=df['time'], cmap='viridis', alpha=0.7)
        plt.colorbar(label='Time')
        plt.xlabel('X Coordinate')
        plt.ylabel('Z Coordinate')
        plt.title('Path Positions Over Time')

        # Plot the heatmap
        plt.subplot(1, 2, 2)
        heatmap_data = df.pivot_table(index='z', columns='x', values='time', aggfunc='mean')
        sns.heatmap(heatmap_data, cmap='viridis', cbar_kws={'label': 'Time'})
        plt.xlabel('X Coordinate')
        plt.ylabel('Z Coordinate')
        plt.title('Heatmap of Path Positions')

        # Save plot as an png
        plt.savefig('/home/erin_vasquez/flask-global-chat/static/path_positions_plot.png')

except Exception as e:
    print(f"An error occurred: {e}")
