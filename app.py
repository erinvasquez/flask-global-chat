from flask import Flask, request, redirect, url_for, render_template

app = Flask(__name__)

# In-memory message board (for simplicity)
messages = []

@app.route('/')
def index():
    return render_template('index.html', messages=messages)

@app.route('/post_message', methods=['POST'])
def post_message():
    message = request.form['message']
    if message:
        messages.append(message)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)





