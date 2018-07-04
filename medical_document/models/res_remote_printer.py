from odoo import fields, models


class ResRemotePrinter(models.Model):
    _inherit = 'res.remote.printer'

    printer_usage = fields.Selection(selection_add=[
        ('internal', 'Internal')
    ])
