# Generated by Django 2.2.2 on 2019-06-25 01:39

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('interface', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Strategy_pnl',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('str_name', models.CharField(default='未输入策略名', max_length=10)),
                ('pnl', models.CharField(default='', max_length=6)),
                ('updated_time', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]
