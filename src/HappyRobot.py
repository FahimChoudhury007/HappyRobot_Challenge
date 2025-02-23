import requests
import json
from flask import Flask, jsonify, request, abort
from pathlib import Path
import pandas as pd


app = Flask(__name__)
fmsca_apiKey = "cdc33e44d693a3a58451898d4ec9df862c65b954"
flask_api_key = "aetgjd789njnjquij082nbjdn57sbjnk5"
script_dir = Path(__file__).parent
csv_file_path = script_dir.parent / "data" / "HappyRobot_Loadsdata.csv"
df = pd.read_csv(csv_file_path)

# API Endpoint to retrieve load details by reference_number
@app.route('/loads', methods=['GET'])
def get_load():
    api_key = request.headers.get("API-KEY")
    if api_key != flask_api_key:
        return jsonify({"error": "Unauthorized access"}), 403

    reference_number = request.args.get('reference_number')
    filtered_row = df[df.iloc[:, 0] == f'REF{reference_number}']
    if not filtered_row.empty:
        load_details = filtered_row.iloc[0].to_dict()
        return jsonify(load_details), 200
    else:
        abort(404, description="Load not found") 


##Proxy API to verify carrier details
@app.route('/verify_dot',methods = ['GET'])

def verify_dot():
    api_key = request.headers.get("API-KEY")

    if api_key != flask_api_key:
        return jsonify({"error": "Unauthorized access"}), 403
    
    dot_number = request.args.get('dot_number')
    mc_number = request.args.get('mc_number')

    if not dot_number and not mc_number:
        return jsonify({"error": "Please provide dot_number or mc_number"}), 400 

    
    if not mc_number:
        fmsca_url = f"https://mobile.fmcsa.dot.gov/qc/services/carriers/{dot_number}?webKey={fmsca_apiKey}"
        try:
            response = requests.get(fmsca_url)
            
            if response.status_code == 200:
                data = response.json()
                if data['content'] == None or data['content'] == []:
                    return jsonify({"error": "Please tell the user that this dot_number does not exist."}), 404
                
                if data['content']['carrier']['allowedToOperate'] == 'Y':
                    formatted_data = {  "dot_number": dot_number,
                                        "carrier_name": data["content"]["carrier"]['legalName'],
                                        "allowed_to_operate": data['content']['carrier']['allowedToOperate'],
                                        "valid": True
                                    }
                    
                    return jsonify(formatted_data), 200
                
                if data['content']['carrier']['allowedToOperate'] == 'N':
                    return jsonify({"Description": "It seems like you are not allowed to operate according to the dot_number provided."}), 403
                    # abort(403, description="It seems like you are not allowed to operate according to the mc_number provided.")

            
            else:
                abort(400, description="Please tell them the dot_number is not in the correct format. It's either malformed or too long.")

            
        except requests.exceptions.RequestException as e:
            return jsonify({"error": "An internal server error occurred."}), 500



    fmsca_url = f"https://mobile.fmcsa.dot.gov/qc/services/carriers/docket-number/{mc_number}?webKey={fmsca_apiKey}"
    try:
        response = requests.get(fmsca_url)
        
        if response.status_code == 200:
            data = response.json()

            if data['content'] == None or data['content'] == []:
                return jsonify({"Description":"Please tell the user that this mc_number does not exit."}), 404
                # return "Please tell the user that this mc_number does not exit."
            
            if data['content'][0]['carrier']['allowedToOperate'] == 'Y':
                formatted_data = {  "dot_number": dot_number,
                                    "carrier_name": data["content"][0]["carrier"]['legalName'],
                                    "allowed_to_operate": data['content'][0]['carrier']['allowedToOperate'],
                                    "valid": True
                                }
                
                return jsonify(formatted_data),200
            
            if data['content'][0]['carrier']['allowedToOperate'] == 'N':
                return jsonify({"Description": "It seems like you are not allowed to operate according to the mc_number provided."}), 403
                # return "It seems like you are not allowed to operate according to the mc_number provided."

        
        else:
            abort(400, description="Please tell them the mc_number is not in the correct format. It's either malformed or too long.")
            # return "Please tell them the mc_number is not in the correct format. It's either malformed or too long."
        
    except requests.exceptions.RequestException as e:    
        return jsonify({"error": "An internal servor error occurred"}), 500
        # return "Exception"


if __name__ == "__main__":
    app.run()
