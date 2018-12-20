from odoo import api, fields, models


class MedicalCoverageAgreementTemplate(models.TransientModel):
    _name = 'medical.coverage.agreement.template'

    agreement_id = fields.Many2one(
        'medical.coverage.agreement',
        readonly=True,
        required=True,
    )
    template_id = fields.Many2one(
        'medical.coverage.agreement',
        domain=[('is_template', '=', True)]
    )
    set_items = fields.Boolean(default=False)

    @api.multi
    def run(self):
        self.ensure_one()
        self.agreement_id.set_template(self.template_id, self.set_items)
