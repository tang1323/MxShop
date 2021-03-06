# Generated by Django 2.2 on 2021-03-16 22:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_operation', '0003_auto_20210315_1056'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraddress',
            name='city',
            field=models.CharField(default='', max_length=100, verbose_name='城市'),
        ),
        migrations.AddField(
            model_name='useraddress',
            name='province',
            field=models.CharField(default='', max_length=100, verbose_name='省份'),
        ),
        migrations.AlterField(
            model_name='userfav',
            name='goods',
            field=models.ForeignKey(help_text='商品ID', on_delete=django.db.models.deletion.CASCADE, to='goods.Goods', verbose_name='商品'),
        ),
    ]
