# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestMgmtsystemIssue(TransactionCase):

    def setUp(self):
        super().setUp()
        self.partner_id = self.env['res.partner'].create({'name': 'Partner'})
        self.origin = self.env['mgmtsystem.nonconformity.origin'].create({
            'name': 'origin',
        })
        self.issue = self.env['mgmtsystem.quality.issue'].create({
            'name': 'Title',
            'description': 'Description',
            'partner_id': self.partner_id.id,
            'responsible_user_id': self.env.uid,
            'manager_user_id': self.env.uid,
            'origin': [(4, self.origin.id)]
        })

    def test_mgmtsystem_issue(self):
        self.issue.to_accepted()
        self.assertEqual(self.issue.state, 'ok')

        self.issue.back_to_pending()
        self.assertEqual(self.issue.state, 'pending')

        action = self.issue.to_nonconformity()
        self.assertEqual(self.issue.state, 'no_ok')
        self.assertEqual(self.issue.non_conformity_id.id, action['res_id'])
