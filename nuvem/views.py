import json
import os
import sys
import urllib
import uuid
from datetime import datetime
from threading import Thread

import detectlanguage
import numpy as np
from PIL import Image
from chunked_upload.constants import http_status
from chunked_upload.exceptions import ChunkedUploadError
from chunked_upload.views import ChunkedUploadView, ChunkedUploadCompleteView
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render

from gerador.genwordcloud import generate, generate_words
from gerador.pdf2txt import pdf2txt
from nuvem.forms import DocumentoForm, LayoutForm, UploadForm
from nuvem.models import Documento

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


def custom_redirect(url_name, *args, **kwargs):
    from django.urls import reverse
    url = reverse(url_name, args=args)
    params = urllib.parse.urlencode(kwargs)
    return HttpResponseRedirect(url + "?%s" % params)


def nuvem(request, id):
    documento = Documento.objects.get(pk=id)
    if documento.status != 'F':
        return render(request, 'nuvem.html', {'allow_edit': False, 'doc': documento})

    nome_arquivo = documento.arquivo.path
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
            linhas = open(nome_arquivo, encoding='ISO-8859-1').read().lower().split('.')[0:numero_linhas]
            trecho = ' '.join([('' if len(linha) < numero_linhas else linha) for linha in linhas])
        lang_detect = detectlanguage.detect(trecho)
        if len(lang_detect) > 0:
            precisao = lang_detect[0]['confidence']
            if precisao > 5:
                documento.language = lang_detect[0]['language']
                documento.save()

    form = LayoutForm(request.POST or None, request.FILES or None,
                      initial={
                          'descricao': documento.descritivo or None,
                          'font_type': documento.font_type,
                          'cores': documento.cores,
                          'language': documento.language
                      })

    colormap = None
    allow_edit = documento.chave and request.GET.get('chave') and documento.chave == request.GET.get('chave')

    if request.POST:
        if form.is_valid():
            documento.descritivo = form.cleaned_data.get('descricao')
            colormap = form.cleaned_data.get('colormap')
            if form.cleaned_data.get('imagem'):
                documento.imagem = form.cleaned_data.get('imagem')
                documento.cores = form.cleaned_data.get('cores')
            else:
                documento.imagem = None
                documento.cores = False

            documento.font_type = form.cleaned_data.get('font_type')
            documento.stopwords = form.cleaned_data.get('stopwords')
            documento.language = form.cleaned_data.get('language')
            documento.save()
            messages.success(request, 'Alteração salva com sucesso.')

    mask = None
    channel = 0
    if documento.imagem:
        try:
            image = Image.open(documento.imagem)
            channel = len(image.split())
            mask = np.array(image)
        except:
            messages.error(request, 'Não foi possivel usar a imagem como mascára, por favor selecione outra.')

    font_type = documento.font_type or 'Carlito-Regular.ttf'
    if not os.path.exists(os.path.join(settings.FONT_PATH, font_type)):
        messages.error(request,
                       'A fonte escolhida não foi encontrada na pasta. Por favor verificar a instalação da fonte.')

    # Fix error: Not Implement methods para imagens com menos de 3 canais.
    if channel >= 3 or not documento.cores:
        color = documento.cores
    else:
        messages.error(request, 'Não foi possivel obter as cores dessa imagem, '
                                'pois ela possui somente %s %s.' % (channel, 'canais' if channel > 1 else 'canal'))
        color = False

    if documento.tipo == 'keywords':
        imagem = generate_words(nome_arquivo, documento.language, mask, color, font_type, colormap)
    else:
        imagem = generate(nome_arquivo, documento.stopwords, documento.language, mask, color, font_type, colormap)

    contexto = {
        'allow_edit': allow_edit,
        'form': form,
        'doc': documento,
        'nuvem': imagem
    }

    return render(request, 'nuvem.html', contexto)


def new_doc_test_size(request):
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


