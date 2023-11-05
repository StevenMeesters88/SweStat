from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from . import forms, models
import pandas as pd
import os
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
import plotly.express as px

file_loc = r'/Users/stevenmeesters/PycharmProjects/SweStat/media/'  # /home/SweStat/SweStat/media i pythonanywhere


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

    def get_data_file(xt):
        if xt == 'CSV':
            print('CSV file')
            return pd.read_csv(file_loc + file_name, delimiter=';')
        if xt == 'XLSX':
            print('XLSX file')
            return pd.read_excel(file_loc + file_name)

    df = get_data_file(xt)

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

    return render(request, 'show_data.html',
                  context={'df': df.head(10), 'extention': xt, 'meta_r': meta_r, 'meta_c': meta_c})


def configure_dashboard(request):
    models.SimpleGraphModel.objects.filter(session_key=request.session.session_key).delete()
    models.GraphTitleModel.objects.filter(session_key=request.session.session_key).delete()
    models.GraphLayoutModel.objects.filter(session_key=request.session.session_key).delete()

    if request.method == 'GET':
        try:
            n_forms = models.FormCounter.objects.filter(session_key=request.session.session_key).latest('id').form_count
            number = n_forms
            models.FormCounter.objects.filter(session_key=request.session.session_key).delete()
            m = models.FormCounter(session_key=request.session.session_key,
                                   form_count=number + 1)
            m.save()
        except ObjectDoesNotExist:
            m = models.FormCounter(session_key=request.session.session_key,
                                   form_count=1)
            m.save()
            n_forms = 1

    n_forms = models.FormCounter.objects.filter(session_key=request.session.session_key).latest('id').form_count

    cols = []
    for column in models.DocumentVariables.objects.filter(session_key=request.session.session_key).values():
        cols.append(column['variable_name'])

    graph_form = forms.CreateMultiLoopChartForm(request.POST, cols, n_forms)

    if request.method == 'POST':
        if graph_form.is_valid():
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

    def create_chart(chart_no, chart, x, y, titel, color, bg_color, start_y, end_y, start_x, end_x):
        if chart == 'Linjediagram':
            return px.line(data_frame=df, x=x, y=y, title=titel).update_traces(line_color=color).update_layout(
                plot_bgcolor=bg_color, yaxis_range=[start_y, end_y], xaxis_range=[start_x, end_x])
        if chart == 'Stapeldiagram':
            return px.bar(data_frame=df, x=x, y=y, title=titel).update_traces(marker_color=color).update_layout(
                plot_bgcolor=bg_color, yaxis_range=[start_y, end_y], xaxis_range=[start_x, end_x])
        if chart == 'Korrelationsgraf':
            return px.scatter(data_frame=df, x=x, y=y, title=titel).update_traces(line_color=color).update_layout(
                plot_bgcolor=bg_color, yaxis_range=[start_y, end_y], xaxis_range=[start_x, end_x])
        if chart == 'Kaka':
            return px.pie(data_frame=df, names=x, values=y, title=titel).update_layout(plot_bgcolor=bg_color)

    fig_list = []
    for x in graph_info:
        color = '#636EFA'
        bg_color = '#f0f8ff'
        title = 'Your Graph' if x['titel'] == '' else x['titel']
        yaxis_start = min(x['y'])
        yaxis_end = max(x['y'])
        xaxis_start = min(x['x'])
        xaxis_end = max(x['x'])
        layout_info = models.GraphLayoutModel.objects.filter(session_key=request.session.session_key).filter(
            graph_id=x['graph_no']).values()
        if layout_info:
            print(f"Graph info: {x['graph_no']}, LAYOUT FINNS")
            for d in layout_info:
                color = d['color']
                title = d['graph_title'] if d['graph_title'] != '' else 'Your Dashboard'
                bg_color = d['bg_color']
                yaxis_start = d['y_axis_sta'] if d['y_axis_sta'] != '' else min(x['y'])
                yaxis_end = d['y_axis_end'] if d['y_axis_end'] != '' else max(x['y'])
                xaxis_start = d['x_axis_sta'] if d['x_axis_sta'] != '' else min(x['x'])
                xaxis_end = d['x_axis_end'] if d['x_axis_end'] != '' else max(x['x'])

        fig = create_chart(chart_no=x['graph_no'], chart=x['chart_type'], x=x['x'], y=x['y'], titel=title,
                           color=color, bg_color=bg_color, start_y=yaxis_start, end_y=yaxis_end,
                           start_x=xaxis_start, end_x=xaxis_end)
        for data in layout_info:
            if data['graph_title_center'] is True:
                fig.update_layout(title_x=0.5)

        fig.update_xaxes(
            mirror=True,
            ticks='outside',
            showline=True,
            linecolor='black' if bg_color != 'black' else 'white',
            gridcolor='lightgrey' if bg_color != 'black' else 'white',
        )
        fig.update_yaxes(
            mirror=True,
            ticks='outside',
            showline=True,
            linecolor='black' if bg_color != 'black' else 'white',
            gridcolor='lightgrey' if bg_color != 'black' else 'white',
        )

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

    def get_extension(file):
        return file[file.find('.') + 1:].upper()

    xt = get_extension(file_name)

    def get_data_file(xt):
        if xt == 'CSV':
            print('CSV file')
            return pd.read_csv(file_loc + file_name, delimiter=';')
        if xt == 'XLSX':
            print('XLSX file')
            return pd.read_excel(file_loc + file_name)

    df = get_data_file(xt)

    graph_data = models.SimpleGraphModel.objects.filter(session_key=request.session.session_key).filter(
        graph_no=graph_no).values()

    def create_chart(chart, x, y, titel, color, bg_color, start_y, end_y, start_x, end_x):
        if chart == 'Linjediagram':
            fig = px.line(data_frame=df, x=x, y=y, title=titel).update_traces(line_color=color).update_layout(
                plot_bgcolor=bg_color, yaxis_range=[start_y, end_y], xaxis_range=[start_x, end_x])
            return fig
        if chart == 'Stapeldiagram':
            return px.bar(data_frame=df, x=x, y=y, title=titel).update_traces(marker_color=color).update_layout(
                plot_bgcolor=bg_color, yaxis_range=[start_y, end_y], xaxis_range=[start_x, end_x])
        if chart == 'Korrelationsgraf':
            return px.scatter(data_frame=df, x=x, y=y, title=titel).update_traces(line_color=color).update_layout(
                plot_bgcolor=bg_color, yaxis_range=[start_y, end_y], xaxis_range=[start_x, end_x])
        if chart == 'Kaka':
            return px.pie(data_frame=df, names=x, values=y, title=titel).update_layout(plot_bgcolor=bg_color)

    layout_data = models.GraphLayoutModel.objects.filter(session_key=request.session.session_key).filter(
        graph_id=graph_no).values()
    centered = False
    color = '#636EFA'
    bg_color = '#f0f8ff'
    yaxis_start = None
    yaxis_end = None
    xaxis_start = None
    xaxis_end = None
    for x in graph_data:
        yaxis_start = min(x['y'])
        yaxis_end = max(x['y'])
        xaxis_start = min(x['x'])
        xaxis_end = max(x['x'])

    if layout_data:
        for x in layout_data:
            centered = x['graph_title_center']  # fix the checkbox when ticked!
            color = x['color']
            bg_color = x['bg_color']
            yaxis_start = x['y_axis_sta'] if x['y_axis_sta'] != '' else min(x['y'])
            yaxis_end = x['y_axis_end'] if x['y_axis_end'] != '' else max(x['y'])
            xaxis_start = x['x_axis_sta'] if x['x_axis_sta'] != '' else min(x['x'])
            xaxis_end = x['x_axis_end'] if x['x_axis_end'] != '' else max(x['x'])

    title = None
    for x in graph_data:
        title = x['titel'] if x['titel'] != '' else 'Your Graph'
        fig = create_chart(x['chart_type'], x['x'], x['y'], title, color, bg_color,
                           yaxis_start, yaxis_end, xaxis_start, xaxis_end)

        fig.update_xaxes(
            mirror=True,
            ticks='outside',
            showline=True,
            linecolor='black' if bg_color != 'black' else 'white',
            gridcolor='lightgrey' if bg_color != 'black' else 'white',
        )
        fig.update_yaxes(
            mirror=True,
            ticks='outside',
            showline=True,
            linecolor='black' if bg_color != 'black' else 'white',
            gridcolor='lightgrey' if bg_color != 'black' else 'white',
        )
        fig = fig.to_html()

    print(bg_color, type(bg_color))

    layout_form = forms.ChangeGraphLayoutForm(request.POST, title, centered, color) # bg_color, xaxis_start, xaxis_end, yaxis_start, yaxis_end)
    print(layout_form, type(layout_form))
    if request.method == 'POST':
        if layout_form.is_valid():
            title = ''
            if layout_data:
                for x in layout_data:
                    title = x['graph_title']
            models.GraphLayoutModel.objects.filter(session_key=request.session.session_key).filter(
                graph_id=graph_no).delete()
            m = models.GraphLayoutModel(
                session_key=request.session.session_key,
                graph_id=graph_no,
                graph_title=title if layout_form.cleaned_data['graph_title'] == '' else layout_form.cleaned_data[
                    'graph_title'],
                color=layout_form.cleaned_data['color'],
                bg_color=layout_form.cleaned_data['bg_color'],
                x_axis_sta=layout_form.cleaned_data['x_axis_start'],
                x_axis_end=layout_form.cleaned_data['x_axis_end'],
                y_axis_sta=layout_form.cleaned_data['y_axis_start'],
                y_axis_end=layout_form.cleaned_data['y_axis_end'],
                graph_title_center=layout_form.cleaned_data['graph_title_center']
            )
            m.save()
            return redirect(reverse('dashboard'))

    return render(request, 'change_layout.html',
                  context={'graph_no': graph_no, 'chart': fig, 'layout_form': layout_form})
