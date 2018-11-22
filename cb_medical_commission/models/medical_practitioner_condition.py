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
    center_ids = fields.Many2many(
        'res.partner',
        domain=[('is_center', '=', True)]
    )
    service_id = fields.Many2one(
        'product.product',
        domain=[('type', '=', 'service')],
    )
    procedure_service_id = fields.Many2one(
        'product.product',
        domain=[('activity_definition_ids', '!=', False)],
    )
    variable_fee = fields.Float(string='Variable fee (%)', default='0.0', )
    fixed_fee = fields.Float(string='Fixed fee', default='0.0', )
    active = fields.Boolean(default=True, required=True, )

    @api.constrains('practitioner_id', 'service_id', 'procedure_service_id')
    def check_condition(self):
        for rec in self.filtered(lambda r: r.active):
            domain = [
                ('practitioner_id', '=', rec.practitioner_id.id),
                ('service_id', '=', rec.service_id.id or False),
                ('procedure_service_id', '=',
                 rec.procedure_service_id.id or False),
                ('active', '=', True),
                ('id', '!=', rec.id)
            ]
            for center in rec.center_ids.ids or [False]:
                if self.search(
                    domain + [('center_ids', '=', center)], limit=1
                ):
                    raise ValidationError(_(
                        'Only one condition is allowed for practitioner, '
                        'service and procedure service'
                    ))

    def get_functions(self, procedure):
        return [
            lambda r: (
                r.service_id == procedure.service_id and
                r.procedure_service_id == procedure.procedure_service_id and
                procedure.procedure_request_id.center_id in r.center_ids
            ),
            lambda r: (
                r.service_id == procedure.service_id and
                r.procedure_service_id == procedure.procedure_service_id and
                not r.center_ids
            ),
            lambda r: (
                r.service_id == procedure.service_id and
                not r.procedure_service_id and
                procedure.procedure_request_id.center_id in r.center_ids
            ),
            lambda r: (
                r.service_id == procedure.service_id and
                not r.procedure_service_id and
                not r.center_ids
            ),
            lambda r: (
                not r.service_id and
                r.procedure_service_id == procedure.procedure_service_id and
                procedure.procedure_request_id.center_id in r.center_ids
            ),
            lambda r: (
                not r.service_id and
                r.procedure_service_id == procedure.procedure_service_id and
                not r.center_ids
            ),
            lambda r: (
                not r.service_id and not r.procedure_service_id and
                procedure.procedure_request_id.center_id in r.center_ids),
            lambda r: (
                not r.service_id and not r.procedure_service_id and
                not r.center_ids),
        ]

    @api.multi
    def get_condition(self, procedure):
        for function in self.get_functions(procedure):
            condition = self.filtered(function)
            if condition:
                return condition[0]
        return False
