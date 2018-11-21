from odoo import models


class MedicalCoverageAgreementItem(models.Model):
    _inherit = 'medical.coverage.agreement.item'

    def _check_authorization(self, method, **kwargs):
        res = super()._check_authorization(method, **kwargs)
        res.update({
            'authorization_checked': kwargs.get('authorization_checked', False)
        })
        if (
            not kwargs.get('authorization_checked', False) and
            method.check_required
        ):
            res['authorization_status'] = 'pending'
        return res
