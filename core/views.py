from rest_framework import generics, permissions
from .models import SiteSettings
from .serializers import SiteSettingsSerializer

class SiteSettingsRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = SiteSettingsSerializer
    # 👈 الأدمين بس هو اللي يقدر يشوف ويعدل الإعدادات
    permission_classes = [permissions.IsAdminUser] 

    def get_object(self):
        # 👈 السحر هنا: بنقول لجانجو هات أول إعداد في الداتابيز، ولو مش موجود اعمله!
        # ده بيضمن إن دايماً عندنا صف واحد بس للإعدادات (Singleton)
        obj, created = SiteSettings.objects.get_or_create(id=1)
        return obj