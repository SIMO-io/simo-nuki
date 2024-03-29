# Generated by Django 3.2.9 on 2024-01-22 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simo_nuki', '0006_auto_20231011_0823'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nukidevice',
            name='firmware_version',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='nukidevice',
            name='last_state',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='nukidevice',
            name='name',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='nukidevice',
            name='type',
            field=models.PositiveIntegerField(choices=[(0, 'smartlock - Nuki Smart Lock 1.0/2.0'), (2, 'opener - Nuki Opener'), (3, 'smartdoor - Nuki Smart Door'), (4, 'smartlock3 - Nuki Smart Lock 3.0 (Pro)')], default=4),
        ),
    ]
