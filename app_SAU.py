from flask import Flask , request, send_file , jsonify, render_template
from flask_cors import CORS
from user_SAU import SAU
from config import PORT, HOST, HOST_LDAP, ipCORS
from json import loads
import os
from jinja2 import Template


users=dict()


def login(data,ip):
    global users
    user=data.get('user')
    test=SAU()
    r=test.login(user,data.get('pwd'),ip)
    if r.get('response'):
        users[user]=test
    return r

def tipo(i):
    tipo=i.split('.')
    if len(tipo)<2:
        tipo = 'path'
    else:
        tipo=tipo[-1]
    return {'file':i, 'type':tipo }


def creatapp():
    app=Flask(__name__)

    CORS(app,restore={r"/*":{"origins":f"http://{ipCORS}" , "supports_credentials":True ,  "headers": ["Authorization"]}})

    @app.route('/files')
    def index():
        req=dict(request.args)
        file=req.get('file')
        if '.' in file:
            return send_file(f'./static/{file}')
        if not os.path.exists(f'./static/{file}'):
            return jsonify({"response": False, "file":None})
        conteudo=os.listdir(f'./static/{file}')
        conteudo=list(map(tipo , conteudo))
        return jsonify({"response": True, "file":conteudo})
    
    @app.route('/<user>/<acao>',methods=['GET','POST'])
    def main(user,acao):
        ip=request.remote_addr
        if request.method=='GET':
            if acao =='files':
                return 'get in files'
            
        elif request.method=='POST':
            tt=request.headers.get('Authorization')

            path=request.args.get('path')
            path = path if path else '/'
            tokem=dict([tt.split(' ') if tt else ['a','b']])
            bearer=tokem.get('Bearer')
            if request.data:
                data=loads(request.data)
            else:
                data={}

            ###### ---------rotas para posts    
            if acao == 'login':
                return jsonify(login(data,ip))
        
            elif acao == 'new_path':
                data['rota']=path
                return  jsonify(users.get(user).new_path(data,bearer))
            
            elif acao == 'del_path':
                data['rota']=path
                return jsonify(users.get(user).del_path(data,bearer))
            
            elif acao == 'del_file':
                data['rota']=path
                return jsonify(users.get(user).del_file(data,bearer))
            
            elif acao == 'new_user':
                data['rota']=path
                return jsonify(users.get(user).new_user(data,bearer))
            
            elif acao == 'del_user':
                data['rota']=path
                return jsonify(users.get(user).del_user(data,bearer))
            
            elif acao == 'upload':
                file= request.files['file']
                data={'file':file, 'path':path}
                return jsonify(users.get(user).upload(data,bearer))
                
    @app.route('/doc')
    def doc():
        with open('templates/doc.html') as arq:
            text=Template(arq.read()).render()
        return (text)

            
    return app


app=creatapp()
app.run(host=HOST, port=PORT,)