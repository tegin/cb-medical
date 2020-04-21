# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Cb Medical Constants",
    "summary": """
        CB Medical Constants""",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca",
    "website": "www.creublanca.es",
    "external_dependencies": {"python": ["bokeh"]},
    "depends": [
        "medical_administration_encounter",
        "web_widget_bokeh_chart",
        "web_widget_color",
    ],
    "data": [
        "views/medical_observation_code.xml",
        "views/medical_observation_uom.xml",
        "data/server_data.xml",
        "security/ir.model.access.csv",
        "views/medical_encounter.xml",
    ],
}
