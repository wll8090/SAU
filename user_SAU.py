from ldap3 import Server, Connection, ALL  
from config import HOST_LDAP , DOMINIO
from random import randint
from hashlib import sha256
from json import loads, dump
import shutil
import os

server=Server(HOST_LDAP,get_info=ALL)

def reload_users(update_file=False):
    global data_users
    if update_file:
        with open('./users.ini','w') as arq:
            dump(data_users , arq)

    with open('./users.ini','r') as arq:
        _users=loads(arq.read())
        data_users.update(_users)
    return data_users

data_users={}
reload_users()

class SAU:
    def validar(func):
        def newfun(self,data,token):
            if token == self.token:
                return func(self,data)
            else: return {"response":False, 'mensg':'erro no token'}
        return newfun

    def login(self,user,pwd,ip):
        reload_users()
        self.user=user
        self.pwd=pwd
        self.conn = Connection(server, user + DOMINIO, pwd)
        if self.conn.bind():
            self.ip=ip
            self.dados=data_users.get(user)
            if not self.dados:
                return {"response":False, 'mensg':'usuario não cadastrados',"token":None, 'filhos':None, 'acesso':None}
            self.acesso=f'./static{self.dados.get("acesso")}'
            self.token=sha256((ip+user).encode()).hexdigest()
            return {"response":True, 'mensg':'sucess', 'token': self.token, "acesso":self.acesso, 'filhos':self.dados.get('filhos')}
        else: return {"response":False, 'mensg':'nome ou senha invalido',"token":None, 'filhos':None, 'acesso':None}

    @validar
    def new_path(self,data):
        nome_path=data.get('nome')
        rota= f'{self.acesso}{data["rota"]}'
        if not os.path.exists(rota):
            return {"response":False, 'mensg':f'{rota} não existe'}
        path=f'{rota}{nome_path}'
        if os.path.exists(path):
            return {"response":False, 'mensg':f'{nome_path}/ já existe em: {rota.replace("./static/","")}'}
        os.mkdir(path)
        return {"response":True, 'mensg':'sucess'}
    
    @validar
    def del_path(self,data):
        nome_path=data.get('nome')
        rota= f'{self.acesso}{data["rota"]}'
        confirm=data.get('confirm')
        path=rota+nome_path
        if not os.path.exists(path):
            return {"response":False, 'mensg':f'{path.replace("./static/","")}/ não existe'}
        try:
            os.rmdir(path)
        except OSError as err:
            if 'A pasta não está vazia:' in  str(err):
                if confirm:
                    shutil.rmtree(path)
                else:
                    return {"response":False, 'mensg':f'{path.replace("./static/","")}/ não esta vazia'}
            else: 
                raise err
        return {"response":True, 'mensg':'sucess'}

    @validar
    def del_file(self,data):
        nome_file=data.get('file')
        file= self.acesso + data["rota"]+ nome_file
        print(file)
        if os.path.exists(file):
            os.remove(file)
            return {"response":True, 'mensg':'sucess'}
        else: return {"response":False, 'mensg':f'{nome_file}/ Não existe'}
    
    @validar
    def new_user(self,data):
        path=data.get('path')
        new_user=data.get('user')
        acesso=f'{data["rota"]}{path}'
        if new_user in data_users:
            return {"response":False, 'mensg':'usuario já existe'}
        data_users[new_user]={"acesso":acesso, "filhos":[]}
        self.dados['filhos'].append(new_user)
        data_users[new_user]={"acesso":acesso, "filhos":[]}
        reload_users(update_file=True)
        return {"response":True, 'mensg':'sucess'}
    
    @validar
    def del_user(self,data):
        user=data.get('user')
        if user not in data_users:
            return {"response":False, 'mensg':'usuario não existe'}
        data_users.pop(user)
        self.dados['filhos'].remove(user)
        reload_users(update_file=True)
        return {"response":True, 'mensg':'sucess'}
    
    @validar
    def upload(self, data):
        file=data.get('file')
        path=data.get('path')
        path=self.acesso+path[1:]
        if not os.path.exists(path):
            return {"response":False, 'mensg':'pasta não existe'}
        try:
            file.save(path+file.filename)
            return {"response":True, 'mensg':f'{file.filename} salvo!'}
        except :
            return {"response":False, 'mensg':f'erro ao salvar {file.filename}'}



