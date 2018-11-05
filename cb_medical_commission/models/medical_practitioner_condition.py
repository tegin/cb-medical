from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MedicalPractitionerCondition(models.Model):
    _name = 'medical.practitioner.condition'
    _description = 'Practitioner condition'

    practitioner_id = fields.Many2one(
        'res.partner',
        required=True,
        readonly=True,
    )
    service_id = fields.Many2one('product.product', )
    procedure_service_id = fields.Many2one('product.product', )
    variable_fee = fields.Float(string='Variable fee (%)', default='0.0', )
    fixed_fee = fields.Float(string='Fixed fee', default='0.0', )
    active = fields.Boolean(default=True, required=True, )

    @api.constrains('practitioner_id', 'service_id', 'procedure_service_id')
    def check_condition(self):
        for rec in self.filtered(lambda r: r.active):
            if self.search([
                ('practitioner_id', '=', rec.practitioner_id.id),
                ('service_id', '=', rec.service_id.id or False),
                ('procedure_service_id', '=',
                 rec.procedure_service_id.id or False),
                ('active', '=', True),
                ('id', '!=', rec.id)
            ], limit=1):
                raise ValidationError(_(
                    'Only one condition is allowed for practitioner, service '
                    'and procedure service'
                ))

    @api.multi
    def get_condition(self, procedure):
        condition = self.filtered(
            lambda r: (
                r.service_id == procedure.service_id and
                r.procedure_service_id == procedure.procedure_service_id
            ))
        if condition:
            return condition[0]
        condition = self.filtered(
            lambda r: (
                r.service_id == procedure.service_id and
                not r.procedure_service_id
            ))
        if condition:
            return condition[0]
        condition = self.filtered(
            lambda r: (
                not r.service_id and
                r.procedure_service_id == procedure.procedure_service_id
            ))
        if condition:
            return condition[0]
        condition = self.filtered(
            lambda r: not r.service_id and not r.procedure_service_id
        )
        if condition:
            return condition[0]
        return False
