from django.urls import path
from .views import new_doc
from .views import nuvem, transcribe, NuvemUploadView, NuvemUploadCompleteView

urlpatterns = [
    path('', new_doc, name="new_doc"),
    path('nuvem/<int:id>', nuvem, name="nuvem"),
    path('transcribe/', transcribe, name="transcribe"),
    path('nuvem-upload/', NuvemUploadView.as_view(), name="nuvem_upload"),
    path('nuvem-upload-completo/', NuvemUploadCompleteView.as_view(), name="nuvem_upload_completo"),
]
