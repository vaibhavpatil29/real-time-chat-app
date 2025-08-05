import eventlet
eventlet.monkey_patch()
from flask import Flask, render_template, request, redirect
from flask_socketio import SocketIO

from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=True)
