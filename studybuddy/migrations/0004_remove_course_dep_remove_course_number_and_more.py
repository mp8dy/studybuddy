# Generated by Django 4.0.2 on 2022-04-01 01:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studybuddy', '0003_course'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='dep',
        ),
        migrations.RemoveField(
            model_name='course',
            name='number',
        ),
        migrations.AddField(
            model_name='course',
            name='courseName',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='courses',
            field=models.ManyToManyField(blank=True, to='studybuddy.Course'),
        ),
    ]
