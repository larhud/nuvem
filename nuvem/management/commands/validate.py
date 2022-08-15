import os
import requests

import hashlib

from django.core.management.base import BaseCommand
from django.conf import settings
from nuvem.models import Documento
from gerador.pdf2txt import pdf2txt


# Esta rotina é necessária para os casos de falha na conversão
class Command(BaseCommand):
    help = 'Valida e converte os textos dos documentos consolidados'

    def handle(self, *args, **options):
        base_dir = os.path.dirname(os.path.abspath(__file__)).split('/')[:-3]
        base_dir = '/'.join(base_dir)
        for doc_base in Documento.objects.filter(status='P'):
            print(f'Iniciando a geração do txt: {doc_base.id}')
            extra_file = open(doc_base.arquivo.path, 'w+')
            for doc in Documento.objects.filter(chave=doc_base.chave).exclude(id=doc_base.id):
                filename, extensao = os.path.splitext(doc.arquivo.path)
                if extensao == '.pdf' and not os.path.exists(filename + '.txt'):
                    print(f'Iniciando conversão PDF: {filename}')
                    pdf2txt(doc.arquivo.path)
                with open(filename + '.txt', 'r') as f:
                    extra_file.write(f.read())
                    extra_file.write('\n')
            extra_file.close()
            doc_base.status = 'F'
            doc_base.save()
            print(f'Documento finalizado {doc_base.id}')
