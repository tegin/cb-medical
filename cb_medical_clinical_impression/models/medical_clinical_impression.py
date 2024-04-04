# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json
from datetime import timedelta

from odoo import api, fields, models


class MedicalClinicalImpression(models.Model):
    _inherit = "medical.clinical.impression"

    auto_validated = fields.Boolean()
    observation_ids = fields.One2many(
        "medical.observation", inverse_name="impression_id"
    )
    observation_data = fields.Serialized(
        compute="_compute_observation_data", inverse="_inverse_observation_data"
    )

    def _inverse_observation_data(self):
        done = []
        to_do = self.observation_ids.ids
        for _key, value in self.observation_data.items():
            if value["id"]:
                self.observation_ids.filtered(lambda r: r.id == value["id"]).write(
                    {
                        "value_str": value["value_str"],
                        "value_int": value["value_int"],
                        "value_float": value["value_float"],
                        "value_bool": value["value_bool"],
                        "value_selection": value["value_selection"],
                        "value_date": value["value_date"],
                        "selection_options": value["selection_options"],
                    }
                )
                done.append(value["id"])
                continue
            observation = self.observation_ids.filtered(
                lambda r: r.concept_id.id == value["concept_id"]
            )
            if observation:
                observation.write(
                    {
                        "value_str": value["value_str"],
                        "value_int": value["value_int"],
                        "value_float": value["value_float"],
                        "value_bool": value["value_bool"],
                        "value_selection": value["value_selection"],
                        "value_date": value["value_date"],
                        "selection_options": value["selection_options"],
                    }
                )
                done.append(observation.id)
                continue
            self.write(
                {
                    "observation_ids": [
                        (
                            0,
                            0,
                            {
                                "patient_id": self.patient_id.id,
                                "name": value["name"],
                                "concept_id": value["concept_id"],
                                "uom_id": value["uom_id"],
                                "value_type": value["value_type"],
                                "value_str": value["value_str"],
                                "value_int": value["value_int"],
                                "value_float": value["value_float"],
                                "value_bool": value["value_bool"],
                                "value_selection": value["value_selection"],
                                "value_date": value["value_date"],
                                "selection_options": value["selection_options"],
                            },
                        )
                    ]
                }
            )
        self.observation_ids.filtered(
            lambda r: r.id in to_do and r.id not in done
        ).unlink()

    @api.depends("observation_ids")
    def _compute_observation_data(self):
        for record in self:
            record.observation_data = json.dumps(record._get_observation_data())

    def _get_observation_data(self):
        return {o.id: o._get_impression_data() for o in self.observation_ids}

    def _set_template_values(self, template):
        result = super()._set_template_values(template)
        self.observation_data = json.dumps(
            {
                str(concept.id): {
                    "id": False,
                    "name": concept.concept_id.name,
                    "concept_id": concept.concept_id.id,
                    "value_type": concept.concept_id.value_type,
                    "value_float": False,
                    "value_int": False,
                    "value_date": False,
                    "value_bool": False,
                    "value_str": False,
                    "value_selection": False,
                    "selection_options": concept.concept_id.selection_options,
                    "uom_id": concept.concept_id.uom_id.id,
                    "uom": concept.concept_id.uom_id.name,
                }
                for concept in template.concept_ids
            }
        )
        return result

    def _cron_validate_clinical_impression(self, hours):
        to_validate = self.search(
            [
                ("fhir_state", "=", "in_progress"),
                (
                    "write_date",
                    "<",
                    fields.Datetime.now() + timedelta(hours=-hours),
                ),
            ]
        )
        for impression in to_validate:
            impression.with_user(impression.write_uid.id).validate_clinical_impression(
                auto_validated=True
            )

    def _validate_clinical_impression_fields(self, auto_validated=False, **kwargs):
        result = super()._validate_clinical_impression_fields(**kwargs)
        if auto_validated:
            result["auto_validated"] = True
        return result

    def action_create_clinical_impression_report(self):
        self.mapped("patient_id").ensure_one()
        self.mapped("specialty_id").ensure_one()
        report = self.env["medical.diagnostic.report"].create(
            self._create_diagnostic_report_vals()
        )
        return report.get_formview_action()

    def _create_diagnostic_report_vals(self):
        encounter = self[0].encounter_id
        return {
            "encounter_id": encounter.id,
            "patient_name": encounter.patient_id.name,
            "vat": encounter.patient_id.vat,
            "patient_age": self.env["medical.diagnostic.report.template"]._compute_age(
                encounter.patient_id
            ),
            "composition": self._get_report_composition(),
            "name": self[0].specialty_id.name,
            "lang": self.env.context.get("lang") or self.env.user.lang,
            "item_blocked": False,
            "with_conclusion": False,
            "with_observation": False,
            "with_composition": True,
        }

    def _get_report_composition(self):
        return self.env["ir.qweb"]._render(
            "cb_medical_clinical_impression.impression_to_diagnostic_report",
            {"impressions": self},
        )
