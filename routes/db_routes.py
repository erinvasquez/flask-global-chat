# Routes for interacting with database
# GET/POST for movement and leaderboard




@app.route('/plot_xz_movement', methods=['POST'])
def plot_xz_movement():
    id = request.form['id']

    if not id:
        return jsonify({'error': 'ID not provided'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT path_data
            FROM movement_data
            WHERE id = %s
        """, (id,))
        result = cursor.fetchone()

        if result:
            path_data = result[0]  # This is already a JSON object
            positions = path_data.get('positions', [])

            # Verify data structure
            if not isinstance(positions, list) or not all(isinstance(pos, dict) and 'x' in pos and 'z' in pos for pos in positions):
                return jsonify({'error': 'Invalid format for positions in path_data'}), 500

            # Extract x, z positions
            x_positions = [pos['x'] for pos in positions]
            z_positions = [pos['z'] for pos in positions]

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

            # Update heatmap generation
            cursor.execute("SELECT path_data FROM movement_data")
            all_path_data = cursor.fetchall()

            # Flatten and prepare data for heatmap
            all_x_positions = []
            all_z_positions = []
            for data in all_path_data:
                path_data = data[0]  # This is already a JSON object
                positions = path_data.get('positions', [])
                if isinstance(positions, list):
                    all_x_positions.extend(pos['x'] for pos in positions if 'x' in pos)
                    all_z_positions.extend(pos['z'] for pos in positions if 'z' in pos)

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
            cursor.execute("SELECT id FROM movement_data")
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
        cursor.execute("SELECT id FROM movement_data")
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