def new_doc(request):
    recaptcha = getattr(settings, "GOOGLE_RECAPTCHA_PUBLIC_KEY", None)
    chave_nome = 'documento-nome-pesquisador'
    chave_email = 'documento-email-pesquisador'

    if request.method == 'GET':
        initial = {
            'nome': request.COOKIES.get(chave_nome),
            'email': request.COOKIES.get(chave_email)
        }
        form = DocumentoForm(initial=initial)
    else:
        form = DocumentoForm(request.POST, request.FILES)

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
                key = str(uuid.uuid4())
                key = key[:20]
                if request.FILES:
                    if post.tipo == 'keywords':
                        url_filename = os.path.join('output', post.arquivo.name)
                        doc = Documento.objects.create(nome=post.nome, email=post.email, arquivo=url_filename,
                                                       tipo=post.tipo, chave=key, status='F')

                        return custom_redirect('nuvem', doc.pk, chave=key)
                    else:
                        # Verifica se todos os arquivos são PDF ou TXT antes de gravar
                        for f in request.FILES.getlist('arquivo'):
                            filename, extensao = os.path.splitext(str(f))
                            if not (extensao == '.pdf' or extensao == '.txt'):
                                messages.error(request,
                                               f'Extensão do arquivo {filename} inválida. '
                                               'Por favor selecione arquivos .txt ou .pdf')
                                return render(request, 'person_form.html', {'form': form, 'recaptcha': recaptcha})

                        docs = []
                        for f in request.FILES.getlist('arquivo'):
                            filename, extensao = os.path.splitext(str(f))
                            doc = Documento.objects.create(nome=post.nome, email=post.email, arquivo=f, tipo=post.tipo,
                                                           chave=key)
                            if extensao == '.pdf':
                                pdf2txt(doc.arquivo.path)
                            docs.append(doc)

                        if len(docs) > 1:
                            extra_filename = str(uuid.uuid4()) + '.txt'
                            extra_file = open(os.path.join(settings.MEDIA_ROOT, 'output', extra_filename), 'w+')
                            for doc in docs:
                                filename, extensao = os.path.splitext(doc.arquivo.path)
                                with open(filename + '.txt', 'r') as f:
                                    extra_file.write(f.read())
                                    extra_file.write('\n')
                            extra_file.close()
                            extra_filename = os.path.join('output', extra_filename)
                            doc_extra = Documento.objects.create(nome=post.nome, email=post.email,
                                                                 arquivo=extra_filename,
                                                                 tipo=post.tipo, chave=key, status='F')
                            response = custom_redirect('nuvem', doc_extra.pk, chave=key)
                        else:
                            doc.status = 'F'
                            doc.save()
                            response = custom_redirect('nuvem', doc.pk, chave=key)

                        response.set_cookie(chave_nome, form.cleaned_data['nome'], max_age=2592000)
                        response.set_cookie(chave_email, form.cleaned_data['email'], max_age=2592000)

                        return response
                else:
                    messages.error(request, 'Nenhum arquivo enviado')

            else:
                messages.error(request, 'ReCAPTCHA inválido. Por favor tente novamente!')

    return render(request, 'person_form.html', {'form': form, 'recaptcha': recaptcha})


class NuvemUploadView(ChunkedUploadView):
    field_name = 'arquivo'  # Nome do campo do formulário onde o arquivo será enviado

    def check_permissions(self, request):
        # Permite que usuários não autenticados façam upload
        pass

    def validate(self, request):
        form = UploadForm(request.POST, request.FILES)

        if not form.is_valid():
            raise ChunkedUploadError(status=http_status.HTTP_400_BAD_REQUEST,
                                     errors=form.errors.as_json())


class NuvemUploadCompleteView(ChunkedUploadCompleteView):

    def on_completion(self, uploaded_file, request):
        # Lógica a ser executada quando o upload for concluído
        Documento.objects.create(nome='ND', email='ND', arquivo=uploaded_file)
        chunked_upload_obj = self.model.objects.get(upload_id=request.POST.get('upload_id'))
        chunked_upload_obj.delete()

    def get_response_data(self, chunked_upload, request):
        return {'message': ("You successfully uploaded '%s' (%s bytes)!" %
                            (chunked_upload.filename, chunked_upload.offset))}

    def check_permissions(self, request):
        # Permite que usuários não autenticados façam upload
        pass


def transcribe(request):
    return render(request, 'trascribe.html', {'form': UploadForm()})
