# Generated by Django 2.0.5 on 2018-05-19 22:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vertical', '0003_result_url_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='result',
            name='url_id',
            field=models.BigIntegerField(default=1526739711986.774, max_length=32, unique=True),
        ),
    ]
