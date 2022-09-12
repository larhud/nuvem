import os
import sys
import re
import uuid
import json
import urllib
import detectlanguage
import numpy as np
from PIL import Image
from django.http import HttpResponseRedirect

from django.shortcuts import render, redirect, get_object_or_404

from threading import Thread
from datetime import datetime

from nuvem.models import Documento
from nuvem.forms import DocumentoForm, LayoutForm
from django.conf import settings
from gerador.genwordcloud import generate, generate_words
from django.contrib import messages
from gerador.pdf2txt import pdf2txt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
detectlanguage.configuration.api_key = settings.API_KEY_LANGUAGE


def home(request):
    return render(request, 'home.html')


class ProcessThread(Thread):
    def __init__(self, document_id):
        Thread.__init__(self)
        self.document_id = document_id
        self.started = datetime.now()

    def run(self):
        doc_base = Documento.objects.get(id=self.document_id)
        if doc_base.consolidado:
            extra_file = open(doc_base.arquivo.path, 'w+')
            for doc in Documento.objects.filter(chave=doc_base.chave).exclude(id=self.document_id):
                filename, extensao = os.path.splitext(doc.arquivo.path)
                if extensao == '.pdf':
                    pdf2txt(doc.arquivo.path)
                    print('PDF gerado %s' % doc.arquivo.path)
                with open(filename + '.txt', 'r') as f:
                    extra_file.write(f.read())
                    extra_file.write('\n')
            extra_file.close()
            doc_base.status = 'F'
            doc_base.save()
        else:
            pdf2txt(doc_base.arquivo.path)
            doc_base.status = 'F'
            doc_base.save()

        finished = datetime.now()
        duration = (finished - self.started).seconds
        print("%s thread started at %s and finished at %s in %s seconds" %
              (self.document_id, self.started, finished, duration))


def new_doc(request):
    form = DocumentoForm(request.POST or None, request.FILES or None)
    recaptcha = getattr(settings, "GOOGLE_RECAPTCHA_PUBLIC_KEY", None)

    if form.is_valid():
        if recaptcha:
            recaptcha_response = request.POST.get('g-recaptcha-response')
            url = 'https://www.google.com/recaptcha/api/siteverify'
            values = {
                'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            data = urllib.parse.urlencode(values).encode()
            req = urllib.request.Request(url, data=data)
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode())
            result = result['success']
        else:
            result = True

        if result:
            post = form.save(commit=False)
            # A hash key serve para identificar os arquivos gerados em um mesmo processamento
            if not post.chave:
                hash_key = str(uuid.uuid4())[:20]
            else:
                hash_key = post.chave
            if request.FILES:
                # Verifica se todos os arquivos são PDF ou TXT antes de gravar
                for f in request.FILES.getlist('arquivo'):
                    filename, extensao = os.path.splitext(str(f))
                    if not (extensao == '.pdf' or extensao == '.txt'):
                        messages.error(request,
                                       'Extensão do arquivo %s inválida. Por favor selecione arquivos .txt ou .pdf' %
                                       filename)
                        return render(request, 'person_form.html', {'form': form, 'recaptcha': recaptcha})

                docs = []
                total_size = 0
                for f in request.FILES.getlist('arquivo'):
                    filename, extensao = os.path.splitext(str(f))
                    doc = Documento.objects.create(nome=post.nome, email=post.email, arquivo=f, tipo=post.tipo,
                                                   font_type=post.font_type, chave=hash_key)
                    docs.append(doc)
                    total_size += os.path.getsize(doc.arquivo.path)

                # se houver mais de um arquivo ou se o arquivo for PDF e maior que 5Mb,
                # a conversão será feita via thread
                if len(docs) > 1 or post.chave:
                    extra_filename = 'output/' + hash_key + '.txt'
                    try:
                        doc_final = Documento.objects.get(chave=hash_key, consolidado=True)
                    except Documento.DoesNotExist:
                        doc_final = Documento.objects.create(
                                        nome=post.nome, email=post.email, arquivo=extra_filename,
                                        tipo=post.tipo, chave=hash_key,
                                        font_type=post.font_type, status='P', consolidado=True)
                    conversao_pdf = True
                else:
                    doc_final = docs[0]
                    if extensao == '.txt':
                        conversao_pdf = False
                    else:
                        conversao_pdf = total_size > (10 * 1048576)
                        if not conversao_pdf:
                            pdf2txt(doc_final.arquivo.path)
                        else:
                            doc_final.status = 'P'
                            doc_final.save()

                if conversao_pdf:
                    pthread = ProcessThread(doc_final.id)
                    pthread.start()
                    return render(request, 'nuvem.html', {'allow_edit': False, 'doc': doc_final})
                else:
                    doc_final.status = 'F'
                    doc_final.save()
                    return custom_redirect('nuvem', doc_final.pk)
            else:
                messages.error(request, 'Nenhum arquivo enviado')

        else:
            messages.error(request, 'ReCAPTCHA inválido. Por favor tente novamente!')

    return render(request, 'person_form.html', {'form': form, 'recaptcha': recaptcha})


