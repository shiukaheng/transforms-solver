# Websocket server for manipulating the scene
import socketio
import eventlet # Needed for socketio

sio = socketio.Server()
app = socketio.WSGIApp(sio)

# On connection, send the scene to the client, use dummy data for now
@sio.on('connection')
def on_connection(sid, environ):
    sio.emit('scene', {'scene': 'dummy scene data'})
    print(f'Client connected: {sid}')

# On scene update, send the scene to all clients
@sio.on('update')
def on_update(sid, data):
    sio.emit('scene', {'scene': data['scene']})

# On disconnection, print a message
@sio.on('disconnect')
def on_disconnect(sid):
    print(f'Client disconnected: {sid}')

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)

