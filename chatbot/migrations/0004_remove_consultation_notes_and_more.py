# Generated by Django 5.1.5 on 2025-01-20 07:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0003_patient_current_disease_patient_current_hospital_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='consultation',
            name='notes',
        ),
        migrations.RemoveField(
            model_name='consultation',
            name='severity',
        ),
        migrations.RemoveField(
            model_name='consultation',
            name='symptoms',
        ),
    ]
