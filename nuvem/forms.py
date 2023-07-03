import os

from django import forms
from django.conf import settings
from django.forms import ModelForm
from django.utils.safestring import mark_safe

from .models import Documento, TYPES, TYPES_LANG, TYPES_FONT


class DocumentoForm(ModelForm):
    tipo = forms.ChoiceField(label='Tipo de Arquivo', choices=TYPES, required=True)
    font_type = forms.ChoiceField(label='Tipo da Fonte', choices=TYPES_FONT, required=True)
    chave = forms.CharField(label='Chave de Acesso (Opcional)', required=False)

    class Media:
        js = ('js/validation.js',)

    class Meta:
        model = Documento
        fields = ['nome', 'email', 'tipo', 'font_type', 'arquivo', 'chave']

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


colormap_url = 'https://www.kaggle.com/code/niteshhalai/wordcloud-colormap'


class LayoutForm(forms.Form):
    language = forms.ChoiceField(label='Selecione o idioma:', choices=TYPES_LANG, required=True)
    font_type = forms.ChoiceField(label='Selecione a fonte:', choices=TYPES_FONT, required=True)
    colormap = forms.CharField(
        label='Mapa de Cores', required=False,
        help_text=mark_safe(f"Visualize os mapas possíveis <a href='{colormap_url}' target='_blank'>aqui</a>"))
    descricao = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}),
                                label='Descrição:', required=False)
    stopwords = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}),
                                label='Adicione mais stopwords (separando-as por ","):', required=False)
    # min_size = forms.IntegerField(widget=forms.IntegerField(), label='Frequência mínima:', initial=2)
    imagem = forms.FileField(widget=forms.FileInput(
        attrs=(
            {'class': 'custom-file-input', 'id': 'inputGroupFile01', 'aria-describedby': 'inputGroupFileAddon01'}
        )), label='Imagem:', required=False)
    cores = forms.BooleanField(widget=forms.CheckboxInput,
                               label='Utilizar as cores da Imagem', required=False)


class UploadForm(DocumentoForm):
    arquivo = forms.FileField(label='Arquivo em PDF ou Texto', widget=forms.FileInput(attrs={'accept': '.txt,.pdf'}))

    class Meta(DocumentoForm.Meta):
        fields = ['arquivo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ['tipo', 'font_type', 'chave']:
            self.fields[name].widget = forms.HiddenInput()
            self.fields[name].required = False
