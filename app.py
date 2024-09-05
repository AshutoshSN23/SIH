from flask import Flask, request, jsonify,render_template
import pandas as pd
import numpy as np
import requests

app = Flask(__name__)

# Function to reverse the address
def get_lat_lng(address, api_key):
    url = 'https://api.opencagedata.com/geocode/v1/json'
    params = {
        'q': address,
        'key': api_key
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            lat_lng = data['results'][0]['geometry']
            return lat_lng['lat'], lat_lng['lng']
        else:
            return None, None
    else:
        print(f"Error: {response.status_code}")
        return None, None


api_key = '909c37d5fcb1424290a6f93a4137c216'  


def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians 
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r

def find_nearby_locations(df, target_lat, target_lon, threshold_km):
    """
    Returns nearby locations within a certain threshold (in km) from the target latitude and longitude.

    Parameters:
    df (DataFrame): DataFrame containing 'Latitude' and 'Longitude' columns.
    target_lat (float): Target latitude.
    target_lon (float): Target longitude.
    threshold_km (float): Distance threshold in kilometers.

    Returns:
    DataFrame: A DataFrame with rows within the specified distance from the target location.
    """
    distances = df.apply(lambda row: haversine(target_lat, target_lon, row['Latitude'], row['Longitude']), axis=1)
    
    # Filter DataFrame for locations within the specified threshold distance
    nearby_df = df[distances <= threshold_km].copy()
    
    # Add a column to show the calculated distances
    nearby_df['Distance_km'] = distances[distances <= threshold_km]
    
    return nearby_df


ALL_2024 = pd.read_csv("2024_Aug.csv", encoding='unicode_escape')
ALL_2024['Latitude'] = pd.to_numeric(ALL_2024['Latitude'], errors='coerce')
ALL_2024['Longitude'] = pd.to_numeric(ALL_2024['Longitude'], errors='coerce')
VALID_2024 = ALL_2024[((ALL_2024['Latitude'].between(-90, 90)) & (ALL_2024['Longitude'].between(-180, 180)))] 

 # 
# def form():

#     if request.method=="GET":
#         return render_template('form.html')
#     else:
#         place = request.form["place"]

#         address = place        
#         # Reverse the address
#         reversed_address = place

#         lat, lng = get_lat_lng(reversed_address, api_key)
#         tol = 1
#         if lat and lng:
#             nearby_hubs = find_nearby_locations(VALID_2024, lat, lng, tol).sort_values(by="Distance_km").head(10) # Default threshold 10km
#             if not nearby_hubs.empty:
#                 return render_template('form.html', res=f"For {place} pin code {nearby_hubs.iloc[0]['Pincode']}, lat: {lat}, lng: {lng}")
#             else:
#                 return render_template('form.html', res=f"Error: No nearby hubs found. Lat: {lat}, Lng: {lng}")
#         else:
#             return render_template('form.html', res="Address not found")

@app.route('/', methods=['GET', 'POST'])
def form():
    if request.method == "GET":
        return render_template('form.html')
    else:
        place = request.form["place"]

        address = place        
        # Reverse the address
        reversed_address = place

        lat, lng = get_lat_lng(reversed_address, api_key)
        tol = 1
        if lat and lng:
            nearby_hubs = find_nearby_locations(VALID_2024, lat, lng, tol).sort_values(by="Distance_km").head(10)  # Default threshold 10km
            if not nearby_hubs.empty:
                # Extract only the first row
                first_hub = nearby_hubs.iloc[0]
                result = {
                    'OfficeName': first_hub['OfficeName'],
                    'Pincode': first_hub['Pincode'],
                    'Distance_km': first_hub['Distance_km']
                }
                return render_template('form.html', result=result, place=place)
            else:
                return render_template('form.html', res=f"Error: No nearby hubs found. Lat: {lat}, Lng: {lng}", place=place)
        else:
            return render_template('form.html', res="Address not found", place=place)

        

if __name__ == '__main__':
    app.run(debug=True)
