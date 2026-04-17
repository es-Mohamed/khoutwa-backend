from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    # 1. شيلنا read_only=True عشان نسمح بالتعديل
    governorate = serializers.CharField(source='profile.governorate', required=False, allow_blank=True)
    area = serializers.CharField(source='profile.area', required=False, allow_blank=True)
    street_address = serializers.CharField(source='profile.street_address', required=False, allow_blank=True)
    
    # 2. خلينا name يستقبل التعديل (write_only) ونرد بـ full_name للقراءة
    name = serializers.CharField(write_only=True, required=False)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'name', 'full_name', 'first_name', 'last_name', 'phone_number', 
                  'profile_picture', 'role', 'is_active', 'is_email_verified', 'date_joined',
                  'governorate', 'area', 'street_address')
        read_only_fields = ('id', 'date_joined', 'is_email_verified', 'role', 'is_active', 'email')

    def update(self, instance, validated_data):
        # 3. فصل بيانات البروفايل (العنوان) عن بيانات اليوزر الأساسية
        profile_data = validated_data.pop('profile', {})
        
        # 4. لو بعت اسم جديد، نفصله لاسم أول واسم أخير زي ما عملنا في الإنشاء
        name = validated_data.pop('name', None)
        if name:
            name_parts = name.strip().split(' ', 1)
            instance.first_name = name_parts[0]
            instance.last_name = name_parts[1] if len(name_parts) > 1 else ''

        # 5. تحديث بيانات اليوزر الأساسية (زي رقم التليفون)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 6. تحديث بيانات العنوان في جدول الـ Profile
        if hasattr(instance, 'profile'):
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users."""

    password = serializers.CharField(write_only=True, min_length=8)
    re_password = serializers.CharField(write_only=True, min_length=8)
    
    # حقول إضافية هنستقبلها من الفرونت إند ومش موجودة بشكل مباشر في موديل اليوزر
    name = serializers.CharField(write_only=True, required=True)
    governorate = serializers.CharField(write_only=True, required=False, allow_blank=True)
    area = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        # شيلنا username لأنه مش مطلوب، وضيفنا الحقول الجديدة
        fields = ('email', 'password', 're_password', 'name', 'phone_number', 'governorate', 'area')

    def validate(self, attrs):
        """Validate passwords match."""
        password = attrs.get('password')
        re_password = attrs.pop('re_password', None)

        if password != re_password:
            raise serializers.ValidationError({'re_password': 'Passwords do not match.'})

        return attrs

    def create(self, validated_data):
        """Create user with hashed password and update profile."""
        
        # 1. استخراج الحقول الإضافية قبل إنشاء المستخدم
        name = validated_data.pop('name', '')
        governorate = validated_data.pop('governorate', '')
        area = validated_data.pop('area', '')
        
        # 2. تقسيم الاسم الكامل إلى اسم أول واسم أخير
        name_parts = name.strip().split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        validated_data['first_name'] = first_name
        validated_data['last_name'] = last_name

        # 3. إنشاء المستخدم (دالة create_user هتشفر الباسورد)
        user = User.objects.create_user(**validated_data)
        
        # 4. تحديث البروفايل (الذي تم إنشاؤه تلقائياً بواسطة signals.py) ببيانات العنوان
        if hasattr(user, 'profile'):
            user.profile.governorate = governorate
            user.profile.area = area
            user.profile.save()
            
        return user