def custom_redirect(url_name, *args, **kwargs):
    from django.urls import reverse
    url = reverse(url_name, args=args)
    params = urllib.parse.urlencode(kwargs)
    return HttpResponseRedirect(url + "?%s" % params)


def nuvem(request, id):
    documento = Documento.objects.get(pk=id)
    if documento.status != 'F':
        return render(request, 'nuvem.html', {'allow_edit': False, 'doc': documento})

    form = LayoutForm(request.POST or None, request.FILES or None,
                      initial={
                          'descricao': documento.descritivo or None,
                          'font_type': documento.font_type,
                          'cores': documento.cores,
                          'select': documento.language
                      })

    allow_edit = documento.chave and request.GET.get('chave') and documento.chave == request.GET.get('chave')

    if request.POST:
        if form.is_valid():
            documento.descritivo = form.cleaned_data.get('descricao')
            if form.cleaned_data.get('imagem'):
                documento.imagem = form.cleaned_data.get('imagem')
            else:
                documento.imagem = None

            documento.font_type = form.cleaned_data.get('font_type')
            documento.stopwords = form.cleaned_data.get('stopwords')
            documento.cores = form.cleaned_data.get('cores')
            documento.language = form.cleaned_data.get('select')
            documento.save()
            messages.success(request, 'Alteração salva com sucesso.')

    nome_arquivo = documento.arquivo.path

    # if not os.path.exists(FONT_PATH + '\\' + documento.font_type):
    #    messages.error(request, 'A fonte escolhida não foi encontrada na pasta. Por favor veriricar a inslação da fonte. Path: %s' % (FONT_PATH + '\\' + documento.font_type))

    prefix, file_extension = os.path.splitext(nome_arquivo)  # prefix = (root,ext)
    if not os.path.exists(prefix + '.txt'):  # caso nao seja um arquivo txt
        pdf2txt(documento.arquivo.path)  # vamos converter de pdf para txt

    nome_arquivo = prefix + '.txt'
    # if os.path.exists(prefix + '.dedup'):                       #caso exista um arquivo.dedup
    #    os.rename(prefix + '.dedup', prefix + key + '.dedup')   #renomear usando a key

    numero_linhas = 50
    if not documento.language:
        try:
            num_linha = 0
            trecho = ''
            with open(nome_arquivo) as f:
                while num_linha < 50:
                    linha = f.readline().lower().strip()
                    if len(linha) > 3:
                        trecho += linha + ' '
                        num_linha += 1
        except UnicodeDecodeError as erro:
            linhas = open(nome_arquivo, encoding='ISO-8859-1').read().lower().split('.')[ 0:numero_linhas ]
            trecho = ' '.join([ ('' if len(linha) < numero_linhas else linha) for linha in linhas ])
        lang_detect = detectlanguage.detect(trecho)
        if len(lang_detect) > 0:
            precisao = lang_detect[ 0 ][ 'confidence' ]
            if precisao > 5:
                documento.language = lang_detect[ 0 ][ 'language' ]
                documento.save()
    mask = None
    channel = 0
    if documento.imagem:
        try:
            image = Image.open(documento.imagem)
            channel = len(image.split())
            mask = np.array(image)
        except Exception:
            messages.error(request, 'Não foi possivel usar a imagem como mascára, por favor selecione outra.')

    font_type = documento.font_type or 'Carlito-Regular.ttf'
    if not os.path.exists(os.path.join(settings.FONT_PATH, font_type)):
        messages.error(request,
                       'A fonte escolhida não foi encontrada na pasta. Por favor veriricar a inslação da fonte.')

    # if documento.font_type:
    #     try:
    #         os.path.exists(documento.font_type)
    #     except Exception:
    #         messages.error(request, 'A fonte escolhida não foi encontrada na pasta. Por favor veriricar a inslação da fonte.')

    # Fix error: Not Implement methods para imagens com menos de 3 canais.
    if channel >= 3 or not documento.cores:
        color = documento.cores
    else:
        messages.error(request, 'Não foi possivel pegar as cores dessa imagem, '
                                'pois ela possui somente %s %s.' % (channel, 'canais' if channel > 1 else 'canal'))
        color = False

    if documento.tipo == 'keywords':
        imagem = generate_words(nome_arquivo, documento.language, mask, color, font_type)
    else:
        imagem = generate(nome_arquivo, documento.stopwords, documento.language, mask, color, font_type)

    contexto = {
        'allow_edit': allow_edit,
        'form': form,
        'doc': documento,
        'nuvem': imagem
    }

    return render(request, 'nuvem.html', contexto)