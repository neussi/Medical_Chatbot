# Generated by Django 3.2.8 on 2025-01-17 02:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disease',
            name='symptoms',
            field=models.ManyToManyField(related_name='diseases', to='chatbot.Symptom'),
        ),
    ]
