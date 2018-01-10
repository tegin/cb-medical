# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class WizardSalePreinvoiceGroup(models.TransientModel):
    _name = "wizard.sale.preinvoice.group.barcode"
    _inherit = "barcodes.barcode_events_mixin"

    preinvoice_group_id = fields.Many2one(
        'sale.preinvoice.group',
        required=True
    )
    line_ids = fields.One2many(
        string='Validated lines',
        comodel_name='sale.order.line',
        related='preinvoice_group_id.line_ids'
    )
    status = fields.Char(readonly=1)

    def on_barcode_scanned(self, barcode):
        encounter_id = self.env['medical.encounter'].search([
            ('internal_identifier', '=', barcode)
        ])
        if not encounter_id:
            self.status = 'Encounter not found'
        lines = self.line_ids.filtered(
            lambda r: r.encounter_id.id == encounter_id.id
        )
        if not lines:
            self.status = 'Lines not found'
        for line in lines:
            self.preinvoice_group_id.validate_line(line)
            self.status = 'OK'
        self.preinvoice_group_id._compute_lines()
