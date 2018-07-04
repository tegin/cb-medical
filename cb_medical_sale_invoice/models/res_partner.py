from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    show_patient = fields.Boolean()
    show_subscriber = fields.Boolean()
    show_authorization = fields.Boolean()
