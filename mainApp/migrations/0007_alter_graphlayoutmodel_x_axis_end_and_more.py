# Generated by Django 4.2.6 on 2023-10-27 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainApp', '0006_alter_graphlayoutmodel_graph_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='graphlayoutmodel',
            name='x_axis_end',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='graphlayoutmodel',
            name='x_axis_sta',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='graphlayoutmodel',
            name='y_axis_end',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='graphlayoutmodel',
            name='y_axis_sta',
            field=models.CharField(max_length=255),
        ),
    ]
