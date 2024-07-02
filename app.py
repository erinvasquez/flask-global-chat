from flask import Flask, request, jsonify, render_template
import psycopg2
import logging

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


@app.route('/submit', methods=['POST'])
def submit():
    app.logger.info('New submission received')
    conn = None
    cursor = None
    try:
        # Connect to the PostgreSQL database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Extract data from the form data
        timestamp = request.form['timestamp']
        level_number = request.form['levelNumber']

        # Insert the data into the database
        cursor.execute("INSERT INTO submissions (timestamp, level_number) VALUES (%s, %s)", (timestamp, level_number))
        conn.commit()

        return jsonify({"message": "Submission successful"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Close the database connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/receive_data', methods=['POST'])
def receive_data():
    conn = None
    cursor = None
    try:
        # Connect to the PostgreSQL database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Extract data from the JSON payload
        data = request.get_json()
        message = data.get('message')

        # Insert the data into the database
        cursor.execute("INSERT INTO unity_data (data_column) VALUES (%s)", (message,))
        conn.commit()

        return jsonify({"message": "Data received successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Close the database connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/get_submissions', methods=['GET'])
def get_submissions():
    conn = None
    cursor = None
    try:
        # Connect to the PostgreSQL database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch all rows from the submissions table
        cursor.execute("SELECT * FROM submissions")
        rows = cursor.fetchall()

        # Convert the rows to a list of dictionaries
        submissions = []
        for row in rows:
            submission = {
                "id": row[0],
                "timestamp": row[1],
                "level_number": row[2]
            }
            submissions.append(submission)

        return jsonify({"submissions": submissions}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Close the database connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()



@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    fullchain_path = '/etc/letsencrypt/live/silenttableshow.com/fullchain.pem'
    privkey_path = '/etc/letsencrypt/live/silenttableshow.com/privkey.pem'

    #app.run(host='0.0.0.0', port=8080, ssl_context=(fullchain_path, privkey_path), debug=False)
    #app.run(host='0.0.0.0', port=8080, debug=False)
    app.run()
