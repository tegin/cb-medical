/* @odoo-module **/
import {NameAndSignature} from "@web/core/signature/name_and_signature";
import {SignatureDialog} from "@web/core/signature/signature_dialog";
import {SignatureField} from "@web/views/fields/signature/signature_field";
import {registry} from "@web/core/registry";
import {renderToString} from "@web/core/utils/render";

class MedicalNameAndSignature extends NameAndSignature {
    setup() {
        super.setup();
    }
    onInputSignName() {
        super.onInputSignName(...arguments);
        if (this.state.signMode !== "auto") {
            this.drawCurrentName();
        }
    }
    getSVGText(font, text, width, height) {
        const svg = renderToString("medical_signature_storage.sign_svg_text", {
            width: width,
            height: height,
            font: font,
            text: text.split("\n"),
            type: this.props.signatureType,
            color: this.props.fontColor,
        });
        console.log(svg);

        return "data:image/svg+xml," + encodeURI(svg);
    }
    onClickSignDrawClear() {
        super.onClickSignDrawClear(...arguments);
        this.drawCurrentName();
    }
}
MedicalNameAndSignature.template = "medical_signature_storage.MedicalNameAndSignature";

export class MedicalSignatureDialog extends SignatureDialog {}
MedicalSignatureDialog.components = {
    ...SignatureDialog.components,
    NameAndSignature: MedicalNameAndSignature,
};

export class MedicalSignatureField extends SignatureField {
    onClickSignature() {
        if (!this.props.readonly) {
            const nameAndSignatureProps = {
                mode: "draw",
                displaySignatureRatio: 3,
                signatureType: "signature",
                noInputName: true,
            };
            const {fullName, record} = this.props;
            let defaultName = "";
            if (fullName) {
                let signName = "";
                const fullNameData = record.data[fullName];
                if (record.fields[fullName].type === "many2one") {
                    // If m2o is empty, it will have falsy value in recordData
                    signName = fullNameData && fullNameData[1];
                } else {
                    signName = fullNameData;
                }
                defaultName = signName === "" ? undefined : signName;
            }

            nameAndSignatureProps.defaultFont = this.props.defaultFont;

            const dialogProps = {
                defaultName,
                nameAndSignatureProps,
                uploadSignature: (signature) => this.uploadSignature(signature),
            };
            this.dialogService.add(MedicalSignatureDialog, dialogProps);
        }
    }
}

registry.category("fields").add("medical_signature", MedicalSignatureField);
