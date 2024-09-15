# Generated by Django 5.1.1 on 2024-09-15 13:45

import django.db.models.deletion
import django_tenants.postgresql_backend.base
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('schema_name', models.CharField(db_index=True, max_length=63, unique=True, validators=[django_tenants.postgresql_backend.base._check_schema_name])),
                ('name', models.CharField(help_text='name of the client', max_length=100)),
                ('organisation_code', models.CharField(blank=True, max_length=128, null=True, unique=True)),
                ('on_trial', models.BooleanField(default=True, verbose_name='designate whether the user is on trial on not')),
                ('created_on', models.DateField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('paid_until', models.DateField(blank=True, default=None, null=True)),
                ('country', models.CharField(blank=True, max_length=150, null=True)),
                ('city', models.CharField(blank=True, max_length=150, null=True)),
                ('address_line1', models.CharField(blank=True, max_length=150, null=True)),
                ('address_line2', models.CharField(blank=True, max_length=150, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.CharField(db_index=True, max_length=253, unique=True)),
                ('is_primary', models.BooleanField(db_index=True, default=True)),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='domains', to='clients.client')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
