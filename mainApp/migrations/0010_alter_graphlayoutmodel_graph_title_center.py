# Generated by Django 4.2.6 on 2023-10-27 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainApp', '0009_graphlayoutmodel_graph_title_center'),
    ]

    operations = [
        migrations.AlterField(
            model_name='graphlayoutmodel',
            name='graph_title_center',
            field=models.BooleanField(null=True),
        ),
    ]
