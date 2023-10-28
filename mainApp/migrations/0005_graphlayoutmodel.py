# Generated by Django 4.2.6 on 2023-10-27 06:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainApp', '0004_graphtitlemodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='GraphLayoutModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(max_length=255)),
                ('graph_id', models.IntegerField()),
                ('graph_title', models.CharField(max_length=255)),
                ('color', models.CharField(max_length=255)),
                ('bg_color', models.CharField(max_length=255)),
                ('height', models.CharField(max_length=255)),
                ('width', models.CharField(max_length=255)),
                ('x_axis_sta', models.FloatField()),
                ('x_axis_end', models.FloatField()),
                ('y_axis_sta', models.FloatField()),
                ('y_axis_end', models.FloatField()),
            ],
        ),
    ]
