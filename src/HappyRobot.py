import requests
import json
from flask import Flask, jsonify, request, abort


app = Flask(__name__)
fmsca_apiKey = "cdc33e44d693a3a58451898d4ec9df862c65b954"

def load_csv_data():
    with open('loads.csv', mode='r') as file:
        reader = csv.DictReader(file)
        loads = {row['reference_number']: row for row in reader}
    return loads

# API Endpoint to retrieve load details by reference_number
@app.route('/loads/<reference_number>', methods=['GET'])
def get_load(reference_number):
    loads = load_csv_data()
    
    # Check if the reference_number exists in the data
    load_details = loads.get(reference_number)
    
    if load_details:
        return jsonify(load_details)  # Return load details in JSON format
    else:
        abort(404, description="Load not found")  # Return 404 if not found

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
    app.run(debug=True)

###FMSCA API ENDPOINT

# fmsca_url = "https://mobile.fmcsa.dot.gov/qc/services/carriers/687592?webKey=cdc33e44d693a3a58451898d4ec9df862c65b954"


###

# r = requests.get(fmsca_url)
# # print(r.status_code)
# print(r.json())

### MC Number

# api_key = "cdc33e44d693a3a58451898d4ec9df862c65b954"
# mc_number = "687592"
# url = f'https://api.tms.fmcsa.dot.gov/v1/motor-carriers/{mc_number}'

# headers = {
#     'Authorization': f'Bearer {api_key}'
# }

# response = requests.get(url,headers=headers)

# print(response.status_code)