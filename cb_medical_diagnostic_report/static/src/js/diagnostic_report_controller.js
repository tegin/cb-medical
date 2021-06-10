/* global Uint8Array base64js*/
odoo.define("diagnostic_report.DiagnosticReportController", function(require) {
    "use strict";

    var FormController = require("web.FormController");

    var DiagnosticReportController = FormController.extend({
        events: _.extend(FormController.prototype.events, {
            paste: "_onPaste",
        }),
        _onPaste: function(e) {
            if (this.mode !== "readonly") {
                return;
            }
            var clipboardData = e.originalEvent.clipboardData;
            var self = this;
            if (clipboardData && clipboardData.items && clipboardData.items.length) {
                var item = clipboardData.items[0];
                if (item.kind === "file" && item.type.indexOf("image/") !== -1) {
                    event.preventDefault();
                    var file = item.getAsFile();
                    self._generateImage(file, e);
                }
            }
        },
        _handle_drop_items: function(drop_items, e) {
            if (this.mode !== "readonly") {
                return this._super(drop_items, e);
            }
            var new_drop_items = [];
            var self = this;
            _.each(drop_items, function(file) {
                if (self._isImage(file)) {
                    self._generateImage(file, e);
                } else {
                    new_drop_items.push(file);
                }
            });
            return this._super(new_drop_items, e);
        },
        _generateImage: function(file, e) {
            var self = this;
            if (!file || !(file instanceof Blob)) {
                return;
            }
            var reader = new FileReader();
            reader.onloadend = self.proxy(
                _.partial(
                    self._generateAttachmentImage,
                    file,
                    reader,
                    e,
                    self.renderer.state.model,
                    self.renderer.state.res_id
                )
            );
            reader.onerror = self.proxy("_file_reader_error_handler");
            reader.readAsArrayBuffer(file);
        },
        _generateAttachmentImage: function(file, reader, e, res_model, res_id) {
            var self = this;
            return this._rpc({
                model: res_model,
                method: "add_image_attachment",
                args: [[res_id]],
                kwargs: {
                    name: file.name,
                    datas: base64js.fromByteArray(new Uint8Array(reader.result)),
                },
            }).then(function() {
                self.trigger_up("reload");
            });
        },
        _isImage: function(item) {
            if (item.type.indexOf("image/") !== -1) {
                return true;
            }
            return false;
        },
    });

    return DiagnosticReportController;
});
