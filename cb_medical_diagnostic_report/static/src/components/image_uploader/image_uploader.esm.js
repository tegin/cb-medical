/** @odoo-module **/

import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

const {Component, useEffect, useState, useRef} = owl;

export class PasteImageField extends Component {
    async setup() {
        super.setup();
        this.notification = useService("notification");
        this.orm = useService("orm");
        this.state = useState({
            isActive: false,
        });
        this.ref = useRef("pasteImageFieldElement");
        useEffect(() => {
            const handleClickOutside = (event) => {
                if (!this.ref.el.contains(event.target)) {
                    this.state.isActive = false;
                }
            };
            // Listen clicks in all the documents
            document.addEventListener("click", handleClickOutside);
            // Remove the listener at dismount
            return () => document.removeEventListener("click", handleClickOutside);
        });
    }
    toggleColor() {
        // Change the state for the color
        this.state.isActive = !this.state.isActive;
    }
    onPaste(event) {
        if (
            event &&
            event.clipboardData &&
            event.clipboardData.items &&
            event.clipboardData.items.length
        ) {
            var item = event.clipboardData.items[0];
            if (item.kind === "file" && item.type.indexOf("image/") !== -1) {
                var fileItem = item.getAsFile();
                this._generateImage(fileItem);
            }
        }
    }
    _generateImage(fileItem) {
        if (!fileItem || !(fileItem instanceof Blob)) {
            return;
        }
        var reader = new FileReader();
        reader.onloadend = _.partial(
            this._generateAttachmentImage.bind(this),
            fileItem,
            reader
        );
        reader.readAsDataURL(fileItem);
    }
    async _generateAttachmentImage(file, reader) {
        await this.props.record.save();
        await this.orm.call(
            this.props.record.resModel,
            "add_image_attachment",
            [[this.props.record.resId]],
            {
                name: file.name,
                datas: reader.result.split(",")[1],
            }
        );
        await this.props.record.load();
        this.props.record.model.notify();
        this.notification.add(_t("Image added successfully"), {
            type: "success",
        });
    }
}
PasteImageField.template = "cb_medical_diagnostic_report.PasteImageField";
PasteImageField.components = {...Component.components};

registry.category("fields").add("paste_image", PasteImageField);
