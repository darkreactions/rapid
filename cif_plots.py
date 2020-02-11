import os
from ipywidgets import Tab, SelectMultiple, Accordion, ToggleButton, VBox, HBox, HTML, Image, Button, Text, Dropdown
#from _plotly_future_ import v4_subplots
import plotly as py
import plotly.graph_objs as go
from ipywidgets import HBox, VBox, Image, Layout, HTML
import numpy as np
import pandas as pd
from IPython.display import display, Javascript, FileLink
#from notebook import notebookapp
import urllib.parse


class JsMolFigure:
    def __init__(self, cif_paths, fig_names, doi_values, widget_side=400):
        self.cif_paths = cif_paths
        self.fig_names = fig_names
        self.doi_values = doi_values
        self.widget_side = widget_side
        #base_url = list(notebookapp.list_running_servers())[0]['base_url']
        self.data_url = ''
        self.html = """
                    <!doctype html>
                    <html>
                    <head>
                    <meta content="text/html; charset=UTF-8" http-equiv="content-type">
                    <script
                        src="https://code.jquery.com/jquery-3.4.1.min.js"
                        integrity="sha256-CSXorXvZcTkaix6Yvo6HppcZGetbYMGWSFlBw8HfCJo="
                        crossorigin="anonymous"></script>

                    <script type="text/javascript" src="jsmol/JSmol.min.js"></script>
                    <style type="text/css">
                    .plot_div{{
                        display: inline;
                        margin: 15px;
                        float: left;
                    }}
                    </style>
                    """.format(self.data_url)
        jmol_html = ''
        jmol_script = ''
        for i, cif_path in enumerate(cif_paths):

            jmol_script += """
                    <!-- CSS Style Inline: -->
                    <style type="text/css">
                        /* Jmol Applet */
                        /* defines height, width and orientation of the Jmol div element */
                        #jmol_div_{1}{{
                            height: {5}px;
                            width:  {5}px;
                            margin: 5px;
                        }}
                    </style>
                    <!-- calls to jQuery and Jmol (inline) -->
                    <script type="text/javascript">
                        // Jmol readyFunction
                        // is called when Jmol is ready

                        jmol_isReady_{1} = function(applet) {{
                            Jmol._getElement(applet, "appletdiv").style.border="1px solid blue";
                        }}
                        // initialize Jmol Applet
                        var myJmol_{1} = "myJmol_{1}";
                        var Info_{1} = {{
                            width:   "100%",
                            height:  "100%",
                            color:   "#000000", //black
                            use:     "HTML5",
                            j2sPath: "./jsmol/j2s", 
                            jarPath: "./jsmol/java",
                            jarFile: "JmolAppletSigned.jar",
                            debug:   false,
                            readyFunction: jmol_isReady_{1},
                            script:  'load "{0}" ; hide _H;',
                            //script: 'load ":tylenol";',
                            allowJavaScript: true,
                            disableJ2SLoadMonitor: true,
                        }}
                        // jQuery ready functions
                        // is called when page has been completely loaded
                        $(document).ready(function() {{
                            console.log('Document is ready');
                            
                        }} )
                        function populate_jmol_{1}(){{
                            html_text = "<center><h3>{4}</h3></center>" + Jmol.getAppletHtml(myJmol_{1}, Info_{1});
                            html_text += Jmol.jmolButton(myJmol_{1},'load "{0}"  SUPERCELL {{2 2 2}}; hide _H;', "Show 2x2x2 supercell");
                            html_text += Jmol.jmolButton(myJmol_{1},'load "{0}"; hide _H;', "Reset");
                            // html_text += '<a href="{2}" target="_blank"><button> Download {4} CIF</button></a>'
                            $("#jmol_div_{1}").html(html_text);
                        }}
                        var lastPrompt=0;
                    </script>
                    """.format(cif_path, i, self.link_generator(self.fig_names[i], i), self.data_url, self.fig_names[i], self.widget_side)

            jmol_html += """
                        <div class='plot_div'>
                            <div id='jmol_div_{0}'> 
                                <div style="text-align: center;">
                                    <button type="button" onclick=populate_jmol_{0}()>Show Molecule</button>
                                </div> 
                            </div>
                        </div>
                        """.format(i)
        self.html += jmol_script + "</head> <body>" + jmol_html + "</body> </html>"

    def link_generator(self, fig_name, i):
        if 'HUTVAV' not in fig_name:
            return self.data_url + '/' + self.cif_paths[i]
        else:
            # return 'https://www.ccdc.cam.ac.uk/structures/Search?Ccdcid={}&DatabaseToSearch=Published'.format(fig_name)
            return 'https://www.ccdc.cam.ac.uk/structures/Search?Doi={}&DatabaseToSearch=Published'.format(urllib.parse.quote(self.doi_values[fig_name]))

    @property
    def plot(self):
        from IPython.display import HTML
        # from ipywidgets import HTML
        return HTML(self.html)

    @property
    def controls(self):
        get_supercell = ToggleButton(
            value=False,
            description='Get supercell',
            disabled=False,
            button_style='',
            tooltip='Click to show supercell'
        )
        get_supercell.observe(self.supercell_callback, 'value')

        run_command = Button(
            description='Run Command',
            disabled=False
        )
        run_command.on_click(self.run_cmd_callback)

        self.command_text = Text(
            value='spin on',
            placeholder='spin on',
            description='Command:',
            disabled=False
        )

        data_filter_vbox = VBox(
            [HBox([get_supercell]), HBox([self.command_text, run_command])])

        return data_filter_vbox

    def run_cmd_callback(self, b):
        if self.command_text.value:
            js_string = """Jmol.script(myJmol_{}, '{}');""".format(
                self.id, self.command_text.value)
            display(Javascript(js_string))

    def supercell_callback(self, state):
        if state.new:
            js_string = """Jmol.script(myJmol_{0}, 'load "{1}" supercell {{2 2 2}}');""".format(
                self.id, self.cif_path)
        else:
            js_string = """Jmol.script(myJmol_{0}, 'load "{1}"');""".format(
                self.id, self.cif_path)
        display(Javascript(js_string))
