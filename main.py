import eventlet
from flask import Flask, render_template
from flask_mqtt import Mqtt
from flask_socketio import SocketIO
from werkzeug.serving import run_simple
from werkzeug.middleware.proxy_fix import ProxyFix

eventlet.monkey_patch()

app = Flask(__name__, template_folder='./templates')
app.config['MQTT_BROKER_URL'] = 'test.mosquitto.org'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_REFRESH_TIME'] = 1.0
app.secret_key = '4ce2134367cf4025b6dfb7f7fa5315dd'

mqtt = Mqtt(app)
socketio = SocketIO(app)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe('#')

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    print('received args: ' + message.topic)
    data = dict(
        topic=message.topic
    # payload = message.payload.decode()
    )
    # emit a mqtt_message event to the socket containing the message data
    socketio.emit('mqtt_message', data=data)

@app.route('/')
def index():
    return render_template('graph.html')

@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    print(level, buf)

# socketio.run(app, host='localhost', port=5000, use_reloader=True, debug=True)
if __name__ == '__main__':
    # important: Do not use reloader because this will create two Flask instances.
    # Flask-MQTT only supports running with one instance
    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=False, debug=True)
# if __name__ == '__main__':
#     run_simple('localhost', 5000, socketio,
#                use_reloader=False, use_debugger=True, use_evalex=True)