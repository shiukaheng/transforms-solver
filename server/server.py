# Websocket server for manipulating the scene
import socketio
import eventlet

from graphs import TestTransformationGraph # Needed for socketio

sio = socketio.Server(cors_allowed_origins='*')
app = socketio.WSGIApp(sio)

CAMERA = 0
HEADSET = 1
WORLD = 2

# Create the world
world = TestTransformationGraph(3, [
    (CAMERA, HEADSET, "non-rigid-unknown", 1),
    (CAMERA, WORLD, "rigid-known", 1),
    (HEADSET, WORLD, "rigid-known", 1),
], 1)

# On connection, send the scene to the client, use dummy data for now
@sio.on('connect')
def on_connect(sid, environ):
    print(f'Client connected: {sid}')
    sio.emit('graph', world.to_dict())

# # On scene update, send the scene to all clients
# @sio.on('update')
# def on_update(sid, data):
#     sio.emit('graph', world.to_dict())

# On disconnection, print a message
@sio.on('disconnect')
def on_disconnect(sid):
    print(f'Client disconnected: {sid}')

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)