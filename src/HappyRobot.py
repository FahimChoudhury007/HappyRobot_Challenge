import requests
import json
from flask import Flask, jsonify, request, abort
from pathlib import Path
import pandas as pd


app = Flask(__name__)
fmsca_apiKey = "cdc33e44d693a3a58451898d4ec9df862c65b954"

script_dir = Path(__file__).parent
csv_file_path = script_dir.parent / "data" / "HappyRobot_Loadsdata.csv"
df = pd.read_csv(csv_file_path)

# API Endpoint to retrieve load details by reference_number
@app.route('/loads/<reference_number>', methods=['GET'])
def get_load(reference_number):
    filtered_row = df[df.iloc[:, 0] == reference_number]
    # Check if the reference_number exists in the data
    if not filtered_row.empty:
       # Convert the row to a dictionary (assuming a single match)
        load_details = filtered_row.iloc[0].to_dict()
        return jsonify(load_details)
    else:
        abort(404, description="Load not found") 

@app.route('/verify_dot',methods = ['GET'])

def verify_dot():
    
    dot_number = request.args.get('dot_number')

    if not dot_number:
        return "Please provide dot_number"
    
    fmsca_url_dotNumber = f"https://mobile.fmcsa.dot.gov/qc/services/carriers/{dot_number}?webKey={fmsca_apiKey}"

    try:
        response = requests.get(fmsca_url_dotNumber)
        
        if response.status_code == 200:
            data = response.json()

            print(data)
            if data and data['content']['carrier']['allowedToOperate'] == 'Y':
                
                return jsonify({"dot_number": dot_number, "valid": True}), 200

        
        else:
            
            return jsonify({"error": "Failed to verify DOT number"}), 500
        
    except requests.exceptions.RequestException as e:

        return "Exception"


if __name__ == "__main__":
    app.run()
