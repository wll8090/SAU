imagem = imagem_api_SAU
api= conteiner_api_SAU
rede= rede_api_SAU

help:
        @echo "criar_image, del_image, criar_volume, run, stop"

criar_image:
        make stop
        docker build -t $(imagem) .

network:
        docker network create $(rede)

del_image:
        make stop
        docker image rm -f $(imagem)

run:
        docker run -p5001:5001 -d --network $(rede) --name $(api) -v ./:/main/ $(imagem)

i-run:
        docker run -p5001:5001 -it --name $(api) -v ./:/main/ $(imagem) bash

stop:
        docker rm -f $(api)

log:
        docker logs $(api)

update:
        make stop
        git pull