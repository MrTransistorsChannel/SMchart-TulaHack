from flask import Flask, request, Response, jsonify, session, g

app = Flask(__name__)
app.secret_key = 'bd9AHE3qPO4KEbXe19MTYunuWUwV6L3I75Mp2K0sNHNuJaO7gLL8pGUdPn6hcBgn'
app.config['SESSION_COOKIE_SAMESITE'] = "None"

responseWithCredentials = Response()
responseWithCredentials.headers['Access-Control-Allow-Origin'] = 'http://localhost:8081'
responseWithCredentials.headers['Access-Control-Allow-Credentials'] = 'true'
responseWithCredentials.headers['Vary'] = 'Origin'

diagramStorage = 'diagram_storage_test/'

class User:
    def __init__(self, username, password, diagrams=None):
        self.username = username
        self.password = password
        self.diagrams = diagrams

    def __repr__(self):
        return f'<User: {self.username}>'


users = [User(username='1', password='1', diagrams=['awesomeDiagram', 'multiple']),
         User(username='badrequest', password='password'),
         User(username='lyagush0n0k', password='password')]

'''@app.route('/element_changed', methods=['POST'])
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
    if request.method == 'GET':
        if session.new or 'username' not in session:
            resp = responseWithCredentials
            resp.response = 'Unauthorized'
            resp.status = 401
            return resp

        resp = responseWithCredentials
        resp.response = session['username']
        resp.status = 200
        return resp

    elif request.method == 'POST':
        session.pop('username', None)
        print('Received new login request')
        user = [x for x in users if x.username == request.form.get('username')]

        if len(user) > 0 and user[0].password == request.form.get('password'):
            print('username' in session)
            session['username'] = user[0].username
            session.modified = True

            resp = responseWithCredentials
            resp.response = session['username']
            resp.status = 200
            return resp
        else:
            resp = responseWithCredentials
            resp.response = 'Wrong password'
            resp.status = 403
            return resp


@app.route('/diagrams', methods=['GET', 'POST'])
def diagram_handler():
    if not g.user:
        resp = responseWithCredentials
        resp.response = 'Forbidden'
        resp.status = 403
        return resp

    if request.method == 'GET':
        if 'name' in request.args:
            with open(diagramStorage + request.args.get('name') + '.bpmn', 'r') as diagram:
                diagramXML = diagram.read()
                resp = responseWithCredentials
                resp.response = diagramXML
                resp.status = 200
                return resp

        resp = jsonify({
            'diagrams': g.user.diagrams
        })
        resp.headers['Access-Control-Allow-Origin'] = 'http://localhost:8081'
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        resp.headers['Vary'] = 'Origin'
        resp.status = 200
        return resp
    elif request.method == 'POST':
        diagramName = request.form.get('name')
        diagramXML = request.form.get('content')

        diagramPath = diagramStorage + diagramName + '.bpmn'

        with open(diagramPath, 'w+') as diagram:
            diagram.truncate(0)
            diagram.write(diagramXML)

        resp = responseWithCredentials
        resp.response = ""
        resp.status = 200
        return resp


app.run()
