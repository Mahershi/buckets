from django.contrib import admin
from .models import User, UserBucket, Bucket, Access, BucketField, FieldType
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email',)}),
        (_('Personal Info'), {'fields': ('name',)}),
        (_('Permission'), {'fields': ('is_superuser',)}),
    )

    add_fieldsets = (
        (None, {'fields': ('email', 'password1', 'password2',)}),
        (_('Personal Info'), {'fields': ('name',)}),
        (_('Permission'), {'fields': ('is_superuser', 'is_staff',)}),
    )

    list_display = ('id', 'name', 'email',)
    list_filter = ('is_superuser', 'is_staff',)
    filter_horizontal = ()
    search_fields = ('name', 'email',)
    ordering = ('name',)


@admin.register(Bucket)
class BucketAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('name', 'created_at',)}),
    )

    add_fieldsets = (
        (None, {'fields': ('name',)}),
    )

    list_display = ('id', 'name', 'created_at',)
    list_filter = ()
    filter_horizontal = ()
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(UserBucket)
class UserBucketAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('bucket', 'user', 'access', 'joined_at')}),
    )

    add_fieldsets = (
        (None, {'fields': ('bucket', 'user', 'access', 'joined_at')}),
    )

    list_display = ('id', 'bucket', 'user', 'access', 'joined_at')
    list_filter = ('bucket', 'user', 'access')
    filter_horizontal = ()
    search_fields = ('bucket', 'user')
    ordering = ('bucket', 'user')


@admin.register(Access)
class AccessAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('type', )}),
    )

    add_fieldsets = (
        (None, {'fields': ('type', )}),
    )

    list_display = ('id', 'type',)
    list_filter = ()
    filter_horizontal = ()
    search_fields = ()
    ordering = ('type', )

@admin.register(FieldType)
class FieldTypeAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('type', )}),
    )

    add_fieldsets = (
        (None, {'fields': ('type', )}),
    )

    list_display = ('id', 'type',)
    list_filter = ()
    filter_horizontal = ()
    search_fields = ()
    ordering = ('type', )


@admin.register(BucketField)
class BucketFieldAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('bucket', 'key', 'type', 'value', 'created_at')}),
    )

    add_fieldsets = (
        (None, {'fields': ('bucket', 'key', 'type', 'value', 'created_at')}),
    )

    list_display = ('id', 'bucket', 'key', 'value', 'type', 'created_at')
    list_filter = ('type', 'bucket',)
    filter_horizontal = ()
    search_fields = ()
    ordering = ('key', )
