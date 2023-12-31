from django import forms
from . import models
import pandas as pd


def validate_file_extension(value):
    if not value.name.endswith(('.csv', '.xlsx')):
        raise forms.ValidationError("Only CSV or XLSX files are accepted")


class LandingPageForm(forms.Form):
    csv_data = forms.FileField(widget=forms.FileInput(attrs={
        'accept': ".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"}),
        label='Select a file', validators=[validate_file_extension])


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


# Backup, change in class name and init method!
class ChangeGraphLayoutFormOLD(forms.Form):

    def __init__(self, *args, **kwargs):
        super(ChangeGraphLayoutFormOLD, self).__init__(*args, **kwargs)
        req, centered = args

        print('form: ', centered)

        self.fields['graph_title_center'] = forms.BooleanField(initial=centered, required=False)

    CHOICES_COLOR = (
        ('#636EFA', 'Standard'),
        ('Black', 'Black'),
        ('White', 'White'),
        ('Red', 'Red'),
        ('Blue', 'Blue'),
        ('Green', 'Green'),
        ('Purple', 'Purple'),
        ('Yellow', 'Yellow')
    )

    BG_CHOICES_COLOR = (
        ('#f0f8ff', 'Standard'),
        ('Black', 'Black'),
        ('White', 'White'),
        ('Red', 'Red'),
        ('Blue', 'Blue'),
        ('Green', 'Green'),
        ('Purple', 'Purple'),
        ('Yellow', 'Yellow')
    )

    GRAPH_CHOICES = (
        ("Linjediagram", "Linjediagram"),
        ("Stapeldiagram", "Stapeldiagram"),
        ("Korrelationsgraf", "Korrelationsgraf"),
        ("Kaka", "Kaka")
    )

    change_graph_type = forms.ChoiceField(choices=GRAPH_CHOICES, required=False)
    graph_title = forms.CharField(max_length=255, required=False)
    color = forms.ChoiceField(choices=CHOICES_COLOR, required=False)
    bg_color = forms.ChoiceField(choices=BG_CHOICES_COLOR, required=False)
    height = forms.CharField(max_length=255, required=False)
    width = forms.CharField(max_length=255, required=False)
    x_axis_start = forms.FloatField(required=False)
    x_axis_end = forms.FloatField(required=False)
    y_axis_start = forms.FloatField(required=False)
    y_axis_end = forms.FloatField(required=False)


class ChangeGraphLayoutForm(forms.Form):
    CHOICES_COLOR = (
        ('#636EFA', 'Standard'),
        ('Black', 'Black'),
        ('White', 'White'),
        ('Red', 'Red'),
        ('Blue', 'Blue'),
        ('Green', 'Green'),
        ('Purple', 'Purple'),
        ('Yellow', 'Yellow')
    )

    BG_CHOICES_COLOR = (
        ('#f0f8ff', 'Standard'),
        ('Black', 'Black'),
        ('White', 'White'),
        ('Red', 'Red'),
        ('Blue', 'Blue'),
        ('Green', 'Green'),
        ('Purple', 'Purple'),
        ('Yellow', 'Yellow')
    )

    GRAPH_CHOICES = (
        ("Linjediagram", "Linjediagram"),
        ("Stapeldiagram", "Stapeldiagram"),
        ("Korrelationsgraf", "Korrelationsgraf"),
        ("Kaka", "Kaka")
    )

    def __init__(self, *args, **kwargs):
        super(ChangeGraphLayoutForm, self).__init__(*args, **kwargs)
        req, title, centered, sel_color = args
        # req, title, centered, sel_color, sel_bg_color, min_x, max_x, min_y, max_y

        print('form centered: ', centered)

        self.fields['graph_title'] = forms.CharField(widget=forms.TextInput(
            attrs={'placeholder': f'{title}',
                   'style': 'width: 300px; height: 30px; border-radius: 4px; font-size: 15px;',
                   'class': 'form-control'}), required=False, max_length=255)
        self.fields['graph_title_center'] = forms.BooleanField(initial=centered, required=False)
        self.fields['color'] = forms.CharField(label='Color', initial={sel_color},
                                               widget=forms.Select(
                                                   choices=self.CHOICES_COLOR,
                                                   attrs={
                                                       'style': 'width: 300px; height: 30px; border-radius: 4px;',
                                                       'class': 'form-control'}), required=False)
        self.fields['bg_color'] = forms.CharField(label='BG_Color',
                                                  widget=forms.Select(
                                                      choices=self.BG_CHOICES_COLOR,
                                                      attrs={
                                                          'style': 'width: 300px; height: 30px; border-radius: 4px;',
                                                          'class': 'form-control'}), required=False)
        self.fields['x_axis_start'] = forms.FloatField(required=False)
        self.fields['x_axis_end'] = forms.FloatField(required=False)
        self.fields['y_axis_start'] = forms.FloatField(required=False)
        self.fields['y_axis_end'] = forms.FloatField(required=False)

    # height = forms.CharField(max_length=255, required=False)
    # width = forms.CharField(max_length=255, required=False)
