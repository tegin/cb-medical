odoo.define("medical_queue_management.CopyClipboardListChar", function (require) {
    "use strict";

    var AbstractField = require("web.AbstractField");
    var registry = require("web.field_registry");

    var CopyClipboardListChar = AbstractField.extend({
        template: "medical_queue_management.CopyClipboardListChar",
        events: {
            "click .o_clipboard_list_view": "_onClipboardClick",
        },
        getValue: function () {
            if (typeof this.value === "object") {
                return this.value.data.display_name;
            }
            return this.value;
        },
        _onClipboardClick: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            navigator.clipboard.writeText(this.getValue());
        },
    });

    registry.add("CopyClipboardListChar", CopyClipboardListChar);
    return CopyClipboardListChar;
});
