from flask import Flask , request, send_file , jsonify, render_template
from flask_cors import CORS
from user_SAU import SAU
from config import PORT, HOST, HOST_LDAP, ipCORS, DOMINIO
from json import loads
import os
from jinja2 import Template
from hashlib import sha256


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

    
    @app.route('/<user>/<acao>',methods=['GET','POST'])
    def main(user,acao):
        ip=request.remote_addr
        tt=request.headers.get('Authorization')
        ###### ---------rotas for GET
        if request.method=='GET':
            if acao == 'files':
                if user != "none":
                    user=users.get(user)
                    if user:
                        if ip==user.ip:
                            rota=user.acesso.replace('./static/','')
                        else:
                            return jsonify({"response": False, "mensg": f"erro no ip {ip}, faça login"})
                    else:
                        return jsonify({"response": False, "mensg":"user não logado"})
                else:
                    rota=''
                req=dict(request.args)
                file=f'./static/{rota}{req.get("file")}'
                if os.path.isfile(file):
                    return send_file(file)
                if not os.path.exists(file):
                    return jsonify({"response": False, "file":None})
                conteudo=os.listdir(file)
                conteudo=list(map(tipo , conteudo))
                return jsonify({"response": True, "file":conteudo}) 
            

        elif request.method=='POST':
            if user not in users and acao != 'login' :
                return jsonify({"response":False, 'mensg':f'{user} não logado'})

            path=request.args.get('path')
            path = path if path else './'
            tokem=dict([tt.split(' ') if tt else ['a','b']])
            bearer=tokem.get('Bearer')
            if request.data:
                data=loads(request.data)
            else:
                data={}

            ###### ---------rotas for POST
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
                print(data)
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
app.run(host=HOST, port=PORT, debug=1)