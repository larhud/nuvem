from django.contrib import admin
from nuvem.models import Documento
from gerador.pdf2txt import pdf2txt

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'arquivo', 'consolidado', 'status')
    readonly_fields = ['pdf_link']

    actions = ('recreate_cloud', )

    def recreate_cloud(self, request, queryset):
        num_oper = 0
        for rec in queryset:
            pdf2txt(rec.arquivo.path)
            rec.status = 'F'
            rec.save()
            num_oper += 1
        self.message_user(request, 'Documentos renderizados: %d ' % num_oper)

    recreate_cloud.short_description = 'Renderiza Nuvem'
