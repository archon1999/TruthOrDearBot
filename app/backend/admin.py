from django.contrib import admin
from django import forms

from ckeditor.widgets import CKEditorWidget

from backend.models import (BotUser, Chat, Game,
                            Task, Template, GamePlayer)


class TemplateAdminForm(forms.ModelForm):
    body_ru = forms.CharField(widget=CKEditorWidget(), label='На русском')
    body_en = forms.CharField(widget=CKEditorWidget(), label='На английском')


@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'chat_id', 'first_name']
    search_fields = ['first_name', 'last_name', 'username']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'type', 'body_ru']
    list_filter = ['type']


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ['id', 'chat_id', 'title']
    search_fields = ['title']


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['id', 'chat']


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    form = TemplateAdminForm
    list_display = ['id', 'title', 'type']


@admin.register(GamePlayer)
class GamePlayerAdmin(admin.ModelAdmin):
    pass
