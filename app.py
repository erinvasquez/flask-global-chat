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
import datetime
from datetime import datetime
import requests
import subprocess

from routes.get_db_connection import get_db_connection, register_routes


app = Flask(__name__, static_folder='static')
register_routes(app)





@app.route('/')
def index():
    return render_template('index.html')




@app.route('/dashboard')
def dashboard():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM movement_data")
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




# Cloud Run health check route
@app.route('/healthz')
def health_check():
    return 'OK', 200

if __name__ == '__main__':
    app.run()



@app.route('/test-db')
def test_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        cursor.close()
        conn.close()
        return "Database connection successful!", 200
    except Exception as e:
        return f"Database connection failed: {e}", 500