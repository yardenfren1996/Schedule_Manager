# Generated by Django 3.1.7 on 2021-04-11 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_shifts', '0002_auto_20201116_0934'),
    ]

    operations = [
        migrations.AddField(
            model_name='shift',
            name='selected',
            field=models.BooleanField(default=0),
        ),
    ]
