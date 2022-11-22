# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import base64

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class MedicalDocumentReference(models.Model):
    # FHIR Entity: Document Reference
    # (https://www.hl7.org/fhir/documentreference.html)
    _name = "medical.document.reference"
    _description = "Medical Document Reference"
    _inherit = ["medical.request", "medical.document.language"]

    @api.model
    def _get_states(self):
        return {
            "draft": ("Draft", "draft"),
            "current": ("Current", "done"),
            "superseded": ("Superseded", "done"),
        }

    internal_identifier = fields.Char(string="Document reference")
    fhir_state = fields.Selection(
        required=True,
        tracking=True,
        default="draft",
    )
    document_type_id = fields.Many2one(
        "medical.document.type",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        ondelete="restrict",
    )
    document_type = fields.Selection(
        related="document_type_id.document_type",
        readonly=True,
        string="Document type reference",
    )
    document_template_id = fields.Many2one(
        "medical.document.template",
        readonly=True,
        copy=False,
        ondelete="restrict",
    )
    text = fields.Html(
        string="Document text",
        compute="_compute_text",
        inverse="_inverse_text",
        readonly=True,
        copy=False,
        sanitize=True,
        prefetch=False,
    )
    database_text = fields.Html(
        string="Database stored text",
        readonly=True,
        copy=False,
        sanitize=True,
        prefetch=False,
    )
    lang = fields.Selection(
        required=False,
        readonly=True,
        copy=False,
        states={"draft": [("readonly", False)]},
    )

    def _inverse_text(self):
        for record in self:
            record.database_text = record.text

    @api.depends("database_text")
    def _compute_text(self):
        for record in self:
            record.text = record._get_text()

    def _get_text(self):
        return self.database_text

    def _get_language(self):
        return self.lang or self.patient_id.lang

    def _get_internal_identifier(self, vals):
        return self.env["ir.sequence"].next_by_code("medical.document.reference") or "/"

    def action_view_request_parameters(self):
        return {
            "view": "medical_document.medical_document_reference_action",
            "view_form": "medical.document.reference.view.form",
        }

    def _get_parent_field_name(self):
        return "document_reference_id"

    def print(self):
        return self._print(self.print_action)

    def view(self):
        return self._print(self.view_action)

    def render(self):
        return self._print(self.render_report)

    def _print(self, action):
        self.ensure_one()
        if self.fhir_state == "draft":
            return self._draft2current(action)
        return action()

    def _render(self):
        return self.with_context(
            lang=self.lang
        ).document_type_id.report_action_id._render(self.id)

    def render_report(self):
        return base64.b64encode(self._render()[0])

    def view_action(self):
        if self.document_type == "action":
            return self.document_type_id.report_action_id.report_action(self)
        raise UserError(_("Function must be defined"))

    def _get_printer_usage(self):
        return "standard"

    def print_action(self):
        content, mime = self._render()
        behaviour = self.remote.with_context(
            printer_usage=self._get_printer_usage()
        ).get_printer_behaviour()
        if "printer" not in behaviour:
            return False
        printer = behaviour.pop("printer")
        return printer.with_context(
            print_report_name="doc_" + self.internal_identifier
        ).print_document(
            report=self.document_type_id.report_action_id,
            content=content,
            doc_format=mime,
        )

    def draft2current(self):
        return self._draft2current(self.print_action)

    def cancel(self):
        pass

    def draft2current_values(self):
        template_id = self.document_type_id.current_template_id.id
        return {
            "lang": self._get_language(),
            "document_template_id": template_id,
            "text": self.with_context(
                template_id=template_id, render_language=self._get_language()
            ).render_text(),
        }

    def change_lang(self, lang):
        text = self.with_context(
            template_id=self.document_template_id.id, render_language=lang
        ).render_text()
        return self.write({"lang": lang, "text": text})

    def _draft2current(self, action):
        self.ensure_one()
        if self.fhir_state != "draft":
            raise ValidationError(_("State must be draft"))
        self.write(self.draft2current_values())
        res = action()
        if res:
            self.write({"fhir_state": "current"})
        return res

    def render_text(self):
        if self.document_type == "action":
            template = self.document_template_id or self.env[
                "medical.document.template"
            ].browse(self._context.get("template_id", False))
            return template.render_template(self._name, self.id)
        raise UserError(_("Function must be defined"))

    def current2superseded_values(self):
        return {"fhir_state": "superseded"}

    def current2superseded(self):
        if self.filtered(lambda r: r.fhir_state != "current"):
            raise ValidationError(_("State must be Current"))
        self.write(self.current2superseded_values())
