from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

# 👇 1. إنشاء استمارة مخصصة لتعديل العميل
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'

# 👇 2. إنشاء استمارة مخصصة لإضافة عميل جديد
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email',)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User Admin."""

    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number', 'profile_picture')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Additional info', {'fields': ('username', 'role', 'is_email_verified')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'role', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('-date_joined',)

    readonly_fields = ('date_joined', 'last_login')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Profile Admin."""

    # 👇 التعديل هنا: استبدلنا city و country بـ governorate و area
    list_display = ('user', 'governorate', 'area', 'created_at')
    
    # 👇 التعديل هنا: تحديث حقول البحث لتعتمد على العنوان الجديد
    search_fields = ('user__email', 'governorate', 'area', 'street_address')
    
    readonly_fields = ('created_at', 'updated_at')