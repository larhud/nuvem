from http.client import FOUND
import os
import re

from django import forms
from django.conf import settings
from django.forms import ModelForm

from larhud.settings import FONT_PATH
from .models import Documento, TYPES, TYPES_LANG

TYPES_FONT = [
    ('Carlito-Regular.ttf', 'Carlito'),
    ('Comfortaa Bold.ttf', 'Comfortaa-Bold'),
    ('Cooper Regular.ttf', 'Cooper'),
    ('Dyuthi.ttf', 'Dyuthi'),
    ('Lato-Regular.ttf', 'Lato-Regular'),
    ('Poppins-Regular.ttf', 'Poppins')
]


class DocumentoForm(ModelForm):
    FONT_NAME = ''
    tipo = forms.ChoiceField(choices=TYPES, required=True)
    font_type = forms.ChoiceField(choices=TYPES_FONT, required=True)

    class Media:
        js = ('js/validation.js',)

    class Meta:
        model = Documento
        fields = ['nome', 'email', 'tipo', 'font_type', 'arquivo']

        # widgets = {
        #     'font_type': forms.Select(choices=TYPES_FONT, attrs={'class': 'form-control'})
        # }

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
            
            if font_type == 'Carlito-Regular.ttf':
                DocumentoForm.FONT_NAME = 'Carlito-Regular.ttf'

            elif font_type == 'Comfortaa Bold.ttf':
                DocumentoForm.FONT_NAME = 'Comfortaa Bold.ttf'

            elif font_type == 'Cooper Regular.ttf':
                DocumentoForm.FONT_NAME = 'Cooper Regular.ttf'

            elif font_type == 'Dyuthi.ttf':
                DocumentoForm.FONT_NAME = 'Dyuthi.ttf'

            elif font_type == 'Lato-Regular.ttf':
                DocumentoForm.FONT_NAME = 'Lato-Regular.ttf'

            elif font_type == 'Poppins-Regular.ttf':
                DocumentoForm.FONT_NAME = 'Poppins-Regular.ttf'

            return self.cleaned_data.get('arquivo')



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

