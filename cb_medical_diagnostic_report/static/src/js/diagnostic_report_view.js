odoo.define("diagnostic_report.DiagnosticReportView", function (require) {
    "use strict";

    var registry = require("web.view_registry");

    var FormView = require("web.FormView");

    var DiagnosticReportController = require("diagnostic_report.DiagnosticReportController");

    var DiagnosticReportRenderer = require("diagnostic_report.DiagnosticReportRenderer");

    var DiagnosticReportView = FormView.extend({
        config: _.extend({}, FormView.prototype.config, {
            Controller: DiagnosticReportController,
            Renderer: DiagnosticReportRenderer,
        }),
    });

    registry.add("diagnostic_report", DiagnosticReportView);

    return DiagnosticReportView;
});
