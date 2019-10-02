from odoo import api, models


class MedicalRequest(models.AbstractModel):
    _inherit = "medical.request"

    @api.model
    def _ignore_child_states(self):
        return False

    def _check_any_child_state(self, expected_states):
        models = [self.env[model] for model in self._get_request_models()]
        fieldname = self._get_parent_field_name()
        for model in models:
            if model._ignore_child_states():
                continue
            childs = model.search(
                [
                    (fieldname, "in", self.ids),
                    ("parent_id", "in", self.ids),
                    ("parent_model", "=", self._name),
                    ("state", "!=", "cancelled"),
                ]
            )
            if childs.filtered(lambda r: r.state in expected_states):
                return True
        return False

    def _check_child_state(self, expected_states, with_childs=True):
        models = [self.env[model] for model in self._get_request_models()]
        fieldname = self._get_parent_field_name()
        has_childs = False
        for model in models:
            if model._ignore_child_states():
                continue
            childs = model.search(
                [
                    (fieldname, "in", self.ids),
                    ("parent_id", "in", self.ids),
                    ("parent_model", "=", self._name),
                    ("state", "!=", "cancelled"),
                ]
            )
            if childs:
                has_childs = True
            if childs.filtered(lambda r: r.state not in expected_states):
                return False
        if not has_childs and with_childs:
            return False
        return True

    def _get_expected_states(self):
        return {
            "1": {
                "state": "draft",
                "check_function": "_check_any_child_state",
                "check_args": {"expected_states": ["active", "completed"]},
                "function": "draft2active",
                "function_args": {},
            },
            "2": {
                "state": "active",
                "check_function": "_check_child_state",
                "check_args": {"expected_states": ["completed"]},
                "function": "active2completed",
                "function_args": {},
            },
        }

    def check_state(self):
        self.ensure_one()
        if self.state == "cancelled":
            return
        states = self._get_expected_states() or {}
        for key in sorted(states.keys()):
            state = states[key]
            if self.state == state["state"] and getattr(
                self, state["check_function"]
            )(**state.get("check_args", {})):
                getattr(self, state["function"])(
                    **state.get("function_args", {})
                )

    def _check_parent_state(self):
        for rec in self.filtered(lambda r: r.parent_model and r.parent_id):
            self.env[rec.parent_model].browse(rec.parent_id).check_state()

    @api.multi
    def draft2active(self):
        res = super().draft2active()
        self._check_parent_state()
        return res

    @api.multi
    def active2suspended(self):
        res = super().active2suspended()
        self._check_parent_state()
        return res

    @api.multi
    def active2completed(self):
        res = super().active2completed()
        self._check_parent_state()
        return res

    @api.multi
    def active2error(self):
        res = super().active2error()
        self._check_parent_state()
        return res

    @api.multi
    def reactive(self):
        res = super().reactive()
        self._check_parent_state()
        return res

    @api.multi
    def cancel(self):
        res = super().cancel()
        self._check_parent_state()
        return res
