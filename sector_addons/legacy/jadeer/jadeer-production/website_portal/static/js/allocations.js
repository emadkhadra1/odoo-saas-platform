odoo.define('website_portal.allocation_portal', function (require) {
    "use strict";

    var rpc = require('web.rpc')
    var publicWidget = require('web.public.widget');
    var time = require('web.time');
    const session = require('web.session');

    publicWidget.registry.EmpPortalallocation = publicWidget.Widget.extend({
        selector: '.new_allocation_form',
        events: {
            'click .new_allocation_confirm': '_onNewallocationConfirm',

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
        _createallocation: function () {

            return this._rpc({
                model: 'hr.leave.allocation',
                method: 'create_allocation_portal',
                args: [{
                    holiday_status_id: $('.new_allocation_form .allocation_status_id').val(),
                    allocation_date: this._parse_date($('.new_allocation_form #allocation_date').val()),
                    allocation_date_to: this._parse_date($('.new_allocation_form #allocation_date_to').val()),
                    duration: document.getElementById('duration').value,
                    description: document.getElementById('description').value,
                }],
            }).then(function (response) {
                if (response.errors) {
                    toastr.error('Something went wrong ' + response.errors + ' , try again.')
                    return Promise.reject(response);
                } else {
                                        console.log('response',response.id);

                    window.location = '/my/allocation/' + response.id;
                }
            });
        },

        _onNewallocationConfirm: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            if ($("#allocation_form").valid()) {
                console.log($(ev.currentTarget))
                this._buttonExec($(ev.currentTarget), this._createallocation);
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
