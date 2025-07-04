from flask import Flask, request, jsonify, render_template, send_file
from dotenv import load_dotenv
load_dotenv()

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

app = Flask(__name__, static_folder='static')




@app.route('/')
def index():
    return render_template('index.html')




@app.route('/dashboard')
def dashboard():
    try:
        # TODO: update for GCP
        # Skip DB connection for now
        # conn = get_db_connection()
        # cursor = conn.cursor()
        # cursor.execute("SELECT id FROM movement_data")
        # ids = cursor.fetchall()
        
        # Fake data for now
        ids = [(1.), (2,), (3,)]

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
