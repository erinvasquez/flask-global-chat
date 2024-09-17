from flask import Flask, request, jsonify, render_template, send_file
import psycopg2
import logging
import json
import traceback
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from io import BytesIO
import os
import random

app = Flask(__name__)

# PostgreSQL connection configuration
DB_NAME = 'leveltimes'
DB_USER = 'fresnousers'
DB_PASSWORD = 'maze'
DB_HOST = 'localhost'
DB_PORT = '5432'

def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

# Setting up logging
#logging.basicConfig(filename='/home/erin_vasquez/flask-global-chat/logs/app.log', level=logging.DEBUG)
handler = logging.FileHandler('logs/app.log')
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)

# Path Position Time List endpoints
@app.route('/receive_positiontimelist', methods=['POST'])
def receive_positiontimelist():
    conn = None
    cursor = None

    try:
        # Connect to the PostgreSQL database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Extract data from the JSON payload
        data = request.get_json()
        #positions = data.get('simplePositions')
        #times = data.get('times')
        path_data = data.get('path_data')
        unique_code = data.get('uniqueCode')

        # Log data
        print(f"Received path data: unique_code={unique_code}")

        # Insert the data into the database
        cursor.execute("INSERT INTO path_position_time_lists (path_positions, path_times, unique_code) VALUES (%s, %s, %s)",
                        (json.dumps([item['position'] for item in path_data]),
                        json.dumps([item['time'] for item in path_data]),
                        unique_code))
        conn.commit()

        return jsonify({"message":"Path data received and stored successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Close the database connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/get_positiontimelist', methods=['GET'])
def get_path_position_time_lists():
    conn = None
    cursor = None

    try:
        # Connect to the PostgreSQL database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch all rows from the table
        cursor.execute("SELECT * FROM path_position_time_lists")
        rows = cursor.fetchall()

        # Print raw data for debugging
        #print("Raw rows from database:", rows)

        # Convert the rows to a list of dictionaries
        lists = []
        for row in rows:
            #path_pos_time_list = {
            #    "id": row[0],
            #    "path_positions": row[1],
            #    "path_times": row[2],
            #    "created_at": row[3].isoformat() # Convert tiemstamp to ISO format string
            #}
            path_data = json.loads(row[1]) # Deserialize path_positions
            path_times = json.loads(row[2]) # Deserialize path_times

            # Combine positions and times into path_data
            combined_data = [{'position': pos, 'time': time} for pos, time in zip(path_data, path_times)]
            path_pos_time_list = {
               "id": row[0],
               "path_data": combined_data,
               "created_at": row[3].isoformat()
            }
            lists.append(path_pos_time_list)


        return jsonify({"path_position_time_lists": lists}), 200

    except Exception as e:
        error_message = f"Error: {str(e)}\n{traceback.format_exc()}"
        print(error_message) # Log errors to the console
        return jsonify({"error": str(e)}), 500

    finally:
        # Close the database connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/get_positiontimelist/<int:id>', methods=['GET'])
def get_positiontimelist(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Query to extract the enitre entry for the specific ID
        query = """
        SELECT id, path_positions, path_times
        FROM path_position_time_lists
        WHERE id = %s
        """

        # Execute query
        cursor.execute(query, (id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            #response = {
            #    'id': result[0],
            #    'path_positions': result[1],
            #    'path_times': result[2]
            #}

            path_data = json.loads(result[1])
            path_times = json.loads(result[2])

            combined_data = [{'position': pos, 'time': time} for pos, time in zip(path_data, path_times)]

            response = {
                'id': result[0],
                'path_data': combined_data
            }
            return jsonify(response)
        else:
            return jsonify({'error': 'Entry not found'}), 404
    except Exception as e:
        logging.error(f"Error fetching path position time list: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/plot_xz_movement', methods=['POST'])
def plot_xz_movement():
    id = request.form['id']
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        SELECT path_positions, path_times
        FROM path_position_time_lists
        WHERE id = %s
        """

        cursor.execute(query, (id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            path_positions = result[0]
            path_times = result[1]

            # Verify data type and structure
            if not isinstance(path_positions, list) or not all(isinstance(pos, dict) and 'x' in pos and 'z' in pos for pos in path_positions):
                return jsonify({'error': 'Invalid format for path_positions'}), 500

            # Extract x, z positions
            x_positions = [pos['x'] for pos in path_positions]
            z_positions = [pos['z'] for pos in path_positions]

            # Create the XZ plot
            plt.figure(figsize=(10, 6))
            plt.plot(x_positions, z_positions, marker='o', linestyle='-', color='b')
            plt.xlabel('X Position')
            plt.ylabel('Z Position')
            plt.title(f'Top-Down View of Movement for ID {id}')
            plt.grid(True)
            plt.xlim(-80, 80)
            plt.ylim(-20, 180)

            # Ensure the directory exists
            plot_directory = os.path.join('static', 'plots')
            if not os.path.exists(plot_directory):
                os.makedirs(plot_directory)

            # Save the XZ plot
            image_filename = f'plots/plot_{id}.png'
            image_path = os.path.join('static', image_filename)
            plt.savefig(image_path)
            plt.close()

            # Generate heatmap of all entries
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT path_positions FROM path_position_time_lists")
            all_path_positions = cursor.fetchall()
            cursor.close()
            conn.close()

            # Flatten and prepare data for heatmap
            all_x_positions = []
            all_z_positions = []
            for positions in all_path_positions:
                path_positions = positions[0]
                if isinstance(path_positions, list):
                    all_x_positions.extend(pos['x'] for pos in path_positions if 'x' in pos)
                    all_z_positions.extend(pos['z'] for pos in path_positions if 'z' in pos)

            # Create heatmap plot
            plt.figure(figsize=(10, 6))
            plt.hist2d(all_x_positions, all_z_positions, bins=30, cmap='hot', range=[[-80, 80], [-20, 180]])
            plt.colorbar(label='Frequency')
            plt.xlabel('X Position')
            plt.ylabel('Z Position')
            plt.title('Heatmap of All Entries')
            plt.xlim(-80, 80)
            plt.ylim(-20, 180)

            # Save the heatmap plot
            heatmap_filename = 'plots/heatmap.png'
            heatmap_path = os.path.join('static', heatmap_filename)
            plt.savefig(heatmap_path)
            plt.close()

            # Fetch all IDs for the dropdown
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM path_position_time_lists")
            ids = cursor.fetchall()
            cursor.close()
            conn.close()

            return render_template('plot_xz_movement.html', ids=[id[0] for id in ids], image=image_filename, heatmap=heatmap_filename, selected_id=id)

        else:
            return jsonify({'error': 'Entry not found'}), 404

    except Exception as e:
        logging.error(f"Error plotting XZ movement: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/plot_xz_movement', methods=['GET'])
def plot_xz_movement_ui():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM path_position_time_lists")
        ids = cursor.fetchall()
        cursor.close()
        conn.close()

        if not ids:
            logging.error("No IDs found in the database")
        else:
            logging.info(f"IDs found: {[id[0] for id in ids]}")

        return render_template('plot_xz_movement.html', ids=[id[0] for id in ids])

    except Exception as e:
        logging.error(f"Error loading plot XZ movement UI: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error'}), 500




# Leaderboard endpoints
@app.route('/submit_score', methods=['POST'])
def submit_score():
    try:
        data = request.json
        player_name = data['player_name']
        completion_time = data['completion_time']
        unique_code = data.get('unique_code')

        # Log data
        print(f"Received leaderboard data: unique_code={unique_code}")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO leaderboard (player_name, completion_time, unique_code) VALUES (%s, %s, %s)',
            (player_name, completion_time, unique_code)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Score submitted successfully", "unique_code": unique_code}), 201
    except Exception as e:
        logging.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT player_name, completion_time FROM leaderboard ORDER by completion_time ASC limit 10'
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        leaderboard = [{"player_name": row[0], "completion_time": row[1]} for row in rows]

        return jsonify(leaderboard)
    except Exception as e:
        logging.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

# Unique code generation
adjectives = ["Brave", "Recusant", "Vigilant", "Swift", "Bold"]
nouns = ["Panda", "Eagle", "Tiger", "Wolf", "Hawk"]

@app.route('/generate_unique_code', methods=['GET'])
def generate_unique_code_endpoint():
    try:
        unique_code = generate_and_verify_unique_code('leaderboard')
        return jsonify({"unique_code": unique_code}), 200
    except Exception as e:
        logging.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

def generate_unique_code():
    adjective = random.choice(adjectives)
    noun = random.choice(nouns)
    number = random.randint(100, 999)
    return f"{adjective}{noun}{number}"

def is_code_unique(code, table):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = f"SELECT COUNT(*) FROM {table} WHERE unique_code = %s"
    cursor.execute(query, (code,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0] == 0

def generate_and_verify_unique_code(table):
    code = generate_unique_code()
    while not is_code_unique(code, table):
        code = generate_unique_code()
    return code


# Statistics

@app.route('/get_statistics', methods=['GET'])
def get_statistics():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Query to get all X and Z positions
        cursor.execute('''
            SELECT path_positions
            FROM path_position_time_lists
        ''')
        rows = cursor.fetchall()

        x_positions = []
        z_positions = []

        # Extract X and Z positions from the path_positions
        for row in rows:
            positions = row[0]  # Assuming path_positions is stored as a list in the DB
            for pos in positions:
                x_positions.append(pos['x'])
                z_positions.append(pos['z'])

        # Calculate statistics
        x_stats = {
            'min': min(x_positions),
            'max': max(x_positions),
            'avg': sum(x_positions) / len(x_positions) if x_positions else 0
        }

        z_stats = {
            'min': min(z_positions),
            'max': max(z_positions),
            'avg': sum(z_positions) / len(z_positions) if z_positions else 0
        }

        return jsonify({'x_stats': x_stats, 'z_stats': z_stats})
    except Exception as e:
        logging.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM path_position_time_lists")
        ids = cursor.fetchall()
        cursor.close()
        conn.close()

        if not ids:
            app.logger.error("No IDs found in the database")
            ids = []

        # Include the selected_id in the context if available
        selected_id = request.args.get('id', default='', type=str)

        return render_template('dashboard.html', ids=[id[0] for id in ids], selected_id=selected_id)

    except Exception as e:
        app.logger.error(f"Error loading dashboard: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    fullchain_path = '/etc/letsencrypt/live/silenttableshow.com/fullchain.pem'
    privkey_path = '/etc/letsencrypt/live/silenttableshow.com/privkey.pem'
    app.run()
