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
@app.route('/loads', methods=['GET'])
def get_load():
    reference_number = request.args.get('reference_number')
    filtered_row = df[df.iloc[:, 0] == f'REF{reference_number}']
    # Check if the reference_number exists in the data
    if not filtered_row.empty:
       # Convert the row to a dictionary (assuming a single match)
        load_details = filtered_row.iloc[0].to_dict()
        return jsonify(load_details)
    else:
        abort(404, description="Load not found") 



###If status_code == 400: the dot number is not in the correct format, it's either too long or malformed
###If the dot number exists, the content will not be none otherwise if the dot number format is valid but it doesn't exits, then it will return content: empty
###Make conditions for these cases and return accordingly.
@app.route('/verify_dot',methods = ['GET'])

def verify_dot():
    ### Have to take care of the case where both mc_number and dot_number are provided.
    dot_number = request.args.get('dot_number')
    mc_number = request.args.get('mc_number')

    if not dot_number and not mc_number:
        return "Please provide dot_number or mc_number"
    
    if not mc_number:
        fmsca_url = f"https://mobile.fmcsa.dot.gov/qc/services/carriers/{dot_number}?webKey={fmsca_apiKey}"
        try:
            response = requests.get(fmsca_url)
            
            if response.status_code == 200:
                data = response.json()
                print(data)
                if data['content'] == None:
                    return "Please tell the user that this dot_number does not exit."
                
                if data['content']['carrier']['allowedToOperate'] == 'Y':
                    formatted_data = {  "dot_number": dot_number,
                                        "carrier_name": data["content"]["carrier"]['legalName'],
                                        "allowed_to_operate": data['content']['carrier']['allowedToOperate'],
                                        "valid": True
                                    }
                    
                    return jsonify(formatted_data)
                
                if data['content']['carrier']['allowedToOperate'] == 'N':
                    return "It seems like you are not allowed to operate according to the mc_number provided."
            
            else:
                return "Please tell them the dot_number is not in the correct format. It's either malformed or too long."
            
        except requests.exceptions.RequestException as e:

            return "Exception"


    fmsca_url = f"https://mobile.fmcsa.dot.gov/qc/services/carriers/docket-number/{mc_number}?webKey={fmsca_apiKey}"
    try:
        response = requests.get(fmsca_url)
        
        if response.status_code == 200:
            data = response.json()

            if data['content'] == None:
                return "Please tell the user that this mc_number does not exit."
            
            if data['content'][0]['carrier']['allowedToOperate'] == 'Y':
                formatted_data = {  "dot_number": dot_number,
                                    "carrier_name": data["content"][0]["carrier"]['legalName'],
                                    "allowed_to_operate": data['content'][0]['carrier']['allowedToOperate'],
                                    "valid": True
                                }
                
                return jsonify(formatted_data)
            
            if data['content'][0]['carrier']['allowedToOperate'] == 'N':
                return "It seems like you are not allowed to operate according to the mc_number provided."

        
        else:
            return "Please tell them the mc_number is not in the correct format. It's either malformed or too long."
        
    except requests.exceptions.RequestException as e:

        return "Exception"


if __name__ == "__main__":
    app.run()
