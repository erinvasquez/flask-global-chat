from flask import Flask, request, jsonify, render_template
import psycopg2

app = Flask(__name__)

# PostgreSQL connection configuration
DB_NAME = 'leveltimes'
DB_USER = 'fresnousers'
DB_PASSWORD = 'maze'
DB_HOST = 'localhost'
DB_PORT = '5432'

@app.route('/submit', methods=['POST'])
def submit():
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
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
        cursor.close()
        conn.close()

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
