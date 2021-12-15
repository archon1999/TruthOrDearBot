# Generated by Django 3.2 on 2021-12-11 17:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0002_auto_20211211_2142'),
    ]

    operations = [
        migrations.AddField(
            model_name='gameplayer',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='players', to='backend.botuser', verbose_name='Пользователь'),
            preserve_default=False,
        ),
    ]