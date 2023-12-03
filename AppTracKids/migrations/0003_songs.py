# Generated by Django 4.2.7 on 2023-12-03 07:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AppTracKids', '0002_project'),
    ]

    operations = [
        migrations.CreateModel(
            name='Songs',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('titulo', models.TextField(default='')),
                ('artista', models.TextField(default='')),
                ('info', models.TextField(default='')),
                ('imagen', models.TextField(default='')),
                ('vocals', models.TextField(default='')),
                ('other', models.TextField(default='')),
                ('drums', models.TextField(default='')),
                ('bass', models.TextField(default='')),
            ],
        ),
    ]
