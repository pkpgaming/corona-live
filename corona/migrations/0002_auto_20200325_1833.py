# Generated by Django 3.0.4 on 2020-03-25 18:33

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('corona', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cache',
            name='created_on',
        ),
        migrations.AddField(
            model_name='cache',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cache',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
