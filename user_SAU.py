from ldap3 import Server, Connection, ALL
from datetime import datetime
from config import HOST_LDAP , DOMINIO, FILES_PERMITIDOS
from hashlib import sha256
from json import loads, dumps
import shutil
import os


server=Server(HOST_LDAP,get_info=ALL)

def reload_users(update_file=False):
    global data_users
    with open('./users.ini','r') as arq:
        _users=loads(arq.read())
        data_users.update(_users)
    return data_users
data_users={}
reload_users()

def reload_files(update_file=False):
    global data_files
    with open('./arquivo_online.json','r',encoding='utf8') as arq:
        _files=loads(arq.read())
        data_files.update(_files)
    return data_files
data_files=dict()
reload_files()


def salva_arquivi_data(file,dados):
    with open(file,'w') as arq:
            dd=dumps(dados, indent=4)
            arq.write(dd)
            arq.close()

class SAU:
    def validar(func):
        def newfun(self,data,token):
            data['path']=data['path'].replace('./', self.acesso)
            if token == self.token:
                return func(self,data)
            else: return {"response":False, 'mensg':'erro no token'}
        return newfun
    
    def salva_estado_files(self, file, estado, isdir=False):
        if estado=='delete':
            if isdir:
                conteudo=[i for i in data_files if file+'/' in i]
                for i in conteudo:
                    data_files.pop(i)
            data_files.pop(file)
        elif estado in ('online','offline'):
            data_naw=datetime.now().strftime('%d/%m/%Y')
            data_files[file]={"estado":estado,"person":self.user,"data":data_naw}
            
        salva_arquivi_data('./arquivo_online.json',data_files)
        reload_files()

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
            self.acesso=self.dados.get("acesso").replace('./','./static/')
            self.token=sha256((ip+user).encode()).hexdigest()
            return {"response":True, 'mensg':'Feito', 'user':self.user , 'token': self.token, "acesso":self.acesso, 'filhos':self.dados.get('filhos')}
        else: return {"response":False, 'mensg':'nome ou senha invalido',"token":None, 'filhos':None, 'acesso':None}

    @validar
    def new_pasta(self,data):
        nome_pasta=data.get('nome')
        rota= data["path"]
        if not os.path.exists(rota):
            return {"response":False, 'mensg':f'{rota.replace("./static/","")} não existe'}
        path=f'{rota}{nome_pasta}'
        if os.path.exists(path):
            return {"response":False, 'mensg':f'{nome_pasta}/ já existe em: {rota.replace("./static/","")}'}
        os.mkdir(path)
        self.salva_estado_files(path,'offline')         # adiciona estado online para nova pasta
        return {"response":True, 'mensg':'Feito'}
    
    @validar
    def del_pasta(self,data):    # deletar pasta
        path= data["path"]+data.get('nome')
        confirm=data.get('confirm')
        if not os.path.exists(path):
            return {"response":False, 'mensg':f'{path.replace("./static/","")}/ não existe'}
        isdir=os.path.isdir(path)
        try:
            os.rmdir(path)
        except OSError as err:
            if confirm:
                shutil.rmtree(path)
            else:
                return {"response":False, 'mensg':f'{path.replace("./static/","")}/ não esta vazia'}
        self.salva_estado_files(path,'delete', isdir)   # deleta estado da pasta  
        return {"response":True, 'mensg':'Feito'}

    @validar
    def del_file(self,data):    #deletar arquivo
        file_name=data.get('file')
        path=data['path']
        file=path+file_name
        if os.path.exists(file):
            os.remove(file)
            self.salva_estado_files(file,'delete')               # deleta file da base estado para de arquivo
            return {"response":True, 'mensg':'Feito'}
        else: return {"response":False, 'mensg':f'{file}/ Não existe'}
    
    @validar
    def new_user(self,data):
        """ feito para adicionar um novo usuario
            redebe os 
        """
        reload_users()
        path=data.get('path').replace('./static/','./')
        new_user=data.get('user')
        if new_user in data_users:
            return {"response":False, 'mensg':'usuario já existe'}
        data_users[new_user]={"acesso":path, "filhos":[]}
        self.dados['filhos'].append(new_user)
        data_users[self.user]=self.dados
        salva_arquivi_data('./users.ini', data_users)
        reload_users()
        return {"response":True, 'mensg':'Feito'}
    
    @validar
    def del_user(self,data):
        user=data.get('user')
        data_users=globals()['data_users']
        if user not in data_users:
            return {"response":False, 'mensg':'usuario não existe'}
        else:
            if data_users.get(user)['filhos']:
                return {"response":False, 'mensg':f'usuario {user} tem filhos, não poder ser excuido'}
            data_users.pop(user)
            if user in self.dados['filhos']:
                self.dados['filhos'].remove(user)
            else: 
                return {"response":False, 'mensg':f'{user} não é filho de {self.user}'}
        data_users[self.user]=self.dados
        salva_arquivi_data('./users.ini',data_users)
        reload_users()
        return {"response":True, 'mensg':'Feito'}
    
    @validar
    def upload(self, data):
        file=data.get('file')
        if (a:=(file.filename.split('.')[-1])) not in FILES_PERMITIDOS:
            return {"response":False, 'mensg':f'arquivo não permitido .{a}'}

        path=data.get('path')
        if not os.path.exists(path):
            return {"response":False, 'mensg':'pasta não existe'}
        try:
            file.save(path+file.filename)
            self.salva_estado_files(path+file.filename,'offline')         #adiciona estado online para file
            return {"response":True, 'mensg':f'{file.filename} salvo!'}
        except :
            return {"response":False, 'mensg':f'erro ao salvar {file.filename}'}
        
    @validar
    def filhos(self,data):
        path=data.get('path').replace('./static/','./')
        l=[i for i in self.dados.get('filhos') if data_users.get(i).get('acesso')==path]
        reload_users()
        return {"response":True, 'filhos':l}
    
    @validar
    def estado(self,data):
        file=data.get('file')
        estado=data.get('estado').lower()
        path=data.get('path')
        file=path+file
        arq=data_files.get(file)
        if arq:
            self.salva_estado_files(file,estado)  # muda estado de file ou pasta
            return {"response":True, 'mensg':f"arquivo {file.replace('./static/','./')} {estado}"}
        else:
            return {"response":False, 'mensg':f"arquivo {file.replace('./static/','./')} não encontrado"}
    
    @validar
    def rename(self,data):
        nome=data.get('nome')
        new_nome=data.get('new_nome')
        path=data.get('path')
        file=path+nome
        tipo=''
        if not os.path.exists(file):
            return {"response":False, 'mensg':f'arquivo não encontrado'}
        if os.path.isfile(file):
            tipo='.'+nome.split('.')[-1]
        new=path+new_nome+tipo
        if os.path.isdir(file):
            acesso=file.replace('./static/','./')+'/'
            new_acesso=acesso.replace(nome,new_nome)
            l=[i for i in data_users if acesso in data_users[i].get('acesso')]
            if l:
                for i in l:
                    print(data_users.get(i)['acesso'])
                    data_users.get(i)['acesso']=data_users.get(i)['acesso'].replace(acesso,new_acesso)
                salva_arquivi_data('./users.ini',data_users)

        if os.path.isdir(file):
            d={}
            for i in data_files:
                if file+'/' in i:
                    keyii=i.replace(file+'/',new+'/')
                    d[keyii]=[i,data_files[i]]  
            for i in d:
                data_files.pop(d[i][0])
                data_files[i]=d[i][1]
        data_files[new]=data_files.pop(file)
        os.rename(file,new)
        salva_arquivi_data('./arquivo_online.json',data_files)
        return {"response":True, 'mensg':f'nome alterado'}
            
