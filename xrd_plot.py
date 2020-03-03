import plotly.graph_objs as go
from collections import defaultdict
from pathlib import Path
from ipywidgets import Tab, SelectMultiple, Accordion, ToggleButton, VBox, HBox, HTML, Image, Button, Text, Dropdown
import pandas as pd


class XRD:
    def __init__(self):
        xrd_paths = Path.cwd() / Path('data/xrd/xy')
        self.xrd_files = defaultdict(list)

        # Scanning xrd files
        for xrd_file in xrd_paths.glob('*.xy'):
            filename = '.'.join(xrd_file.name.split('.')[:-1])
            if filename.split('_')[-1] != 'LBL':
                plate_name = '_'.join(filename.split('_')[:-1])
                vial_name = filename.split('_')[-1]
                self.xrd_files[plate_name].append(vial_name)
            else:
                plate_name = filename
                self.xrd_files[plate_name].append(None)

        self.plate_list = list(self.xrd_files.keys())
        self.select_plate_widget = Dropdown(
            options=self.plate_list,
            description='Plate:',
            disabled=False,
        )
        self.select_plate_widget.observe(self.change_plates, 'value')

        self.select_vial_widget = Dropdown(
            options=self.xrd_files[self.plate_list[0]],
            description='Vial:',
            disabled=False,
        )
        self.select_vial_widget.observe(self.change_vial, 'value')

        # Initialize data
        self.selected_plate = self.plate_list[0]
        self.selected_vial = self.xrd_files[self.plate_list[0]][0]
        self.xyplot = XYPlot([0], [0]).plot(r'$2\theta \text{ (degree)}$',
                                            'Intensity (a.u)')

        self.select_xrd()
        self.full_widget = VBox(
            [self.xyplot, self.select_plate_widget, self.select_vial_widget])
        self.full_widget.layout.align_items = 'center'

    def change_plates(self, state):
        self.selected_plate = state.new
        self.selected_vial = self.xrd_files[self.selected_plate][0]
        self.select_vial_widget.options = self.xrd_files[self.selected_plate]
        self.select_xrd()

    def change_vial(self, state):
        self.selected_vial = state.new
        self.select_xrd()

    def select_xrd(self):
        if self.selected_vial == None:
            filename = self.selected_plate + '.xy'
        else:
            filename = self.selected_plate + '_' + self.selected_vial + '.xy'
        data = pd.read_csv(Path('data/xrd/xy') / Path(filename),
                           header=None,
                           skiprows=1,
                           delimiter=' ')
        x = data.iloc[:, 0]
        y = data.iloc[:, 1]
        with self.xyplot.batch_update():
            self.xyplot.data[0].x = x
            self.xyplot.data[0].y = y

    @property
    def plot(self):
        return self.full_widget


class XYPlot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def plot(self, xaxis_label, yaxis_label, annotations=[], reversed=False, extra_traces=None):
        ann = []
        for a in annotations:
            ann.append(go.layout.Annotation(
                x=a[0],
                y=a[1],
                xref="x",
                yref="y",
                text=a[2],
                showarrow=False,
                ax=20,
                ay=-30,
            ))
        trace = go.Scatter(
            x=self.x,
            y=self.y,
        )

        data = [trace]
        if extra_traces:
            for t in extra_traces:
                data.append(t)

        layout = go.Layout(
            showlegend=False,
            annotations=ann,
            xaxis=go.layout.XAxis(
                title=go.layout.xaxis.Title(
                    text=xaxis_label,
                ),
                autorange='reversed' if reversed else True,
            ),
            yaxis=go.layout.YAxis(
                title=go.layout.yaxis.Title(
                    text=yaxis_label,
                )
            ),
            autosize=False,
            width=1000,
            height=600,
            margin=go.layout.Margin(
                l=50,
                r=50,
                b=100,
                t=100,
                pad=4
            ),
        )
        return go.FigureWidget(data=data, layout=layout)
