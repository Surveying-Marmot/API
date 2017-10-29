from app import app, db, auth
from flask import Flask, request, url_for, jsonify, abort, g
from app.models import Users

@app.route(app.config['BASE_URL']+"/users/create", methods=["POST"])
def create_user():
    """ Create a new user """

    # Validate the inputs
    username = request.json.get('username')
    password = request.json.get('password')

    if username is None or password is None:
        abort(400)
    if Users.query.filter_by(username = username).first() is not None:
        abort(400)

    user = Users(username = username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({ 'username': user.username }), 201

@app.route(app.config['BASE_URL']+'/users/login')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({ 'token': token.decode('ascii') })

@app.route(app.config['BASE_URL']+'/users/<int:id>')
@auth.login_required
def get_user(id):
    user = Users.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})

@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = Users.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = Users.query.filter_by(username = username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True
