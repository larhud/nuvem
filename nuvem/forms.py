from http.client import FOUND
import os
import re

from django import forms
from django.conf import settings
from django.forms import ModelForm

from larhud.settings import FONT_PATH, FONT_NAME
from .models import Documento, TYPES, TYPES_LANG, TYPES_FONT


class DocumentoForm(ModelForm):

    tipo = forms.ChoiceField(choices=TYPES, required=True)
    font_type = forms.ChoiceField(choices=TYPES_FONT, required=True)

    class Media:
        js = ('js/validation.js',)

    class Meta:
        model = Documento
        fields = ['nome', 'email', 'tipo', 'font_type', 'arquivo',]

    def clean_arquivo(self):
        files = self.files.getlist('arquivo')
        tipo = self.cleaned_data.get('tipo')
        font_type = self.cleaned_data.get('font_type')
        for file in files:
            extension = os.path.splitext(file.name)[1]
            if extension != '.txt' and extension != '.pdf':
                self.add_error('arquivo',
                               'Extensão %s do arquivo %s inválida. Somente arquivos de textos e PDF '
                               'são permitidos.' % (extension, file.name))

            if tipo == 'keywords' and extension != '.txt':
                self.add_error('arquivo', 'Extensão %s do arquivo %s inválida. Somente arquivos .txt '
                                          'são permitidos para esse tipo de arquivo.' % (extension, file.name))
            return self.cleaned_data.get('arquivo')

    #Documento.objects.create(numero='1111', #tipo=Documento.font_type)

    font_name = Documento.objects.last()
    font_name_gwc = ''

    if font_name.font_type == Documento.font_type:
        if Documento.font_type == 'Carlito-Regular.ttf':
            font_name_gwc = 'Carlito-Regular.ttf'

    elif font_name.font_type == Documento.font_type:
        if Documento.font_type == 'Comfortaa Bold.ttf':
            font_name_gwc = 'Comfortaa Bold.ttf'

    elif font_name.font_type == Documento.font_type:
        if Documento.font_type == 'Cooper Regular.ttf':
            font_name_gwc = 'Cooper Regular.ttf'

    elif font_name.font_type == Documento.font_type:
        if Documento.font_type == 'Dyuthi.ttf':
            font_name_gwc = 'Dyuthi.ttf'

    elif font_name.font_type == Documento.font_type:
        if Documento.font_type == 'Lato-Regular.ttf':
            font_name_gwc = 'Lato-Regular.ttf'

    elif font_name.font_type == Documento.font_type:
        if Documento.font_type == 'Poppins-Regular.ttf':
            font_name_gwc = 'Poppins-Regular.ttf'


class LayoutForm(forms.Form):
    imagem = forms.FileField(widget=forms.FileInput(
        attrs=(
            {'class': 'custom-file-input', 'id': 'inputGroupFile01', 'aria-describedby': 'inputGroupFileAddon01'}
        )), label='Imagem:', required=False)
    select = forms.ChoiceField(label='Selecione o idioma:',choices=TYPES_LANG, required=True)

    descricao = forms.CharField(widget=forms.Textarea(attrs={'rows': 4,}),
                                label='Descrição:', required=False)
    stopwords = forms.CharField(widget=forms.Textarea(attrs={'rows': 4,}),
                                label='Adicione mais stopwords (separando-as por ","):', required=False)
    # min_size = forms.IntegerField(widget=forms.IntegerField(), label='Frequência mínima:', initial=2)
    cores = forms.BooleanField(widget=forms.CheckboxInput,
                               label='Cores da Imagem', required=False)

