# Generated by Django 3.1.8 on 2021-04-21 09:29

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('healthy_spider_records', '0007_bonomedicorecord'),
    ]

    operations = [
        migrations.CreateModel(
            name='PortalsaludSanitasRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.TextField(blank=True, null=True)),
                ('speciality_name', models.CharField(blank=True, max_length=256, null=True)),
                ('pvp', models.CharField(blank=True, max_length=64, null=True)),
                ('pvp_full', models.TextField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('center', models.TextField(blank=True, null=True)),
                ('province_name', models.CharField(blank=True, max_length=64, null=True)),
                ('includes', models.TextField(blank=True, null=True)),
                ('excludes', models.TextField(blank=True, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('gender', models.CharField(blank=True, choices=[('F', 'Mujer'), ('M', 'Hombre')], max_length=1, null=True)),
                ('url', models.URLField(blank=True, max_length=300, null=True)),
                ('creation_timestamp', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('last_update_timestamp', models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]