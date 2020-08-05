from flask import Flask, request, render_template, jsonify
import pandas as pd
import numpy as np
from flask_mysqldb import MySQL
#from flask_wtf import FlaskForm
#from wtforms import SelectField
import os



app = Flask(__name__)

app.config['MYSQL_HOST'] = 'nw-poc-cps1.vmware.com'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Suman.524532'
app.config['MYSQL_DB'] = 'cps_db'

mysql = MySQL(app)

#SECRET_KEY = os.urandom(32)
#app.config['SECRET_KEY'] = SECRET_KEY

std_data = pd.read_csv("data/Network Hardware Standards.csv")
#std_data = std_data.reindex(sorted(std_data.DeviceType), axis=1)
#std_data = std_data[sorted(std_data.DeviceType)]
model_price = pd.read_csv("data/Device Model Price.csv")

sum_data = pd.merge(std_data, model_price, on ="DeviceModel", how="left")
sum_data['DeviceModel'] = sum_data['DeviceModel'].replace(np.nan, 'NONE')
#sum_data.to_csv("sum_data.csv")


#class Form(FlaskForm):
#   locations = SelectField('Locations')

@app.route('/')
def main_page():
    return render_template("main.html")

@app.route('/existing')
def existing():

    device_type = {}
    device_model = {}
    conn = mysql.connect
    '''
    query_country = "select distinct(site_name)  from site_details "
    result_country = pd.read_sql(query_country, conn)



    data = result_country['site_name'].unique().tolist()
    data = list(filter(None, data))
    data.sort()
    data.insert(0, 'Select Locations')
    form = Form()
    form.locations.choices = [(i, i) for i in data]
    '''
    service_list = sum_data['ServiceType'].unique().tolist()
    for service in service_list:
        device_type[service] = sum_data.loc[sum_data['ServiceType'] == service,'DeviceType'].unique().tolist()
        device_type[service] = sorted(device_type[service])

    device_list = sum_data['DeviceType'].unique().tolist()
    for device in device_list:
        device_model[device] = sum_data.loc[sum_data['DeviceType'] == device, 'DeviceModel'].unique().tolist()

    model_price_1 = pd.read_csv("data/Device Model Price.csv")
    model_price = model_price_1.to_json(orient='records')


    query = "select distinct(country),region  from site_details "\
            "join circuit_details on circuit_details.location=site_details.site_name " \
            "order by country"

    result = pd.read_sql(query, conn)

    country_list = result.to_json(orient='records')
    query_country = "select distinct(site_name),country  from site_details "
    result_country = pd.read_sql(query_country, conn)

    location_list = result_country.to_json(orient='records')

    #****Extract device details************
    query_device = "select * from hw_device_details"
    result_device = pd.read_sql(query_device, conn)
    LAN_WLAN = ['WIRELESS CNTRL', 'CE ROUTER', 'CORE SWITCH', 'DMZ SWITCH', 'ACCESS SWITCH', 'OFFICE SWITCH',
                  'VOICE SWITCH', 'WIRELESS SWITCH', 'LAB SWITCH', 'MANAGEMENT SWITCH']

    def check_service(result_device):
        if result_device['service_unit'] in LAN_WLAN:
            return "LAN-WLAN"
        else:
            return "None"
    result_device['service_type'] = result_device.apply(check_service, axis=1)

    device_list = result_device
    #print(device_list)

    conn.close()
    #print(location_list)
    gss_list= ['CORK BEHAN HOUSE','CORK YEATS HOUSE','BROOMFIELD','Bangalore PS'
        ,'BANGALORE KM','BANGALORE KV' ,'BANGALORE CNX','Costa Rica','Tokyo',
        'Shanghai R&D','Guangzhou','Beijing R&D','Sydney','Melbourne','Singapore Suntec']
    #print(device_type)

    service_list_checkbox = ['LAN-WLAN','WAN','DC-Ops','Firewall']
    return render_template("existing.html", service_list=service_list, device_type=device_type,
                           device_model=device_model,model_price=model_price,
                           country_list=country_list, location_list = location_list,
                           gss_list = gss_list, device_list=device_list, service_list_checkbox = service_list_checkbox)


