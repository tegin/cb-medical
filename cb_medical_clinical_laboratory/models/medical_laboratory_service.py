# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MedicalLaboratoryService(models.Model):
    _name = 'medical.laboratory.service'
    _description = 'Laboratory service'
    _rec_name = 'code'

    code = fields.Char(
        required=True,
    )
    name = fields.Char(

    )
    delay = fields.Integer()
    laboratory_code = fields.Char(
        required=True,
    )
    service_price_ids = fields.One2many(
        'medical.laboratory.service.price',
        inverse_name='laboratory_service_id',
        readonly=True,
    )
    active = fields.Boolean(
        default=True,
        required=True,
    )

    _sql_constraints = [(
        'unique_laboratory_code', 'UNIQUE(laboratory_code)',
        'Laboratory Code must be unique'
    )]


class MedicalLaboratoryServicePrice(models.Model):
    _name = 'medical.laboratory.service.price'
    _description = 'Laboratory service price list'

    laboratory_service_id = fields.Many2one(
        'medical.laboratory.service',
        required=True,
    )
    laboratory_code = fields.Char(
        required=True,
        string="Coverage code"
    )
    amount = fields.Float(required=True,)
    cost = fields.Float()

    _sql_constraints = [(
        'unique_code', 'UNIQUE(laboratory_code, laboratory_service_id)',
        'Code must be unique on a service'
    )]
