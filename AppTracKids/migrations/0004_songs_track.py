# Generated by Django 4.2.7 on 2023-12-03 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AppTracKids', '0003_songs'),
    ]

    operations = [
        migrations.AddField(
            model_name='songs',
            name='track',
            field=models.TextField(default=''),
        ),
    ]