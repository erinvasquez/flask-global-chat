# Routes for interacting with database
# GET/POST for movement and leaderboard



# Flask blueprint
from flask import Blueprint, jsonify
db_bp = Blueprint('db', __name__)



# Leaderboard endpoints
@db_bp.route('/submit_score', methods=['POST'])
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




@db_bp.route('/leaderboard', methods=['GET'])
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
