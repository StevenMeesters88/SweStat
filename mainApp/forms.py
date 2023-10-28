from django import forms
from . import models
import pandas as pd


class LandingPageForm(forms.Form):
    csv_data = forms.FileField(widget=forms.FileInput(attrs={'accept': ".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"}), label='Select a file')


class CreateMultiLoopChartForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(CreateMultiLoopChartForm, self).__init__(*args, **kwargs)
        req, cols, n = args

        for i in range(n):
            self.fields[f'chart{i}'] = forms.CharField(label='Choose diagram', widget=forms.Select(choices=(
                ("Linjediagram", "Linjediagram"),
                ("Stapeldiagram", "Stapeldiagram"),
                ("Korrelationsgraf", "Korrelationsgraf"),
                ("Kaka", "Kaka"),
            ), attrs={'style': 'width: 300px; height: 30px; border-radius: 4px;', 'class': 'form-control'}))
            self.fields[f'x{i}'] = forms.CharField(label='Choose X variable',
                                                   widget=forms.Select(choices=tuple([(name, name) for name in cols]),
                                                                       attrs={
                                                                           'style': 'width: 300px; height: 30px; border-radius: 4px;',
                                                                           'class': 'form-control'}))
            self.fields[f'y{i}'] = forms.CharField(label='Choose Y variable',
                                                   widget=forms.Select(choices=tuple([(name, name) for name in cols]),
                                                                       attrs={
                                                                           'style': 'width: 300px; height: 30px; border-radius: 4px;',
                                                                           'class': 'form-control'}))
            self.fields[f'titel{i}'] = forms.CharField(widget=forms.TextInput(
                attrs={'placeholder': 'Title',
                       'style': 'width: 300px; height: 30px; border-radius: 4px; font-size: 15px;',
                       'class': 'form-control'}), required=False, max_length=255)


class ReturnFromDashPopulateForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(ReturnFromDashPopulateForm, self).__init__(*args, **kwargs)
        req, antal, cols, graph_data = args

        df = pd.DataFrame(graph_data)

        for i in df.index:
            self.fields[f'chart{i}'] = forms.CharField(label='Choose_chart_type', widget=forms.Select(choices=(
                ("Linjediagram", "Linjediagram"),
                ("Stapeldiagram", "Stapeldiagram"),
                ("Korrelationsgraf", "Korrelationsgraf"),
                ("Kaka", "Kaka"),
            ), attrs={'style': 'width: 300px; height: 30px; border-radius: 4px;', 'class': 'form-control'}))
            self.fields[f'x{i}'] = forms.CharField(label='Välj typ',
                                                   widget=forms.Select(choices=tuple([(name, name) for name in cols]),
                                                                       attrs={
                                                                           'style': 'width: 300px; height: 30px; border-radius: 4px;',
                                                                           'class': 'form-control'}))
            self.fields[f'y{i}'] = forms.CharField(label='Välj typ',
                                                   widget=forms.Select(choices=tuple([(name, name) for name in cols]),
                                                                       attrs={
                                                                           'style': 'width: 300px; height: 30px; border-radius: 4px;',
                                                                           'class': 'form-control'}))
            self.fields[f'titel{i}'] = forms.CharField(widget=forms.TextInput(
                attrs={'placeholder': f'{df["titel"][i]}',
                       'style': 'width: 300px; height: 30px; border-radius: 4px; font-size: 15px;',
                       'class': 'form-control'}), required=False, max_length=255)


class GraphTitleForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'Title', 'style': 'width: 300px; height: 30px; border-radius: 4px; font-size: 15px;',
               'class': 'form-control'}), required=False, max_length=255)


class GraphTitleFormNew(forms.Form):

    def __init__(self, *args, **kwargs):
        super(GraphTitleFormNew, self).__init__(*args, **kwargs)
        req, curr_title = args

        self.fields[f'title'] = forms.CharField(widget=forms.TextInput(
            attrs={'placeholder': f'{curr_title}',
                   'style': 'width: 300px; height: 30px; border-radius: 4px; font-size: 15px;',
                   'class': 'form-control'}), required=False, max_length=255)


class ChangeGraphLayoutForm(forms.Form):
    CHOICES_COLOR = (
        ('Standard', 'Standard'),
        ('Black', 'Black'),
        ('White', 'White'),
        ('Red', 'Red'),
        ('Blue', 'Blue'),
        ('Green', 'Green'),
        ('Purple', 'Purple'),
        ('Yellow', 'Yellow')
    )

    graph_title = forms.CharField(max_length=255, required=False)
    graph_title_center = forms.BooleanField(required=False)
    color = forms.ChoiceField(choices=CHOICES_COLOR, required=False)
    bg_color = forms.ChoiceField(choices=CHOICES_COLOR, required=False)
    height = forms.CharField(max_length=255, required=False)
    width = forms.CharField(max_length=255, required=False)
    x_axis_start = forms.FloatField(required=False)
    x_axis_end = forms.FloatField(required=False)
    y_axis_start = forms.FloatField(required=False)
    y_axis_end = forms.FloatField(required=False)

