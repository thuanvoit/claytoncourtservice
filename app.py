from flask import Flask, jsonify
from helper import case_searcher

app = Flask(__name__)


@app.route('/api/cases/<case_type>/<case_number>', methods=['GET'])
def case_search(case_number, case_type):
    info = case_searcher(case_number, case_type)
    return jsonify(info)
