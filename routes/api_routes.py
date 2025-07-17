# routes/api_routes.py


# Flask blueprint
from flask import Blueprint, jsonify
api_bp = Blueprint('api', __name__)




# Unique code generation
adjectives = ["Brave", "Recusant", "Vigilant", "Swift", "Bold"]
nouns = ["Panda", "Eagle", "Tiger", "Wolf", "Hawk"]

@api_bp.route('/generate_unique_code', methods=['GET'])
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
