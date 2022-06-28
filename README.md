# Nuvem de Palavras Larhud
Este serviço permite gerar uma nuvem de palavras para textos em português, inglês ou espanhol.
O intuito é que um usuário leigo possa executar uma nuvem de palavras sem que precise instalar nenhum software
em seu computador. Para tal, o usuário precisa apenas enviar um arquivo em PDF ou TXT e o serviço irá gerar a imagem com uma nuvem de palavras.

## Como instalar

1) Faça o download do projeto via git clone

```
git clone https://github.com/larhud/nuvem.git
cd nuvem
virtualenv -p python3 .venv
source .venv/bin/activate
pip install -r requirements.txt
```     

2) copie o configs/defaults/local.py para o diretório larhud e altere o arquivo com as configurações específicas da sua instalação, principalmente com os parâmetros do banco de dados e do font_path

* Confira se DEBUG=True para que você consiga visualizar as imagens localmente.
* Confira se o FONT_PATH está apontando para o caminho correto.
* Se estiver usando Windows, o FONT_PATH deve ser o caminho para a pasta de fontes do Windows, geralmente localizada em `C:/Windows/Fonts/`.
* Caso tenha algum problema com a o caminho padrão do Windows, tente passar o caminho para a pasta de fontes do projeto, localizada em `/nuvem/estaticos/fonts/` (lembre-se de passar o caminho completo, onde seu projeto está localizado).
* Nota: Cuidado ao usar `\`, pois o python utiliza `\` para introduzir caracteres especiais. Ná duvida substitua por `/` ou `\\`.


3) Se você estiver utilizando MySQL, crie o banco. Se você estiver utilizando sqlite, basta rodar o migrate que o banco é criado automaticamente:

```
python manage.py migrate
python manage.py check
```

4) Para rodar na sua máquina local, basta rodar python manage.py runserver.

5) Para acessar o ambiente administrativo, crie um usuário: 

```
python manage.py createsuperuser
```

6) Caso você queira rodar em um servidor, procure as configurações do NGINX e do supervisor na pasta /configs/defaults
