# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval


class MedicalEncounter(models.Model):

    _inherit = "medical.encounter"

    # Make it selection? Or just text of whatever?
    medical_process_description = fields.Text(string="Medical Process Description")

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        readonly=0,
        tracking=True,
    )

    def medical_impresion_tree_view_action_old(self):
        self.ensure_one()
        view_id = self.env.ref(
            "medical_clinical_impression.medical_clinical_impression_tree_view"
        ).id
        ctx = dict(self._context)
        ctx["default_patient_id"] = self.id

        return {
            "type": "ir.actions.act_window",
            "res_model": "medical.clinical.impression",
            "name": _("Medical Impression"),
            "view_type": "list",
            "view_mode": "tree",
            "views": [(view_id, "list")],
            "context": ctx,
            "domain": [("encounter_id", "=", self.id)],
        }

    def medical_impresion_tree_view_action(self):
        result = self.env["ir.actions.act_window"]._for_xml_id(
            "medical_clinical_impression."
            "medical_clinical_impression_act_window"
        )
        ctx_dict = {}
        ctx_dict["default_encounter_id"] = self.id
        ctx_dict["search_default_filter_not_cancelled"] = True
        ctx_dict["active_id"] = self.patient_id.id
        domain = expression.AND(
            [
                safe_eval(result["domain"], ctx_dict),
                [
                    ("encounter_id", "=", self.id),
                    ("patient_id", "=", self.patient_id.id),
                ],
            ]
        )
        result["domain"] = domain
        result["context"] = ctx_dict
        return result
