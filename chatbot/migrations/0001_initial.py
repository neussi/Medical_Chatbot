# Generated by Django 3.2.8 on 2025-01-12 17:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Hospital',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('address', models.TextField()),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('phone', models.CharField(max_length=20)),
                ('specialties', models.TextField()),
                ('emergency', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(max_length=20, unique=True)),
                ('name', models.CharField(blank=True, max_length=100)),
                ('language', models.CharField(default='fr', max_length=2)),
                ('age', models.IntegerField(null=True)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female')], max_length=1, null=True)),
                ('location_latitude', models.FloatField(null=True)),
                ('location_longitude', models.FloatField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('conversation_state', models.CharField(default='initial', max_length=50)),
                ('current_symptoms', models.TextField(default='')),
            ],
        ),
        migrations.CreateModel(
            name='Symptom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_fr', models.CharField(max_length=100)),
                ('name_en', models.CharField(max_length=100)),
                ('description_fr', models.TextField()),
                ('description_en', models.TextField()),
                ('keywords_fr', models.TextField(blank=True)),
                ('keywords_en', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('specialty', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=20)),
                ('languages', models.CharField(max_length=200)),
                ('available', models.BooleanField(default=True)),
                ('hospital', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chatbot.hospital')),
            ],
        ),
        migrations.CreateModel(
            name='Disease',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_fr', models.CharField(max_length=100)),
                ('name_en', models.CharField(max_length=100)),
                ('description_fr', models.TextField()),
                ('description_en', models.TextField()),
                ('severity', models.IntegerField(choices=[(1, 'Légère'), (2, 'Modérée'), (3, 'Sévère'), (4, 'Critique')])),
                ('symptoms', models.ManyToManyField(to='chatbot.Symptom')),
            ],
        ),
        migrations.CreateModel(
            name='Consultation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('severity', models.IntegerField(choices=[(1, 'Légère'), (2, 'Modérée'), (3, 'Sévère'), (4, 'Critique')], default=1)),
                ('disease', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='chatbot.disease')),
                ('doctor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='chatbot.doctor')),
                ('hospital', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='chatbot.hospital')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chatbot.patient')),
                ('symptoms', models.ManyToManyField(to='chatbot.Symptom')),
            ],
        ),
    ]
