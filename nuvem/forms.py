from http.client import FOUND
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from django import forms
from django.conf import settings
from django.forms import ModelForm

from larhud.settings import FONT_PATH
from .models import Documento, TYPES, TYPES_LANG, TYPES_FONT


class DocumentoForm(ModelForm):
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


class LayoutForm(forms.Form):
    imagem = forms.FileField(widget=forms.FileInput(
        attrs=(
            {'class': 'custom-file-input', 'id': 'inputGroupFile01', 'aria-describedby': 'inputGroupFileAddon01'}
        )), label='Imagem:', required=False)
    select = forms.ChoiceField(label='Selecione o idioma:',choices=TYPES_LANG, required=True)
    font_type = forms.ChoiceField(label= 'Selecione a fonte:',choices=TYPES_FONT, required=True)
    descricao = forms.CharField(widget=forms.Textarea(attrs={'rows': 4,}),
                                label='Descrição:', required=False)
    stopwords = forms.CharField(widget=forms.Textarea(attrs={'rows': 4,}),
                                label='Adicione mais stopwords (separando-as por ","):', required=False)
    # min_size = forms.IntegerField(widget=forms.IntegerField(), label='Frequência mínima:', initial=2)
    cores = forms.BooleanField(widget=forms.CheckboxInput,
                               label='Cores da Imagem', required=False)

