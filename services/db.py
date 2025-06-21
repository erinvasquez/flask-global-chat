# database




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

        # Check if data is properly received and parsed
        if not isinstance(data, dict):
            return jsonify({"error": "Invalid data format"}), 400

        # Extract the path_data and unique_code
        path_data = data.get('path_data')
        unique_code = data.get('uniqueCode')

        if not path_data or not unique_code:
            return jsonify({"error": "Missing 'path_data' or 'uniqueCode' in the request"}), 400

        # Insert the data into the database
        cursor.execute("INSERT INTO movement_data (path_data, unique_code) VALUES (%s, %s)",
                        (json.dumps(path_data),
                        unique_code))
        conn.commit()

        return jsonify({"message":"Movement data received and stored successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Close the database connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()




@app.route('/get_positiontimelist', methods=['GET'])
def get_positiontimelists():
    conn = None
    cursor = None

    try:
        # Connect to the PostgreSQL database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch all rows from the table
        cursor.execute("SELECT * FROM movement_data")
        rows = cursor.fetchall()

        #print("Fetched rows: ", rows);

        # Convert the rows to a list of dictionaries
        lists = []
        for row in rows:
            id = row[0]
            path_data = row[1]
            unique_code = row[2]
            created_at = row[3]

            if isinstance(created_at, datetime):
                created_at = created_at.isoformat()
            elif isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at).isoformat()
            else:
                created_at = None

            movement_data = {
               "path_data": path_data,
               "unique_code": unique_code,
               "created_at": created_at
            }
            lists.append(movement_data)

        return jsonify({"movement list data": lists}), 200

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

        cursor.execute("""
            SELECT path_data, unique_code, created_at
            FROM movement_data
            WHERE id = %s
        """, (id,))
        result = cursor.fetchone()

        if result:
            path_data, unique_code, created_at = result

            created_at_iso = created_at.isoformat() if created_at else None

            response = {
                'path_data': path_data,
                'unique_code': unique_code,
                'created_at': created_at_iso
            }

            return jsonify(response)
        else:
            return jsonify({'error': 'Entry not found'}), 404

    except Exception as e:
        app.logger.error(f"Error fetching movement data: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error'}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()




# Statistics
@app.route('/get_statistics', methods=['GET'])
def get_statistics():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT path_data FROM movement_data')
        rows = cursor.fetchall()

        x_positions = []
        z_positions = []

        for row in rows:
            path_data = row[0]  # This is already a JSON object
            positions = path_data.get('positions', [])
            for pos in positions:
                if isinstance(pos, dict) and 'x' in pos and 'z' in pos:
                    x_positions.append(pos['x'])
                    z_positions.append(pos['z'])

        # Calculate statistics
        def calc_stats(positions):
            if not positions:
                return {'min': None, 'max': None, 'avg': None}
            return {
                'min': min(positions),
                'max': max(positions),
                'avg': sum(positions) / len(positions)
            }

        x_stats = calc_stats(x_positions)
        z_stats = calc_stats(z_positions)

        return jsonify({'x_stats': x_stats, 'z_stats': z_stats})
    except Exception as e:
        logging.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
