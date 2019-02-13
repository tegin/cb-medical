# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, _


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
        related='preinvoice_group_id.line_ids', readonly=True,
    )
    status = fields.Text(
        readonly=1,
        default="Start scanning",
    )
    status_state = fields.Integer(
        default=0,
        readonly=1,
    )
    encounter_id = fields.Many2one(
        'medical.encounter',
        computed='on_barcode_scanned',
    )
    processed_lines = fields.Many2many(
        'sale.order.line',
        computed='on_barcode_scanned',
    )

    def _show_lines(self):
        show_lines = _("The following lines have been processed from "
                       "Encounter %s:\n") % self.encounter_id.display_name
        for line in self.processed_lines:
            show_lines = "%s %s [%s]\n" % (
                show_lines, line.product_id.name, line.order_id.name)
        return show_lines + _("Scan the next barcode or press Close to "
                              "finish scanning.")

    def on_barcode_scanned(self, barcode):
        self.encounter_id = self.env['medical.encounter'].search([
            ('internal_identifier', '=', barcode)
        ])
        if not self.encounter_id:
            self.status = _("Barcode %s does not correspond to any "
                            "Encounter. Try with another barcode or "
                            "press Close to finish scanning.") % barcode
            self.status_state = 1
            return
        self.processed_lines = self.line_ids.filtered(
            lambda r: r.encounter_id.id == self.encounter_id.id and not
            r.is_validated
        )
        if not self.processed_lines:
            self.status = (
                _(
                    "The Encounter %s does not belong to this pre-invoice "
                    "group. Try with another barcode or press Close to finish "
                    "scanning."
                ) % self.encounter_id.display_name
            )
            self.status_state = 1
            return
        for line in self.processed_lines:
            self.preinvoice_group_id.validate_line(line)
            self.status = self._show_lines()
            self.status_state = 0
        self.preinvoice_group_id._compute_lines()
