from odoo import models


class MedicalCoverageAgreementItem(models.Model):
    _inherit = 'medical.coverage.agreement.item'

    def _check_authorization(self, **kwargs):
        res = super()._check_authorization(**kwargs)
        res.update({
            'authorization_checked': kwargs.get('authorization_checked', False)
        })
        if (
            not kwargs.get('authorization_checked', False) and
            self.authorization_method_id.check_required
        ):
            res['authorization_status'] = 'pending'
        return res
