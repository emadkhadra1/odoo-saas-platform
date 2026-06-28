odoo.define('website_portal.loan_portal', function (require) {
    "use strict";

    var rpc = require('web.rpc')
    var publicWidget = require('web.public.widget');
    var time = require('web.time');
    const session = require('web.session');

    publicWidget.registry.EmpPortalloan = publicWidget.Widget.extend({
        selector: '.new_loan_form',
        events: {
            'click .new_loan_confirm': '_onNewLoanConfirm',

        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        _buttonExec: function ($btn, callback) {
            // TODO remove once the automatic system which does this lands in master
            $btn.prop('disabled', true);
            return callback.call(this).guardedCatch(function () {
                $btn.prop('disabled', false);
            });
        },
        /**
         * @private
         * @returns {Promise}
         */
        _createLoan: function () {

            return this._rpc({
                model: 'hr.loan',
                method: 'create_loan_portal',
                args: [{
                    loan_type: $('.new_loan_form .loan_status_id').val(),
                    loan_date: this._parse_date($('.new_loan_form #loan_date').val()),
                    payment_date: this._parse_date($('.new_loan_form #payment_date').val()),
                    loan_amount: document.getElementById('loan_amount_input_id').value,
                    installments: document.getElementById('installments_input_id').value,
                }],
            }).then(function (response) {
                if (response.errors) {
                    toastr.error('Something went wrong ' + response.errors + ' , try again.')
                    return Promise.reject(response);
                } else {
                                        console.log('response',response.id);

                    window.location = '/my/loan/' + response.id;
                }
            });
        },

        _onNewLoanConfirm: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            if ($("#loan_form").valid()) {
                console.log($(ev.currentTarget))
                this._buttonExec($(ev.currentTarget), this._createLoan);
            } else {
                toastr.warning('Please fill the mandatory fields.')
            }

        },
        _parse_date: function (value) {
            console.log(value);
            var date = moment(value, "YYYY-MM-DD", true);
            if (date.isValid()) {
                return time.date_to_str(date.toDate());
            } else {
                return false;
            }
        },
    });

})
;
