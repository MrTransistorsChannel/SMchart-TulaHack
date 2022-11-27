import os

from flask import Flask, request, Response, jsonify, session, g

app = Flask(__name__)
app.secret_key = 'bd9AHE3qPO4KEbXe19MTYunuWUwV6L3I75Mp2K0sNHNuJaO7gLL8pGUdPn6hcBgn'
app.config['SESSION_COOKIE_SAMESITE'] = "None"

responseWithCredentials = Response()  # Sample response with cross-domain cookies
responseWithCredentials.headers['Access-Control-Allow-Credentials'] = 'true'
responseWithCredentials.headers['Vary'] = 'Origin'

diagramStorage = 'diagram_storage_test/'  # Path to test diagram storage


class User:
    def __init__(self, username, password, diagrams=None):
        self.username = username
        self.password = password
        self.diagrams = diagrams

    def __repr__(self):
        return f'<User: {self.username}>'

        # Test storage for users and their diagrams, was planned to be inside SQL database


users = [User(username='1', password='1', diagrams=['notSoAwesomeDiagram', 'awesomeDiagram', 'multiple']),
         User(username='badrequest', password='password'),
         User(username='lyagush0n0k', password='password')]

'''@app.route('/element_changed', methods=['POST'])   # Was planned to be used for multi-user functionality, event-based system
def element_changed():
    print(request.form)
    return '', 200
'''


@app.before_request
def before_request():
    g.user = None
    if 'username' in session:
        user = [x for x in users if x.username == session['username']]
        g.user = user[0] if user else None


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':  # GET request returns status of the login and account info
        if session.new or 'username' not in session:
            resp = responseWithCredentials
            resp.data = 'Unauthorized'
            resp.headers['Access-Control-Allow-Origin'] = request.origin
            resp.status = 401
            return resp

        resp = responseWithCredentials
        resp.data = session['username']
        resp.headers['Access-Control-Allow-Origin'] = request.origin
        resp.status = 200
        return resp

    elif request.method == 'POST':  # POST request is used for authorization
        session.pop('username', None)
        print('Received new login request')
        user = [x for x in users if x.username == request.form.get('username')]

        if len(user) > 0 and user[0].password == request.form.get('password'):
            session['username'] = user[0].username
            session.modified = True

            resp = responseWithCredentials
            resp.data = session['username']
            resp.headers['Access-Control-Allow-Origin'] = request.origin
            resp.status = 200
            return resp
        else:
            resp = responseWithCredentials
            resp.data = 'Wrong password'
            resp.headers['Access-Control-Allow-Origin'] = request.origin
            resp.status = 403
            return resp


@app.route('/diagrams', methods=['GET', 'POST'])
def diagram_handler():
    if not g.user:
        resp = responseWithCredentials
        resp.data = 'Forbidden'
        resp.headers['Access-Control-Allow-Origin'] = request.origin
        resp.status = 403
        return resp

    if request.method == 'GET':  # GET requests handle file list and reading files from the server
        if 'name' in request.args:
            with open(diagramStorage + request.args.get('name') + '.bpmn', 'r') as diagram:
                diagramXML = diagram.read()
                resp = responseWithCredentials
                resp.data = diagramXML
                responseWithCredentials.headers['Access-Control-Allow-Origin'] = request.origin
                resp.status = 200
                return resp

        resp = jsonify({
            'diagrams': g.user.diagrams
        })
        resp.headers['Access-Control-Allow-Origin'] = request.origin
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        resp.headers['Vary'] = 'Origin'
        resp.status = 200
        return resp
    elif request.method == 'POST':  # POST requests handle file saves
        diagramName = request.form.get('name')
        diagramXML = request.form.get('content')

        diagramPath = diagramStorage + diagramName + '.bpmn'

        with open(diagramPath, 'w+') as diagram:
            diagram.truncate(0)
            diagram.write(diagramXML)

        resp = responseWithCredentials
        resp.response = ""
        responseWithCredentials.headers['Access-Control-Allow-Origin'] = request.origin
        resp.status = 200
        return resp
    elif request.method == 'PUT':  # PUT requests handle modification of the file (e.g. renaming)
        action = request.form.get('action')
        if action == 'rename':
            newName = request.form.get('newName')
            oldName = request.form.get('oldName')
            os.system('mv ./' + diagramStorage + oldName + '.bpmn ./' + diagramStorage + newName + '.bpmn')

            resp = responseWithCredentials
            resp.data = diagramStorage + newName + '.bpmn'
            resp.headers['Access-Control-Allow-Origin'] = request.origin
            resp.status = 200
            return resp


app.run()
