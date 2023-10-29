from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from . import forms, models
import pandas as pd
import os
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
import plotly.express as px

file_loc = r'/Users/stevenmeesters/PycharmProjects/SweStat/media/'


def temptest(request):
    return render(request, 'temptest.html')


def home(request):
    # add deletion of data!
    def delete_data():
        models.Document.objects.filter(session_key=request.session.session_key).delete()
        models.DocumentVariables.objects.filter(session_key=request.session.session_key).delete()
        models.FormCounter.objects.filter(session_key=request.session.session_key).delete()
        models.SimpleGraphModel.objects.filter(session_key=request.session.session_key).delete()
        models.GraphTitleModel.objects.filter(session_key=request.session.session_key).delete()
        models.GraphLayoutModel.objects.filter(session_key=request.session.session_key).delete()

    # Logic to delete all data when returning to the home page
    try:
        file_loc = models.Document.objects.filter(session_key=request.session.session_key).values()
        for x in file_loc:
            file = x['docfile']
            os.remove(r'/Users/stevenmeesters/PycharmProjects/SweStat/media/' + f"{file}")
        delete_data()
        print('Data deleted')
    except ObjectDoesNotExist:
        delete_data()
        print('ObjectDoesNotExist')
    except FileNotFoundError:
        delete_data()
        print('FileNotFoundError')

    # getting the session key if it is not saved
    if not request.session.session_key:
        request.session.save()
    session_id = request.session.session_key
    print('session_id: ', session_id)

    # Initializing the data upload form
    doc_form = forms.LandingPageForm(request.POST, request.FILES)
    if request.method == 'POST':
        if doc_form.is_valid():
            newdoc = models.Document(session_key=session_id,
                                     docfile=request.FILES['csv_data'],
                                     file_type='CSV')
            newdoc.save()
            return redirect('upload_document')

    return render(request, 'home.html', context={'doc_form': doc_form})


def upload_document(request):
    models.FormCounter.objects.filter(session_key=request.session.session_key).delete()

    max_id = models.Document.objects.filter(session_key=request.session.session_key).latest('id').id
    file_name = models.Document.objects.values_list('docfile', flat=True).get(id=max_id)

    def get_extension(file):
        return file[file.find('.') + 1:].upper()

    xt = get_extension(file_name)

    if xt == 'CSV':
        print('CSV file')
        df = pd.read_csv(file_loc + file_name, delimiter=';')
    if xt == 'XLSX':
        print('XLSX file')
        df = pd.read_excel(file_loc + file_name)

    head = df.head(10)

    def meta_data(data):
        return len(data), len(data.columns)

    meta_r, meta_c = meta_data(df)

    variables = list()
    l = models.DocumentVariables.objects.filter(session_key=request.session.session_key).values()
    if l:
        for x in l:
            variables.append(x['variable_name'])

    var_no = 0
    for col in df.columns.to_list():
        if col not in variables:
            var_no += 1
            m = models.DocumentVariables(session_key=request.session.session_key,
                                         variable_no=var_no,
                                         variable_name=col)
            m.save()

    return render(request, 'show_data.html', context={'df': head, 'extention': xt, 'meta_r': meta_r, 'meta_c': meta_c})


def configure_dashboard(request):
    models.SimpleGraphModel.objects.filter(session_key=request.session.session_key).delete()
    models.GraphTitleModel.objects.filter(session_key=request.session.session_key).delete()
    models.GraphLayoutModel.objects.filter(session_key=request.session.session_key).delete()

    if request.method == 'GET':
        try:
            print('try')
            n_forms = models.FormCounter.objects.filter(session_key=request.session.session_key).latest('id').form_count
            number = n_forms
            models.FormCounter.objects.filter(session_key=request.session.session_key).delete()
            m = models.FormCounter(session_key=request.session.session_key,
                                   form_count=number + 1)
            m.save()
        except ObjectDoesNotExist:
            print('ObjectDoesNotExist')
            m = models.FormCounter(session_key=request.session.session_key,
                                   form_count=1)
            m.save()
            n_forms = 1

    n_forms = models.FormCounter.objects.filter(session_key=request.session.session_key).latest('id').form_count
    print(n_forms)

    cols = []
    for column in models.DocumentVariables.objects.filter(session_key=request.session.session_key).values():
        cols.append(column['variable_name'])

    graph_form = forms.CreateMultiLoopChartForm(request.POST, cols, n_forms)

    if request.method == 'POST':
        print('POST check')
        if graph_form.is_valid():
            print('Valid')
            for idx in range(n_forms):
                m = models.SimpleGraphModel(
                    session_key=request.session.session_key,
                    graph_no=idx,
                    chart_type=graph_form.cleaned_data[f'chart{idx}'],
                    x=graph_form.cleaned_data[f'x{idx}'],
                    y=graph_form.cleaned_data[f'y{idx}'],
                    titel=graph_form.cleaned_data[f'titel{idx}']
                )
                m.save()
                if idx == (n_forms - 1):
                    return redirect(reverse('dashboard'))

    return render(request, 'configure_dash.html', context={'graph_form': graph_form, 'n_forms': n_forms})


