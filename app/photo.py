from app import app, db, auth
from flask import Flask, request, url_for, jsonify, abort, g
from app.models import Photo


