odoo.define("cb_medical_clinical_impression.impression_component", function (require) {
    "use strict";
    const datepicker = require("web.datepicker");

    const ImpressionComponent = require("medical_clinical_impression/static/src/components/impression_component.js");
    const field_utils = require("web.field_utils");
    const {Component} = owl;
    const {onMounted, onPatched, onWillPatch, useRef} = owl.hooks;

    class ObservationComponent extends Component {
        setup() {
            super.setup();
            console.log(this);
            this.value = this.props.state.data.data.observation_data;
            this.datepicker = undefined;
            this.dateRef = useRef("date_component");
            onMounted(this._onPatched.bind(this));
            onWillPatch(async () => {
                if (this.datepicker) {
                    await this.datepicker.destroy();
                }
            });
            onPatched(this._onPatched.bind(this));
        }
        _onPatched() {
            if (this.dateRef.el) {
                this.datepicker = this._makeDatePicker();
                this.datepicker.on(
                    "datetime_changed",
                    this,
                    this._onDateChanged.bind(this)
                );
                this.datepicker.appendTo(this.dateRef.el);
            }
        }
        _makeDatePicker() {
            return new datepicker.DateWidget(this, {
                defaultDate: this.props.value.value_date,
            });
        }
        formattedValue(value) {
            switch (value.value_type) {
                case "int":
                    return field_utils.format.integer(value.value_int);
                case "float":
                    return field_utils.format.float(value.value_float);
                case "selection":
                    return value.value_selection || "";
                case "str":
                    return value.value_str || "";
                case "date":
                    return (
                        field_utils.format.date(
                            field_utils.parse.date(value.value_date)
                        ) || ""
                    );
            }
        }
        _onValueBoolInput(ev) {
            this.value = this.props.state.data.data.observation_data;
            this.value[this.props.value_id]["value_" + this.props.value.value_type] =
                ev.target.checked;
            this._onSetValue(this.value);
        }
        _onValueInput(ev) {
            this.value = this.props.state.data.data.observation_data;
            this.value[this.props.value_id]["value_" + this.props.value.value_type] =
                ev.target.value;
            this._onSetValue(this.value);
        }
        _onValueIntInput(ev) {
            this.value = this.props.state.data.data.observation_data;
            this.value[this.props.value_id][
                "value_" + this.props.value.value_type
            ] = parseInt(ev.target.value, 10);
            this._onSetValue(this.value);
        }
        _onValueFloatInput(ev) {
            this.value = this.props.state.data.data.observation_data;
            this.value[this.props.value_id][
                "value_" + this.props.value.value_type
            ] = parseFloat(ev.target.value);
            this._onSetValue(this.value);
        }
        _onDateChanged() {
            this.value[this.props.value_id][
                "value_" + this.props.value.value_type
            ] = field_utils.parse.date(this.datepicker.getValue());
            this._onSetValue(this.value);
        }
        _onSetValue(value, options) {
            return new Promise((resolve, reject) => {
                const changes = {};
                changes.observation_data = value;
                this.trigger("field-changed", {
                    dataPointID: this.props.state.data.id,
                    changes: changes,
                    viewType: this.viewType,
                    doNotSetDirty: options && options.doNotSetDirty,
                    notifyChange: !options || options.notifyChange !== false,
                    allowWarning: options && options.allowWarning,
                    onSuccess: resolve,
                    onFailure: reject,
                });
            });
        }
        getSelectionOptions() {
            return (this.props.value.selection_options || "").split(";");
        }
    }
    ObservationComponent.template =
        "cb_medical_clinical_impression.ObservationComponent";
    class ObservationsComponent extends Component {}
    ObservationsComponent.components = {ObservationComponent};
    ObservationsComponent.template =
        "cb_medical_clinical_impression.ObservationsComponent";

    ImpressionComponent.patch(
        "cb_medical_clinical_impression.ImpressionComponent",
        (T) => {
            class NewT extends T {
                generateDiagnosticReport() {
                    return this.trigger("create_impression_report", {
                        res_id: this.state.data.res_id,
                        db_id: this.state.data.id,
                    });
                }
            }
            NewT.components = {
                ...T.components,
                ObservationsComponent,
            };
            return NewT;
        }
    );
});