@app.route('/new')
def new():
    device_category = {}
    device_type = {}
    device_model = {}
    service_list = sum_data['ServiceType'].unique().tolist()
    service_category_list = sum_data['ServiceCategory'].unique().tolist()
    for category in service_category_list:
        device_category[category] = sum_data.loc[sum_data['ServiceCategory'] == category, 'ServiceType'].unique().tolist()
    for service in service_list:
        device_type[service] = sum_data.loc[sum_data['ServiceType'] == service,'DeviceType'].unique().tolist()
        device_type[service] = sorted(device_type[service])

    device_list = sum_data['DeviceType'].unique().tolist()
    for device in device_list:
        device_model[device] = sum_data.loc[sum_data['DeviceType'] == device, 'DeviceModel'].unique().tolist()


    model_price_1 = pd.read_csv("data/Device Model Price.csv")
    model_price = model_price_1.to_json(orient='records')

    conn = mysql.connect
    query = "select distinct(country),region  from site_details "\
            "join circuit_details on circuit_details.location=site_details.site_name " \
            "order by country"

    result = pd.read_sql(query, conn)

    country_list = result.to_json(orient='records')
    query_country = "select distinct(site_name),country  from site_details "
    result_country= pd.read_sql(query_country, conn)

    location_list = result_country.to_json(orient='records')
    conn.close()
    #print(location_list)
    gss_list= ['CORK BEHAN HOUSE','CORK YEATS HOUSE','BROOMFIELD','Bangalore PS'
        ,'BANGALORE KM','BANGALORE KV' ,'BANGALORE CNX','Costa Rica','Tokyo',
        'Shanghai R&D','Guangzhou','Beijing R&D','Sydney','Melbourne','Singapore Suntec']


    return render_template("new.html", service_list=service_list, device_type=device_type,
                           service_category_list = service_category_list,device_category=device_category,
                           device_model=device_model,model_price=model_price,
                           country_list=country_list, location_list = location_list, gss_list = gss_list)


def getSiteSpecifics(headcount):
    site_specs = dict()
    site_specs['mpls_count'] = 0
    site_specs['internet_count'] = 2
    if headcount < 50:
        site_specs['tier'] = "2B"
        site_specs['mpls_count'] = 0
        site_specs['mpls_bw'] = 0
        site_specs['internet_bw'] = 100
    elif 50 <= headcount < 100:
        site_specs['tier'] = "2A"
        site_specs['mpls_count'] = 1
        site_specs['mpls_bw'] = 50
        site_specs['internet_bw'] = 100
    elif 100 <= headcount < 250:
        site_specs['tier'] = "1C"
        site_specs['mpls_count'] = 2
        site_specs['mpls_bw'] = 100
        site_specs['internet_bw'] = 500
    elif 250 <= headcount < 500:
        site_specs['tier'] = "1B"
        site_specs['mpls_count'] = 2
        site_specs['mpls_bw'] = 200
        site_specs['internet_bw'] = 500
    elif headcount >= 500:
        site_specs['tier'] = "1A"
        site_specs['mpls_count'] = 2
        site_specs['mpls_bw'] = 500
        site_specs['internet_bw'] = 1000
    return site_specs


def ciruitDetails(country, site_specs):
    circuit_cost = dict()

    cur = mysql.connection.cursor()
    mpls_query = "select country,circuit_type,max(circuit_details.`$/Mbit`) as max_per_meg, "\
                 "sum(mrc_usd)/sum(bandwidth_mb) as avg_per_meg from site_details " \
                 "join circuit_details on circuit_details.location=site_details.site_name " \
                 "where site_details.country = '" + country + "' and tier in ('1A','1B','1C','2A','2B') "\
                                                              "and circuit_type='MPLS'"

    cur.execute(mpls_query)
    mpls_result = cur.fetchall()
    if mpls_result[0][0] is None:
        circuit_cost["mpls_max"] = 0
        circuit_cost["mpls_avg"] = 0
    else:
        circuit_cost["mpls_max"] = float(mpls_result[0][2])
        circuit_cost["mpls_avg"] = float(mpls_result[0][3])

    circuit_cost['mpls_cost_max'] = circuit_cost["mpls_max"] * site_specs['mpls_bw']
    circuit_cost['mpls_cost_avg'] = circuit_cost["mpls_avg"] * site_specs['mpls_bw']

    int_query = "select country,circuit_type,max(circuit_details.`$/Mbit`) as max_per_meg, " \
                "sum(mrc_usd)/sum(bandwidth_mb) as avg_per_meg from site_details " \
                "join circuit_details on circuit_details.location=site_details.site_name " \
                "where site_details.country = '" + country + "' and tier in ('1A','1B','1C','2A','2B') " \
                                                             "and circuit_type='Internet'"

    cur.execute(int_query)

    int_result = cur.fetchall()
    if int_result[0][0] is None:
        circuit_cost["int_max"] = 0
        circuit_cost["int_avg"] = 0
    else:
        circuit_cost["int_max"] = float(int_result[0][2])
        circuit_cost["int_avg"] = float(int_result[0][3])

    circuit_cost['int_cost_max'] = circuit_cost["int_max"] * site_specs['internet_bw']
    circuit_cost['int_cost_avg'] = circuit_cost["int_avg"] * site_specs['internet_bw']

    cur.close()
    return circuit_cost


