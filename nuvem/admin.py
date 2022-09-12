from django.contrib import admin
from nuvem.models import Documento


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    fields = (('nome', 'email'), ('arquivo', 'tamanho'), ('language', 'tipo', 'font_type'), 'descritivo', 'stopwords', 'chave', 'cores', 'consolidado', 'status')
    list_display = ('nome', 'email', 'arquivo', 'consolidado', 'status')
    readonly_fields = ['pdf_link', 'tamanho']