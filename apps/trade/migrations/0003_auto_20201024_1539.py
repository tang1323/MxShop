# Generated by Django 2.2 on 2020-10-24 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trade', '0002_auto_20201024_1303'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderinfo',
            name='pay_status',
            field=models.CharField(blank=True, choices=[('success', '成功'), ('cancel', '取消'), ('cancel', '待支付')], max_length=30, null=True, verbose_name='订单状态'),
        ),
    ]