@app.route('/fetch')
def fetch():

    headcount = int(request.args.get("headcount"))
    country = request.args.get('country')

    site_specs = getSiteSpecifics(headcount)
    circuit_cost = ciruitDetails(country, site_specs)
    tier_val = "Tier "+ site_specs['tier']

    tier_data = sum_data.loc[sum_data['Tier'] == tier_val]
    tier_data = tier_data.sort_values(['ServiceType', 'DeviceType'])

    result = tier_data.to_json(orient='records')

    response = {'0': result, '1': site_specs, '2': circuit_cost}

    return jsonify(response)


@app.route('/fetch_device', methods = ['POST','GET'])
def fetch_device():

    headcount = int(request.get_json("headcount"))
    site_specs = getSiteSpecifics(headcount)
    service_list  = sum_data['ServiceType'].unique().tolist()
    response = {'0': site_specs, '1': service_list}

    return jsonify(response)


@app.route('/existing_details', methods = ['POST','GET'])
def existing_details():
    conn = mysql.connect
    dict_value = request.get_json('dict')
    checkbox_service = dict_value['key1']
    location = dict_value['key2']

    checked_service= checkbox_service.split(',')
    checked_service = checked_service[:-1]

    query_device = "select * from hw_device_details"
    result_device = pd.read_sql(query_device, conn)
    LAN_WLAN = ['WIRELESS CNTRL', 'CE ROUTER', 'CORE SWITCH', 'DMZ SWITCH', 'ACCESS SWITCH', 'OFFICE SWITCH',
                'VOICE SWITCH', 'WIRELESS SWITCH', 'LAB SWITCH', 'MANAGEMENT SWITCH']
    WAN = ['MPLS ROUTE REFLECTOR', 'INTERNET ROUTE REFLECTOR', 'INTERNET ROUTER', 'MPLS ROUTER', 'P2P ROUTER']
    Firewall = ['Firewall']

    def check_service(result_device):
        if result_device['service_unit'] in LAN_WLAN:
            return "LAN-WLAN"
        elif result_device['service_unit'] in WAN:
            return "WAN"
        elif result_device['service_unit'] in Firewall:
            return "Firewall"
        else:
            return "None"

    result_device['service_type'] = result_device.apply(check_service, axis=1)
    result_device = result_device[~result_device.device_name.str.contains("SUP")]

    device_list = result_device[(result_device['service_type'].isin(checked_service)) & (result_device['location'] == location)]
    result = device_list.to_json(orient='records')
    service_list_checkbox = ['LAN-WLAN', 'WAN', 'DC-Ops', 'Firewall']

    response = {'0': result, '1': checked_service, '2': service_list_checkbox}
    conn.close()

    return jsonify(response)


@app.route('/bom', methods = ['POST','GET'])
def bom():
    dict_value = request.get_json('dict_nest')
    #checkbox_service = dict_value['key1']

    output = pd.DataFrame()

    for i in dict_value:
        output = output.append([i], ignore_index=True)
    #df = pd.DataFrame(list(dict_value.items()), columns=['column1', 'column2'])
    print(output.dropna())

    return "true"


@app.route('/bom_html', methods = ['POST','GET'])
def bom_html():

    return  render_template('bom_html.html')


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)