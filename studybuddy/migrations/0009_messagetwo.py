# Generated by Django 3.2.12 on 2022-04-21 17:44

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('studybuddy', '0008_profile_courses'),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageTwo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sent_by', models.CharField(default='', max_length=100)),
                ('message', models.CharField(max_length=100)),
                ('to', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
