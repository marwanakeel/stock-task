import json
import os
from flask import Flask, jsonify, request
import paho.mqtt.client as mqtt

app = Flask(__name__)

# Set up MQTT client
mqtt_client = mqtt.Client()
mqtt_client.connect(os.getenv("STREAMER_HOST"), int(os.getenv("STREAMER_PORT")), 60)
mqtt_client.subscribe("thndr-trading")

# Define stocks dictionary to hold stock data and analysis
# This can be database but for now let's keep it simple
stocks = {}

# Define function to handle incoming MQTT messages
def on_message(client, userdata, msg):
    data = json.loads(msg.payload)
    stock_id = data['stock_id']
    if stock_id not in stocks:
        stocks[stock_id] = {'name': data['name'], 'price': data['price'], 'availability': data['availability'], 'technical_analysis': None}
    else:
        stocks[stock_id]['price'] = data['price']
        stocks[stock_id]['availability'] = data['availability']
        if stocks[stock_id]['technical_analysis'] is not None:
            if stocks[stock_id]['technical_analysis']['type'] == 'UP' and data['price'] >= stocks[stock_id]['technical_analysis']['target']:
                stocks[stock_id]['technical_analysis']['target_hit'] = True
            elif stocks[stock_id]['technical_analysis']['type'] == 'DOWN' and data['price'] <= stocks[stock_id]['technical_analysis']['target']:
                stocks[stock_id]['technical_analysis']['target_hit'] = True

# Set up MQTT message handler
mqtt_client.on_message = on_message

# Define API endpoints
@app.route('/')
def default_page():
    return "Hello Thndr User"

@app.route('/stocks')
def get_stocks():
    stock_list = []
    for stock_id, stock_data in stocks.items():
        stock_list.append({'stock_id': stock_id, 'name': stock_data['name'], 'price': stock_data['price'], 'availability': stock_data['availability']})
    return jsonify(stock_list)

@app.route('/stocks/<stock_id>')
def get_stock(stock_id):
    if stock_id in stocks:
        return jsonify(stocks[stock_id])
    else:
        return jsonify({'error': 'Stock not found'}), 404

@app.route('/admin/stocks/<stock_id>/analysis', methods=['POST'])
def add_analysis(stock_id):
    if stock_id not in stocks:
        return jsonify({'error': 'Stock not found'}), 404
    target = request.json['target']
    analysis_type = request.json['type']
    stocks[stock_id]['technical_analysis'] = {'target': target, 'type': analysis_type, 'target_hit': False}
    return jsonify(stocks[stock_id]['technical_analysis'])

# Start MQTT client loop
mqtt_client.loop_start()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