def dashboard(request):
    max_id = models.Document.objects.filter(session_key=request.session.session_key).latest('id').id
    file_name = models.Document.objects.values_list('docfile', flat=True).get(id=max_id)

    try:
        dash_title = models.GraphTitleModel.objects.filter(session_key=request.session.session_key).latest('id').title
    except ObjectDoesNotExist:
        m = models.GraphTitleModel(session_key=request.session.session_key,
                                   title='Your Dashboard')
        m.save()
        dash_title = models.GraphTitleModel.objects.filter(session_key=request.session.session_key).latest('id').title

    def get_extension(file):
        return file[file.find('.') + 1:].upper()

    xt = get_extension(file_name)

    if xt == 'CSV':
        df = pd.read_csv(file_loc + file_name, delimiter=';')
    if xt == 'XLSX':
        df = pd.read_excel(file_loc + file_name)

    try:
        n_forms = models.FormCounter.objects.filter(session_key=request.session.session_key).latest('id').form_count
    except ObjectDoesNotExist:
        n_forms = 1

    graph_info = models.SimpleGraphModel.objects.filter(session_key=request.session.session_key).values()

    def create_chart(chart_no, chart, x, y, titel, layout):
        final_titel = titel
        for d in layout:
            final_titel = d['graph_title'] if d['graph_title'] != '' else titel
        if chart == 'Linjediagram':
            return px.line(data_frame=df, x=x, y=y, title=final_titel, color_discrete_map={'Age': 'red'})
        if chart == 'Stapeldiagram':
            return px.bar(data_frame=df, x=x, y=y, title=final_titel, color_discrete_map={'Age': 'red'})
        if chart == 'Korrelationsgraf':
            return px.scatter(data_frame=df, x=x, y=y, title=final_titel, color_discrete_map={x: color})
        if chart == 'Kaka':
            return px.pie(data_frame=df, names=x, values=y, title=final_titel, color_discrete_map={x: color})

    fig_list = []
    for x in graph_info:
        layout_info = models.GraphLayoutModel.objects.filter(session_key=request.session.session_key).filter(graph_id=x['graph_no']).values()
        fig = create_chart(chart_no=x['graph_no'], chart=x['chart_type'], x=x['x'], y=x['y'], titel=x['titel'], layout=layout_info)
        color = '#636EFA'
        for data in layout_info:
            if data['graph_title_center'] is True:
                fig.update_layout(title_x=0.5)
        fig = fig.update_traces(marker=dict(color=color))
        fig = fig.to_html()
        fig_list.append([x['graph_no'], fig])

    return render(request, template_name='build_dash.html', context={'fig_list': fig_list, 'dash_title': dash_title})


