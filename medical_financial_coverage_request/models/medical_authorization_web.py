# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MedicalAuthorizationWeb(models.Model):

    _name = 'medical.authorization.web'
    _description = 'Authorization Web'

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    link = fields.Char()
    notes = fields.Text()
    authorization_method_ids = fields.One2many(
        'medical.authorization.method',
        inverse_name='authorization_web_id',
        readonly=True
    )

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        for record in self:
            record.authorization_method_ids.write({
                'integration_information': record.link,
                'method_information': record.notes,
            })
        return res
