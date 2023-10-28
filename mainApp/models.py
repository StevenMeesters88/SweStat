from django.db import models


# Create your models here.
class Document(models.Model):
    session_key = models.CharField(max_length=255)
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')
    file_type = models.CharField(max_length=255)


class DocumentVariables(models.Model):
    session_key = models.CharField(max_length=255)
    variable_no = models.IntegerField()
    variable_name = models.CharField(max_length=1000)


class FormCounter(models.Model):
    session_key = models.CharField(max_length=255)
    form_count = models.IntegerField()


class SimpleGraphModel(models.Model):
    session_key = models.CharField(max_length=255)
    graph_no = models.IntegerField()
    chart_type = models.CharField(max_length=255)
    x = models.CharField(max_length=255)
    y = models.CharField(max_length=255)
    titel = models.CharField(max_length=255)


class GraphTitleModel(models.Model):
    session_key = models.CharField(max_length=255)
    title = models.CharField(max_length=255)


class GraphLayoutModel(models.Model):
    session_key = models.CharField(max_length=255, null=True)
    graph_id = models.CharField(max_length=255, null=True)
    graph_title = models.CharField(max_length=255, null=True)
    graph_title_center = models.BooleanField(null=True)
    color = models.CharField(max_length=255, null=True)
    bg_color = models.CharField(max_length=255, null=True)
    height = models.CharField(max_length=255, null=True)
    width = models.CharField(max_length=255, null=True)
    x_axis_sta = models.FloatField(null=True)
    x_axis_end = models.FloatField(null=True)
    y_axis_sta = models.FloatField(null=True)
    y_axis_end = models.FloatField(null=True)
