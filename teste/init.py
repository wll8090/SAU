import requests
from time import sleep
import os

os.system('cls')
host='192.168.40.102'
port=5001

def local(megs,metod,rota, arg, head=''):
    print(f'Requisição de --->  {megs}')
    url=f'http://{host}:{port}'
    if metod == 'get':
        a=requests.get(f'{url}{rota}?{arg}')
    elif metod =='post':
        a=requests.post(f'{url}{rota}', **arg, headers= head)

    print(f'teste em: {a.url}')
    print(f'code ---> {a.status_code}')
    print(a.text)
    if 'true' in a.text:
        print('passou')
    else:
        print('erro <<<<<<<<')
    print('\n\n\n')
    sleep(1)
   



local('files','get','/files','file=/')

user=    #adicioanr um usuario  é o mesmo que vai para as URLs
pwd=     # adicionar a senha do usuario
data={'json':{'user':user,'pwd':pwd }}  #  << erro se n tiver usuario vinculado ao LDAP e senha 
local('login','post','/login/login', data)

token=   # adicionar um token Bearer
head={'Authorization':f'Bearer {token}'}
data={'json':{'nome':'pasta_teste'}}
local('criar pasta','post','/sergio.sousa/new_path?path=/', data, head=head)


data={'json':{'user':'user.teste','path':'pasta_teste'}}
local('criar usuario','post',f'/{user}/new_user?path=/', data, head=head)


data={'files':{'file':('init.py',open('./init.py','rb'))}}
local('uploads','post',f'/{user}/upload?path=/pasta_teste/', data , head=head)


data={'json':{'file':'init.py'}}
local('uploads','post',f'/{user}/del_file?path=/pasta_teste/', data , head=head)


data={'json':{'user':'user.teste'}}
local('deletar usuario','post',f'/{user}/del_user?path=/', data, head=head)


data={'json':{'nome':'pasta_teste'}}
local('deletar pasta','post',f'/{user}/del_path?path=/', data, head=head)

