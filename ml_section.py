import pickle
from ipywidgets import (Tab, SelectMultiple, Accordion, ToggleButton,
                        VBox, HBox, HTML, Image, Button, Text, Dropdown)
import plotly.graph_objs as go
import numpy as np


class MLSection:
    def __init__(self):
        self.data = pickle.load(open('all_data.pkl', 'rb'))
        self.setup_widgets()
        self.refresh_plot()

    def setup_widgets(self):
        amine_list = sorted(list(self.data.keys()))
        self.select_amine = Dropdown(
            options=amine_list,
            description='Amine: ',
            disabled=False,
        )

        self.select_metric = Dropdown(
            options=['Accuracy', 'Precision', 'Recall', 'F1'],
            description='Metric: ',
            disabled=False,
        )

        self.figure = go.FigureWidget()

        self.select_amine.observe(self.select_amine_callback, 'value')
        self.select_metric.observe(self.select_amine_callback, 'value')

        self.full_widget = VBox([self.figure,
                                 HBox([self.select_amine, self.select_metric])])

    def select_amine_callback(self, state):
        self.refresh_plot()

    def refresh_plot(self):
        color_list = ['rgba(31, 118, 180, 1)', 'rgba(255, 127, 14, 1)',
                      'rgba(44, 160, 44, 1)', 'rgba(214, 39, 39, 1)',
                      'rgba(147, 103, 189, 1)', 'rgba(140, 86, 75, 1)',
                      'rgba(227, 119, 195, 1)', 'rgba(127, 127, 127, 1)',
                      'rgba(189, 189, 34, 1)', 'rgba(23, 189, 207, 1)']
        amine = self.select_amine.value
        metric = self.select_metric.value
        x_values = self.data[amine]['learn_rate']
        # y_values = self.data[amine]
        layout = go.Layout(
            hovermode='closest',
            showlegend=True,
            xaxis=go.layout.XAxis(
                title=go.layout.xaxis.Title(
                    text="Number of training experiments",
                ),
            ),
            yaxis=go.layout.YAxis(
                title=go.layout.yaxis.Title(
                    text=metric,
                )
            ),
        )

        trace_list = []
        for i, model in enumerate(sorted(self.data[amine]['model'].keys())):
            y_mean = [np.mean(y_data.flatten()) for y_data in
                      self.data[amine]['model'][model][metric.lower()]]
            x = x_values

            trace = go.Scatter(
                name=model,
                x=x,
                y=y_mean,
                marker=dict(size=5, color=color_list[i % len(color_list)],),
                opacity=1.0,

            )
            trace_list.append(trace)

            y_std_dev = [np.std(y_data.flatten()) for y_data in
                         self.data[amine]['model'][model][metric.lower()]]

            y_upper = np.array(y_mean) + np.array(y_std_dev)
            y_lower = np.array(y_mean) - np.array(y_std_dev)

            trace2 = go.Scatter(
                x=x+x[::-1],
                y=list(y_upper)+list(reversed(y_lower)),
                fill='tozerox',
                fillcolor=self.change_alpha(
                    color_list[i % len(color_list)], 0.3),
                line=dict(color='rgba(255,255,255,0)'),
                name=model,
                showlegend=False,
            )
            trace_list.append(trace2)
            """
            if std_dev[model]:

                x_rev = x[::-1]
                y_upper = np.array(data[model]) + np.array(std_dev[model])
                y_lower = np.array(data[model]) - np.array(std_dev[model])
                trace2 = go.Scatter(
                    x=x+x_rev,
                    y=list(y_upper)+list(y_lower)[::-1],
                    fill='tozerox',
                    fillcolor=self.change_alpha(
                        color_list[i % len(color_list)], 0.3),
                    line=dict(color='rgba(255,255,255,0)'),
                    name=model,
                    showlegend=False,
                )
                trace_list.append(trace2)
            """
        # self.figure = go.FigureWidget(data=trace_list, layout=layout)
        with self.figure.batch_update():
            self.figure.data = []
            # for trace in trace_list:
            self.figure.add_traces(trace_list)
            self.figure.layout = layout

    def change_alpha(self, color, alpha):
        color = color.split(',')
        color[-1] = '{})'.format(alpha)
        return ','.join(color)

    @property
    def plot(self):
        return self.full_widget
