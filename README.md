# Nuvem de Palavras Larhud
Este serviço permite gerar uma nuvem de palavras para textos em português, inglês ou espanhol.
O intuito é que um usuário leigo possa executar uma nuvem de palavras sem que precise instalar nenhum software
em seu computador. Para tal, o usuário precisa apenas enviar um arquivo em PDF ou TXT e o serviço irá gerar a imagem com uma nuvem de palavras.

#Como instalar

1) Faça o download do projeto via git clone

```
git clone https://github.com/larhud/nuvem.git
cd nuvem
virtualenv -p python3 .venv
source .venv/bin/activate
pip install -r requirements.txt
```     

2) copie o local.py para o diretório larhud e altere o arquivo com as configurações específicas da sua instalação

3) Crie o banco e teste se está tudo ok:

```
python manage.py migrate
python manage.py check
```

4) Para rodar na sua máquina local, basta rodar python manage.py runserver.

5) Caso você queira rodar em um servidor, procure as configurações do NGINX e do supervisor na pasta /configs/defaults
