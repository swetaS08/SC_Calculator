import sqlite3
from statistics import mean
from datetime import datetime
from flask import Flask, request, render_template
import  os
import pandas as pd
import numpy as np

app = Flask(__name__ , template_folder='templates')


std_data = pd.read_csv("data/Network Hardware Standards.csv")
model_price = pd.read_csv("data/Device Model Price.csv")

sum_data= pd.merge(std_data,model_price, on ="DeviceModel", how="left")
sum_data['DeviceModel'] = sum_data['DeviceModel'].replace(np.nan, 'NONE')


@app.route('/')
def home():
    device_type = {}
    device_model = {}
    service_list= sum_data['ServiceType'].unique().tolist()
    for service in service_list:
        device_type[service] = sum_data.loc[sum_data['ServiceType'] == service,'DeviceType'].unique().tolist()
    #print(device_type)
    device_list = sum_data['DeviceType'].unique().tolist()
    for device in device_list:
        device_model[device] = sum_data.loc[sum_data['DeviceType'] == device, 'DeviceModel'].unique().tolist()

    #print(device_model)
    model_price_1 = pd.read_csv("data/Device Model Price.csv")
    model_price = model_price_1.to_json(orient='records')

    return render_template("index.html", service_list= service_list, device_type=device_type, device_model= device_model, model_price = model_price)

@app.route('/fetch')
def fetch():
    link_count = {}
    H_C = int(request.args.get("headcount"))

    mpls_count = 0
    internet_count = 2
    if H_C < 50:
        Site_Tier ="Tier 2B"
        mpls_count = 0

    elif H_C >= 50 and H_C < 100:
        Site_Tier = "Tier 2A"
        mpls_count = 1

    elif H_C >= 100 and H_C < 250:
        Site_Tier = "Tier 1C"
        mpls_count = 2

    elif H_C >=250 and H_C < 500 :
        Site_Tier ="Tier 1B"
        mpls_count = 2

    elif H_C >= 500:
        Site_Tier = "Tier 1A"
        mpls_count = 2

    tier_data = sum_data.loc[std_data['Tier'] == Site_Tier]
    capex_value = sum(tier_data['CAPEX'].fillna(0))
    opex_value = sum(tier_data['OPEX'].fillna(0))

    link_count['mpls_count'] = mpls_count
    link_count['internet_count'] = internet_count
    link_count['tier'] =Site_Tier
    link_count['capex'] = capex_value
    link_count['opex'] = opex_value

    result = tier_data.to_json(orient='records')

    response = { '0': result, '1': link_count }
    return response





if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)