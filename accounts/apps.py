from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    # 👇 الدالة دي بتشتغل أول ما السيرفر يقوم، وبنستخدمها عشان نفعّل الـ Signals
    def ready(self):
        import accounts.signals # تأكد من استيراد ملف signals عشان يتم تفعيل الإشارات