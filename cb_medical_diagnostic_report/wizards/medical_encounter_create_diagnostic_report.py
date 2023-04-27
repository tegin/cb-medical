# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalEncounterCreateDiagnosticReport(models.TransientModel):

    _inherit = "medical.encounter.create.diagnostic.report"

    template_id = fields.Many2one(
        domain="['|','&', ('template_type','=','general'), "
        "'|', ('medical_department_id','=',False), "
        "('medical_department_id.user_ids','=',uid),"
        "'&', ('create_uid','=',uid), ('template_type', '=', 'user')]"
    )