# Under construction
def return_from_dash(request):
    max_id = models.Document.objects.filter(session_key=request.session.session_key).latest('id').id
    file_name = models.Document.objects.values_list('docfile', flat=True).get(id=max_id)

    def get_extension(file):
        return file[file.find('.') + 1:].upper()

    xt = get_extension(file_name)

    if xt == 'CSV':
        df = pd.read_csv(file_loc + file_name, delimiter=';')
    if xt == 'XLSX':
        df = pd.read_excel(file_loc + file_name)

    if models.Document.objects.filter(session_key=request.session.session_key).latest('id').file_type == 'SQL':
        del df['Unnamed: 0']

    dash_title = models.GraphTitleModel.objects.filter(session_key=request.session.session_key).latest('id').title

    title_form = forms.GraphTitleFormNew(request.POST, dash_title)
    if request.method == 'POST':
        if title_form.is_valid():
            if title_form.cleaned_data['title'] != '':
                models.GraphTitleModel.objects.filter(session_key=request.session.session_key).delete()
                m = models.GraphTitleModel(session_key=request.session.session_key,
                                           title=title_form.cleaned_data['title'])
                m.save()
                return redirect(reverse('dashboard'))
            return redirect(reverse('dashboard'))

    grafer = models.SimpleGraphModel.objects.filter(session_key=request.session.session_key).values()

    antal = 0
    for i in grafer:
        antal += 1

    cols = list()
    for col in models.DocumentVariables.objects.filter(session_key=request.session.session_key).values():
        cols.append(col['variable_name'])

    form = forms.ReturnFromDashPopulateForm(request.POST, antal, cols, grafer)

    if request.method == 'POST':
        print('POSTPOST')
        if form.is_valid():
            models.SimpleGraphModel.objects.filter(session_key=request.session.session_key).delete()
            for idx in range(antal):
                m = models.SimpleGraphModel(
                    session_key=request.session.session_key,
                    graph_no=idx + 1,
                    chart_type=form.cleaned_data[f'chart{idx}'],
                    x=form.cleaned_data[f'x{idx}'],
                    y=form.cleaned_data[f'y{idx}'],
                    titel=form.cleaned_data[f'titel{idx}']
                )
                m.save()
                if idx == (antal - 1):
                    return redirect(reverse('dashboard'))

    return render(request, 'return_from_dash.html',
                  context={'columns': list(df.columns), 'data': df, 'form': form, 'dash_title': dash_title,
                           'title_form': title_form})


def change_layout(request, graph_no):
    max_id = models.Document.objects.filter(session_key=request.session.session_key).latest('id').id
    file_name = models.Document.objects.values_list('docfile', flat=True).get(id=max_id)

    df = pd.read_csv(file_loc + file_name, delimiter=';')

    def create_chart(chart, x, y, titel):
        if chart == 'Linjediagram':
            return px.line(data_frame=df, x=x, y=y, title=titel).to_html()
        if chart == 'Stapeldiagram':
            return px.bar(data_frame=df, x=x, y=y, title=titel).to_html()
        if chart == 'Korrelationsgraf':
            return px.scatter(data_frame=df, x=x, y=y, title=titel).to_html()
        if chart == 'Kaka':
            return px.pie(data_frame=df, names=x, values=y, title=titel).to_html()

    # get the graph
    graph_data = models.SimpleGraphModel.objects.filter(session_key=request.session.session_key).filter(graph_no=graph_no).values()
    for x in graph_data:
        fig = create_chart(x['chart_type'], x['x'], x['y'], x['titel'])

    layout_form = forms.ChangeGraphLayoutForm(request.POST)
    if request.method == 'POST':
        if layout_form.is_valid():
            data = models.GraphLayoutModel.objects.filter(session_key=request.session.session_key).filter(graph_id=graph_no).values()
            title = ''
            if data:
                for x in data:
                    title = x['graph_title']
            models.GraphLayoutModel.objects.filter(session_key=request.session.session_key).filter(graph_id=graph_no).delete()
            m = models.GraphLayoutModel(
                session_key=request.session.session_key,
                graph_id=graph_no,
                graph_title=title if layout_form.cleaned_data['graph_title'] == '' else layout_form.cleaned_data['graph_title'],
                color=layout_form.cleaned_data['color'],
                bg_color=layout_form.cleaned_data['bg_color'],
                height=layout_form.cleaned_data['height'],
                width=layout_form.cleaned_data['width'],
                x_axis_sta=layout_form.cleaned_data['x_axis_start'],
                x_axis_end=layout_form.cleaned_data['x_axis_end'],
                y_axis_sta=layout_form.cleaned_data['y_axis_start'],
                y_axis_end=layout_form.cleaned_data['y_axis_end'],
                graph_title_center=layout_form.cleaned_data['graph_title_center']
            )
            m.save()
            return redirect(reverse('dashboard'))

    return render(request, 'change_layout.html', context={'graph_no': graph_no, 'chart': fig, 'layout_form': layout_form})
