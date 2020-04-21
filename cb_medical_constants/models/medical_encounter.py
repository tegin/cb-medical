# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
import requests

from bokeh.plotting import figure, ColumnDataSource
from bokeh.embed import components
from bokeh.models import LinearAxis, Range1d, HoverTool, Label
from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import UserError

TOOLTIPS = [(_("date"), "@{dates_string}"), (_("value"), "@{y}")]


class MedicalEncounter(models.Model):
    _inherit = "medical.encounter"

    constants_chart = fields.Text(
        string="Bokeh Chart", store=False, compute="_compute_constants_chart"
    )

    @api.depends()
    def _compute_constants_chart(self):
        import logging

        logging.info("Computing")
        for record in self:
            record.constants_chart = record._get_constants_chart()

    @api.multi
    def get_constants_chart(self):
        self.ensure_one()
        action = self.env.ref(
            "cb_medical_constants.medical_encounter_action"
        ).read()[0]
        action["res_id"] = self.id
        return action

    def _get_constants_chart(self):
        lang_code = self.env.context.get("lang") or "en_US"
        language = self.env["res.lang"].search([("code", "=", lang_code)])
        date_format = "%s %s" % (language.date_format, language.time_format)
        integration_codes = (
            self.env["medical.observation.code"]
            .search([])
            .mapped("integration_code")
        )
        path = "%s%s" % (
            self.env["ir.config_parameter"].get_param(
                "medical.constants.server"
            ),
            self.env["ir.config_parameter"].get_param(
                "medical.constants.path"
            ),
        )
        response = requests.post(
            path,
            json={
                # "encounter_id": self.id,
                # "measure_ids": medical_measures,
                "encounter_id": 1503,
                "observation_codes": integration_codes,
            },
        )
        response.raise_for_status()
        constant_measurements = json.loads(response.content.decode("utf-8"))
        if constant_measurements["observations"]:
            chart = figure(
                background_fill_color="white",
                plot_height=500,
                plot_width=800,
                x_axis_label=_("Measurements"),
                x_axis_location="below",
                x_axis_type="datetime",
            )
            chart.yaxis.visible = False
            used_uoms = []
            for key in constant_measurements["observations"].keys():
                measure_id = self.env["medical.observation.code"].search(
                    [("integration_code", "=", str(key))]
                )
                sorted_dict = sorted(
                    constant_measurements["observations"][key],
                    key=lambda r: r["observation_date"],
                )
                dates = []
                values = []
                dates_string = []
                obs_uom = measure_id.default_observation_uom
                obs_code = -1
                if len(sorted_dict):
                    obs_code = sorted_dict[0]["observation_uom"]
                    obs_uom = self.env["medical.observation.uom"].search(
                        [("integration_code", "=", obs_code)]
                    )

                if not obs_uom:
                    raise UserError(_("UOM with code %s not found") % obs_code)

                for m in sorted_dict:
                    values.append(m["observation_value"])
                    observation_date = datetime.fromtimestamp(
                        m["observation_date"]
                    )
                    dates.append(observation_date)
                    dates_string.append(observation_date.strftime(date_format))

                source = ColumnDataSource(
                    data=dict(x=dates, y=values, dates_string=dates_string)
                )

                if obs_uom.id not in used_uoms:
                    chart.extra_y_ranges[
                        str(obs_uom.integration_code)
                    ] = Range1d(start=measure_id.y_min, end=measure_id.y_max)
                    chart.add_layout(
                        LinearAxis(
                            y_range_name=str(obs_uom.integration_code),
                            axis_line_width=1,
                        ),
                        "left",
                    )
                    chart.add_layout(Label(text=obs_uom.symbol), "above")
                    used_uoms.append(obs_uom.id)

                legend_name = "%s (%s)" % (measure_id.name, obs_uom.symbol)
                chart.line(
                    "x",
                    "y",
                    source=source,
                    line_width=2,
                    line_color=measure_id.color,
                    y_range_name=str(obs_uom.integration_code),
                    legend=legend_name,
                )
                cr = chart.circle(
                    "x",
                    "y",
                    source=source,
                    size=10,
                    color=measure_id.color,
                    y_range_name=str(obs_uom.integration_code),
                    legend=legend_name,
                )

                chart.add_tools(
                    HoverTool(tooltips=TOOLTIPS, callback=None, renderers=[cr])
                )
            chart.legend.click_policy = "hide"
            chart.legend.label_text_font_size = "7pt"
            script, div = components(chart)
            return "%s%s" % (div, script)
        else:
            return False
