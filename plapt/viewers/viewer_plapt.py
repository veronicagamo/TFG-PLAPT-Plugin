import os
import json
import webbrowser
import pyworkflow.viewer as pwviewer
from pyworkflow.protocol import params
from jinja2 import Template
from plapt.protocols.protocol_plapt import ProtChemPLAPT

class JsonTableViewer(pwviewer.Viewer):
    _label = 'Ligand-Target Interaction Viewer'
    _environments = [pwviewer.DESKTOP_TKINTER]
    _targets = []

    def _visualize(self, json_file, **kwargs):
        json_path = os.path.abspath(json_file)
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"JSON file not found: {json_path}")

        data = self.read_json(json_path)
        if not data:
            raise ValueError(f"No data found in JSON file: {json_path}")

        html_content = self.create_html(data)
        html_path = self.save_html(html_content, json_path)
        self.display_html(html_path)

    def read_json(self, json_path):
        with open(json_path, 'r') as f:
            data = json.load(f)
        return data

    def create_html(self, data):
        template = Template("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Ligand-Target Interaction Data</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #4CAF50; color: white; }
                .high { background-color: #ff6666; }
                .good { background-color: #ffcc66; }
                .moderate { background-color: #66ccff; }
            </style>
        </head>
        <body>
            <h2>Ligand-Target Interaction Data</h2>
            <table>
                <tr>
                    <th>SMILES</th>
                    <th>pKd</th>
                    <th>Affinity (µM)</th>
                    <th>Interpretation</th>
                </tr>
                {% for entry in data %}
                <tr class="{{ entry.classification }}">
                    <td>{{ entry.molecule }}</td>
                    <td>{{ entry.neg_log10_affinity_M }}</td>
                    <td>{{ "{:.3f}".format(entry.affinity_uM) }}</td>
                    <td>{{ entry.interpretation }}</td>
                </tr>
                {% endfor %}
            </table>
        </body>
        </html>
        """)

        # Process classification based on pKd values
        for entry in data:
            if entry['neg_log10_affinity_M'] > 8:
                entry['classification'] = 'high'
                entry['interpretation'] = 'High Affinity'
            elif entry['neg_log10_affinity_M'] > 6:
                entry['classification'] = 'good'
                entry['interpretation'] = 'Good Affinity'
            else:
                entry['classification'] = 'moderate'
                entry['interpretation'] = 'Moderate Affinity'

        return template.render(data=data)

    def save_html(self, html_content, json_path):
        html_path = os.path.splitext(json_path)[0] + '.html'
        with open(html_path, 'w') as f:
            f.write(html_content)
        return html_path

    def display_html(self, html_path):
        webbrowser.open_new_tab(f'file://{os.path.realpath(html_path)}')


class ProtChemInteractionViewer(pwviewer.ProtocolViewer):
    """ Viewer for ligand-target interaction analysis """
    _label = 'PLAPT Viewer'
    _targets = [ProtChemPLAPT]

    def __init__(self, **args):
        super().__init__(**args)

    def _defineParams(self, form):
        form.addSection(label='View Interaction Data')
        group_json = form.addGroup('JSON Data')
        group_json.addParam('displayJson', params.LabelParam,
                            label='Open JSON File:',
                            help='Show ligand-target interaction data.')

    def _getVisualizeDict(self):
        return {
            'displayJson': self._showJson,
        }

    def _showJson(self, paramName=None):
        json_file = self.getJsonFile()
        return JsonTableViewer(project=self.getProject())._visualize(json_file)

    def getJsonFile(self):
        return self.protocol._getExtraPath("results.json")
