import argparse

from gpiozero import LineSensor

from flask import Flask
app = Flask(__name__)

from mtable import MeasurementTable

@app.route('/cfg')
def cfg():
    return app.args

@app.route('/state')
def state():
    return app.mtable.state()

@app.route('/stop')
def stop():
    app.mtable.stop()
    return app.mtable.state()

@app.route('/reset')
def reset():
    app.mtable.reset()
    return app.mtable.state()

@app.route('/rotate/<deg>', methods=['GET'])
def rotate(deg):
    deg = float(deg)
    app.mtable.rotate(deg)
    return app.mtable.state()
    
@app.route('/rotateto/<angle>', methods=['GET'])
def rotateto(angle):
    angle = float(angle)
    app.mtable.rotateto(angle)
    return app.mtable.state()

@app.route('/speed/<s>', methods=['GET'])
def speed(s):
    s = float(s)
    app.mtable.set_speed(s)
    return app.mtable.state()

if __name__ == '__main__':
    # NOTE: flask debug mode causes problems with threads: the motor movement was interrupted
    
    parser = argparse.ArgumentParser()

    parser.add_argument('--motor_forward_pin', required=False, type=int, default=24, help='GPIO PIN connected to the L298N motor driver FORWARD PIN')
    parser.add_argument('--motor_backward_pin', required=False, type=int, default=23, help='GPIO PIN connected to the L298N motor driver BACKWARD PIN')
    parser.add_argument('--motor_enable_pin', required=False, type=int, default=25, help='GPIO PIN connected to the L298N motor driver ENABLE PIN')
    parser.add_argument('--motor_speed', required=False, type=float, default=1.0, help='motor speed (0,1>')

    parser.add_argument('--lsensor_sample_rate', required=False, type=int, default=30, help='TCRT5000 (+ LM393) proximity sensor sample rate in Hz')
    parser.add_argument('--lsensor_pin', required=False, type=int, default=16, help='GPIO PIN connected to the TCRT5000 (+ LM393) proximity sensor')
    parser.add_argument('--lsensor_resolution_deg', required=False, type=float, default=1.0, help='optical encoder wheel resolution in degrees')

    try:
        args = parser.parse_args()
    except SystemExit as e:
        logger.error(e)
        os._exit(e.code)
   
    print(f"arguments: {args}")
    app.args = vars(args)   
    app.mtable = MeasurementTable(**app.args)
    
    app.run(host='0.0.0.0', port=5000)
    