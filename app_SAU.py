from flask import Flask , request, send_file , jsonify, abort
from flask_cors import CORS
from user_SAU import SAU
from config import PORT, HOST, ipCORS
from json import loads
import os
from jinja2 import Template


users=dict()


def login(data,ip):
    global users
    user=data.get('user').lower()
    test=SAU()
    r=test.login(user,data.get('pwd'),ip)
    if r.get('response'):
        users[user]=test
    return r

def reload_files(update_file=False):
    global data_files
    with open('./arquivo_online.json','r') as arq:
        _files=loads(arq.read())
        data_files.update(_files)
    return data_files
data_files={}
reload_files()

def gerador_tipo(caminho):
    def tipo(i):
        tipo=i.split('.')
        if len(tipo)<2:
            tipo = 'path'
        else:
            tipo=tipo[-1]
        ii=(caminho+'/'+i).replace('//','/')
        estado=data_files.get(ii)
        return {'file':i, 'type':tipo, 'estado':estado }
    return tipo


def logout(data,ip):
    nome_user=data.get('user')
    user=users.get(nome_user)
    if not user:
        return {"response":False, "mensg":"user não encontrado"}
    else:
        if user.ip==ip:
            a=users.pop(nome_user)
            return {"response":True, "mensg":"ok"}
        else:
            {"response":False, "mensg":"ip não valido "}


login({'user':'sergio.ti','pwd':'@Aa1020'},'192.168.40.102')


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
                reload_files()
                data=dict(request.args)
                file=('./static/'+data.get('path')).replace('/./','/')
                blok=True
                if user != 'none' and user in users:    # if para usuario logado
                    if ip==users[user].ip:              #validação de ip
                        file=(users.get(user).acesso+data.get('path')).replace('/./','/')
                        blok=False
                if file.endswith('/'):
                    file=file[:-1]

                if blok:    # if que bloqueia as requisições
                    list_file=file.split('/')
                    for i in list_file[2:]:
                        i='/'.join(list_file)
                        if data_files[i]  =='offline':
                            return jsonify({"response": False, "mensg": "caminho não encontrado"})
                        list_file.pop()

                if os.path.isfile(file):   # if para ver de arquivos
                    return send_file(file)
                
                elif os.path.isdir(file):  #  envia todos os nomes de arquivos
                    files=os.listdir(file)
                    tipo=gerador_tipo(file)
                    files=list(map(tipo,files))
                    if blok:
                        files=[i for i in files if i['estado'] =='online']
                    return jsonify({"response": True, "files": files})
                else:
                    return jsonify({"response": True, "files": 'None'})


            

        elif request.method=='POST':
            if user not in users and acao != 'login' :
                return jsonify({"response":False, 'mensg':f'{user} não logado'})

            path=request.args.get('path')
            path = path if path else './'
            tokem=dict([tt.split(' ') if tt else ['a','b']])
            bearer=tokem.get('Bearer')
            data={}
            data['path']=path
            if request.data:
                data.update(loads(request.data))

            ###### ---------rotas for POST
            if acao == 'login':
                return jsonify(login(data,ip))
            
            elif acao == 'logout':
                return jsonify(logout(data,ip))
            
            elif acao == 'filhos':
                return  jsonify(users.get(user).filhos(data,bearer))
        
            elif acao == 'new_pasta':
                return  jsonify(users.get(user).new_pasta(data,bearer))
            
            elif acao == 'del_pasta':
                return jsonify(users.get(user).del_pasta(data,bearer))
            
            elif acao == 'del_file':
                return jsonify(users.get(user).del_file(data,bearer))
            
            elif acao == 'new_user':
                return jsonify(users.get(user).new_user(data,bearer))
            
            elif acao == 'del_user':
                return jsonify(users.get(user).del_user(data,bearer))
            
            elif acao == 'upload':
                file= request.files['file']
                data['file']=file
                return jsonify(users.get(user).upload(data,bearer))
            
            elif acao == 'rename':
                return jsonify(users.get(user).rename(data,bearer))
            
            elif acao == 'estado':
                return jsonify(users.get(user).estado(data,bearer))
        return abort(404)
                
    @app.route('/doc')
    def doc():
        with open('templates/doc.html',encoding='utf8') as arq:
            text=Template(arq.read()).render()
        return (text)

            
    return app


if __name__=="__main__":
    app=creatapp()
    app.run(host=HOST, port=PORT)