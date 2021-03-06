# Generated by Django 3.2.7 on 2021-10-26 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bill', '0002_alter_billattachment_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='billsubscriber',
            name='amount_paid',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='Amount paid'),
        ),
        migrations.AlterField(
            model_name='bill',
            name='type',
            field=models.CharField(choices=[('food', 'Food'), ('shopping', 'Shopping'), ('entertainment', 'Entertainment'), ('outing', 'Outing'), ('miscelleneous', 'Miscellaneous')], default='miscelleneous', max_length=254, verbose_name='Bill type'),
        ),
    ]
