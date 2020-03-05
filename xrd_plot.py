import plotly.graph_objs as go
from collections import defaultdict
from pathlib import Path
from ipywidgets import Tab, SelectMultiple, Accordion, ToggleButton, VBox, HBox, HTML, Image, Button, Text, Dropdown, Layout
import pandas as pd
import os
import numpy as np


class XRD:
    def __init__(self):
        xrd_paths = Path.cwd() / Path('data/xrd/xy')
        data_path = Path.cwd() / Path('data/0042.perovskitedata_RAPID.csv')

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

        self.inchis = pd.read_csv('./data/inventory.csv')
        self.inchi_dict = dict(zip(self.inchis['Chemical Name'],
                                   self.inchis['InChI Key (ID)']))
        self.chem_dict = dict(zip(self.inchis['InChI Key (ID)'],
                                  self.inchis['Chemical Name']))
        self.data = pd.read_csv(data_path)
        self.amine_to_plate_dict = defaultdict(list)
        for plate in self.plate_list:
            filtered = self.data[self.data['RunID_vial'].str.contains(
                plate, regex=False)]
            if len(filtered) > 0:
                amine_inchi = filtered.iloc[0]['_rxn_organic_inchikey']
                self.amine_to_plate_dict[amine_inchi].append(plate)
            else:
                print('Plate not found : {}'.format(plate))

        # print(self.amine_to_plate_dict)
        self.amine_list = [self.chem_dict[key]
                           for key in self.amine_to_plate_dict.keys()]

        self.select_amine_widget = Dropdown(
            options=self.amine_list,
            description='Amine:',
            disabled=False,
        )
        self.select_amine_widget.observe(self.change_amine, 'value')

        self.selected_amine = self.amine_list[0]
        self.selected_inchi = self.inchi_dict[self.selected_amine]
        self.selected_plate = self.amine_to_plate_dict[self.selected_inchi][0]
        self.selected_vial = self.xrd_files[self.selected_plate][0]

        self.select_plate_widget = Dropdown(
            options=self.amine_to_plate_dict[self.selected_inchi],
            description='Plate:',
            disabled=False,
        )
        self.select_plate_widget.observe(self.change_plates, 'value')

        self.select_vial_widget = Dropdown(
            options=self.xrd_files[self.selected_plate],
            description='Vial:',
            disabled=False,
        )
        self.select_vial_widget.observe(self.change_vial, 'value')

        # Initialize data

        self.xyplot = XYPlot([0], [0]).plot(r'$2\theta \text{ (degree)}$',
                                            'Intensity (a.u)')

        self.xrd_plot = VBox(
            [self.xyplot, self.select_amine_widget, HBox([self.select_plate_widget, self.select_vial_widget])])

        self.exp_details = ExpDetails()

        self.full_widget = Tab([self.xrd_plot, self.exp_details])
        self.full_widget.set_title(0, 'XRD Plot')
        self.full_widget.set_title(1, 'Experiment Details')

        self.select_xrd()
        #self.full_widget.layout.align_items = 'center'

    def change_amine(self, state):
        self.selected_amine = state.new
        self.selected_inchi = self.inchi_dict[self.selected_amine]
        self.select_plate_widget.options = self.amine_to_plate_dict[self.selected_inchi]
        self.selected_plate = self.amine_to_plate_dict[self.selected_inchi][0]
        self.selected_vial = self.xrd_files[self.selected_plate][0]
        self.select_xrd()

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
            self.exp_details.populate(None, None)
        else:
            vial_id = self.selected_plate + '_' + self.selected_vial
            filename = vial_id + '.xy'
            sel_exp = self.data[self.data['RunID_vial'] == vial_id].iloc[0]
            amine = self.chem_dict[self.selected_inchi]
            self.exp_details.populate(sel_exp, amine)
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


class ExpDetails(HBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.experiment_table = HTML()
        self.experiment_table.value = "Please click on a point"
        "to explore experiment details"
        self.image_folder = Path.cwd() / Path('data/images')

        with open("{}/{}".format(self.image_folder, 'not_found.png'), "rb") as f:
            b = f.read()
            image_data = b

        self.image_widget = Image(
            value=image_data,
            layout=Layout(height='400px', width='650px')
        )
        self.children = [self.experiment_table, self.image_widget]

    def generate_table(self, row, columns, column_names):
        table_html = """ <table border="1" style="width:100%;">
                        <tbody>"""
        for i, column in enumerate(columns):
            if isinstance(row[column], str):
                value = row[column].split('_')[-1]
            else:
                value = np.round(row[column], decimals=3)
            table_html += """
                            <tr>
                                <td style="padding: 8px;">{}</td>
                                <td style="padding: 8px;">{}</td>
                            </tr>
                          """.format(column_names[i], value)
        table_html += """
                        </tbody>
                        </table>
                        """
        return table_html

    def populate(self, selected_experiment, amine):
        img_filepath = Path.cwd() / Path(self.image_folder, 'not_found.png')
        table_value = "Selected XRD is representative of the plate"

        if type(selected_experiment) != type(None):
            columns = ['RunID_vial', '_rxn_M_acid', '_rxn_M_inorganic', '_rxn_M_organic',
                       '_rxn_mixingtime1S', '_rxn_mixingtime2S',
                       '_rxn_reactiontimeS', '_rxn_stirrateRPM',
                       '_rxn_temperatureC_actual_bulk']
            column_names = ['Well ID', 'Formic Acid [FAH]', 'Lead Iodide [PbI2]',
                            #'Dimethylammonium Iodide [Me2NH2I]',
                            '{}'.format(amine),
                            'Mixing Time Stage 1 (s)', 'Mixing Time Stage 2 (s)',
                            'Reaction Time (s)', 'Stir Rate (RPM)',
                            'Temperature (C)']
            name = selected_experiment['RunID_vial']
            img_filename = name+'_side.jpg'
            img_filepath = Path.cwd() / Path(self.image_folder, img_filename)
            prefix = '_'.join(name.split('_')[:-1])
            table_value = '<p>Plate ID:<br> {}</p>'.format(
                prefix) + self.generate_table(selected_experiment.loc[columns],
                                              columns, column_names)

        with open(img_filepath, "rb") as f:
            b = f.read()
            #self.image_data[img_filename] = b
            self.image_widget.value = b

        self.experiment_table.value = table_value


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
