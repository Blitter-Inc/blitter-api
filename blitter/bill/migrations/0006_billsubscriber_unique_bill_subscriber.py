# Generated by Django 3.2.7 on 2021-12-08 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bill', '0005_auto_20211110_1203'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='billsubscriber',
            constraint=models.UniqueConstraint(fields=('bill', 'user'), name='unique_bill_subscriber'),
        ),
    ]
