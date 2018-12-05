import re
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MedicalCoverage(models.Model):
    _inherit = 'medical.coverage'

    subscriber_required = fields.Boolean(
        related='coverage_template_id.subscriber_required',
        readonly=True,
    )
    subscriber_format = fields.Char(
        related='coverage_template_id.subscriber_format',
        readonly=True,
    )

    @api.constrains('subscriber_id')
    def check_subscriber(self):
        for rec in self:
            if rec.subscriber_required and not self.env.context(
                'no_check_subscriber', False
            ):
                match = re.match(rec.subscriber_format, rec.subscriber_id)
                if not match:
                    raise ValidationError(_(
                        'Subscriber id is not valid'
                    ))
