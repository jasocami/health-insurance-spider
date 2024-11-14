# Generated by Django 3.1.7 on 2021-04-08 15:28

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('healthy_spider_records', '0003_smartsalusrecord'),
    ]

    operations = [
        migrations.CreateModel(
            name='IglobalmedRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(blank=True, max_length=128, null=True)),
                ('speciality_name', models.CharField(blank=True, max_length=256, null=True)),
                ('pvp', models.CharField(blank=True, max_length=64, null=True)),
                ('pvp_middle', models.CharField(blank=True, max_length=64, null=True)),
                ('pvp_full', models.CharField(blank=True, max_length=64, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('center', models.CharField(blank=True, max_length=256, null=True)),
                ('province_name', models.CharField(blank=True, max_length=64, null=True)),
                ('city', models.CharField(blank=True, max_length=64, null=True)),
                ('town', models.CharField(blank=True, max_length=64, null=True)),
                ('includes', models.TextField(blank=True, null=True)),
                ('excludes', models.TextField(blank=True, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('health_registration', models.CharField(blank=True, max_length=60, null=True)),
                ('url', models.URLField(blank=True, max_length=300, null=True)),
                ('latitude', models.CharField(blank=True, max_length=30, null=True)),
                ('longitude', models.CharField(blank=True, max_length=30, null=True)),
                ('creation_timestamp', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('last_update_timestamp', models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]
