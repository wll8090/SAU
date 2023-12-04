import requests
from time import sleep
import os

os.system('cls')
host='192.168.40.102'
port=5001


arquivos=0
login=1
criar_user=0
criar_pasta=1
fazer_upload=1
estado=1
filhos=0
rename=0
files=1



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
    sleep(2)
   


if arquivos:
    local('files','get','/none/files','file=/')

user= 'sergio.ti'          # adicioanr um usuario  é o mesmo que vai para as URLs
pwd=  '@Aa1020'         # adicionar a senha do usuario
data={'json':{'user':user,'pwd':pwd }}  #  << erro se n tiver usuario vinculado ao LDAP e senha 
local('login','post','/login/login', data)

token= 'aa5b5f5097b95ba6f99f0477a05e913efbb9a5c3955cb6a70c20e11198df2607'  # adicionar um token Bearer
head={'Authorization':f'Bearer {token}'}


if files:
    data={'json':{'user':'user.teste'}}
    local('busca de arquivos','get',f'/{user}/files','path=./', head=head)

#nova pasta
if criar_pasta:
    data={'json':{'nome':'pasta_teste'}}
    local('criar pasta','post',f'/{user}/new_pasta?path=./', data, head=head)        


#new user
if criar_user:
    data={'json':{'user':'user.teste'}}
    local('criar usuario','post',f'/{user}/new_user?path=./sti/teste/', data, head=head)          


#upload
if fazer_upload:
    data={'files':{'file':('dino.jpg',open('./teste/dino.jpg','rb'))}}
    local('uploads','post',f'/{user}/upload?path=./pasta_teste/', data , head=head)     


#estado do arquivo
if estado:
    data={'json':{'file':'dino.jpg','estado':'online'}}
    local('deletar pasta','post',f'/{user}/estado?path=./pasta_teste/', data, head=head)

if files:
    data={'json':{'user':'user.teste'}}
    local('busca de arquivos','get',f'/{user}/files','path=./', head=head)


#deletar_pastar
if fazer_upload:
    data={'json':{'file':'dino.jpg'}}
    local('deletar arquivo','post',f'/{user}/del_file?path=./pasta_teste/', data , head=head)     


#ver filhos  ./
if filhos:
    data={'json':{'user':'user.teste'}}
    local('ver filhos em ./','post',f'/{user}/filhos?path=./', data, head=head)

#ver filhos  ./fisica/
if filhos:
    data={'json':{'user':'user.teste'}}
    local('ver filhos em ./fisica/','post',f'/{user}/filhos?path=./fisica/', data, head=head)

#ver filhos  ./quimica/
if filhos:
    data={'json':{'user':'user.teste'}}
    local('ver filhos em ./quimica/','post',f'/{user}/filhos?path=./quimica/', data, head=head)   


#deletar user
if criar_user:
    data={'json':{'user':'user.teste'}}
    local('deletar usuario','post',f'/{user}/del_user?path=./', data, head=head)          


#deletar pasta
if criar_pasta:
    data={'json':{'nome':'pasta_teste'}}
    local('deletar pasta','post',f'/{user}/del_pasta?path=./', data, head=head)

#renomear arquivos e pastas
if rename:
    data={'json':{'nome':'fisica', 'new_nome':'test_pasta'}}
    local('deletar pasta','post',f'/{user}/rename?path=./', data, head=head)



if rename:
    data={'json':{'nome':'test_pasta', 'new_nome':'fisica'}}
    local('deletar pasta','post',f'/{user}/rename?path=./', data, head=head)
