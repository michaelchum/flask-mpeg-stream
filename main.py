from flask import Flask, render_template, Response
from camera import VideoCamera
import zmq
from threading import Thread
import numpy as np
from time import sleep

server_started = False
global_img = None

def init_server():
    global server_started
    if not server_started:
        server_started = True
        t = Thread(target=zero_server)
        t.start()

def zero_server():
    global global_img
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("ipc:///zero/0")
    while True:
        #  Wait for next request from client
        message = socket.recv()
        print("Updated global")
        global_img = np.fromstring(message, dtype=np.uint8)
        # global_img = cv2.imdecode(frame, 1)
        # cv2.imwrite("hello.jpg", global_img)
        # ret, global_img = cv2.imencode('.jpg', global_img)
        socket.send(b"Updated")

def gen_img():
    global global_img
    while global_img is not None:
        sleep(0.04)
        try:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + global_img.tobytes() + b'\r\n\r\n')
        except:
            print("Disconnected")
            break

app = Flask(__name__)

@app.route('/')
def index():
    init_server()
    return render_template('index.html')

@app.route('/init')
def init():
    init_server()
    return 'Init'

# def gen(camera):
#     while True:
#         frame = camera.get_frame()
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    init_server()
    global global_img
    # return Response(gen(VideoCamera()),
    #                 mimetype='multipart/x-mixed-replace; boundary=frame')
    if global_img is not None:
        try:
            return Response(gen_img(), mimetype='multipart/x-mixed-replace; boundary=frame')
        except:
            print("Disconnected")
    return "No image"

@app.route('/<path:dummy>')
def fallback(dummy):
    init_server()
    return 'This one catches everything else'

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000, threaded=True)