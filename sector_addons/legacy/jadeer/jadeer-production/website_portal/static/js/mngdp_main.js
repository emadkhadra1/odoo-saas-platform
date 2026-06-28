odoo.define('custom_adi.pr_form', function (require) {
    "use strict";

    var sAnimations = require('website.content.snippets.animation');
    var core = require('web.core');
    var _t = core._t;
    // sAnimations.registry.pr_form = sAnimations.Class.extend({
    //     selector: '.pd_form',
    //     read_events: {
    //         'change .oe_search_budget': '_onChangeBudget',
    //     },
    //     init: function () {
    //         this._super.apply(this, arguments);
    //         this.isWebsite = true;
    //     },
    //     /**
    //      * @override
    //      */
    //     start: function () {
    //         var def = this._super.apply(this, arguments);
    //         return def;
    //
    //     },
    //     _onChangeBudget: function (ev) {
    //         $(".oe_search_analytic_account").empty();
    //         $(".oe_search_account_account").empty();
    //
    //         var buget = ev.target.value;
    //         this._rpc({
    //             route: "/budget/account/search",
    //             params: {
    //                 budget_id: parseInt(buget),
    //             },
    //         }).then(function (data) {
    //             var dropdown_analytic = $(".oe_search_analytic_account");
    //             var dropdown_account = $(".oe_search_account_account");
    //             dropdown_analytic.empty();
    //             dropdown_account.empty();
    //             dropdown_analytic.append($('<option value="">Select Analtyic Account</option>'))
    //             dropdown_account.append($('<option value="">Select Account Account</option>'))
    //             $.each(data['analytic'], function (index, item) {
    //                 dropdown_analytic.append(
    //                     $('<option>', {
    //                         value: item['id'],
    //                         text: item['name']
    //                     }, '</option>'))
    //             });
    //             $.each(data['accounts'], function (index, item) {
    //                 dropdown_account.append(
    //                     $('<option>', {
    //                         value: item['id'],
    //                         text: item['name']
    //                     }, '</option>'))
    //             });
    //
    //         });
    //     },
    // });
    sAnimations.registry.pr_receiving_form = sAnimations.Class.extend(
        {
            template: 'website_portal.receive_pr_products',
            selector: '.receiving_collapse',
            read_events: {
                'change .po_select': '_onChangePurchaseOrder',
                'change .point_select': '_onChangePoint',
                'change #receive_qty': '_onChangeReceiveQty',
            },

            init: function () {
                this._super.apply(this, arguments);
                this.isWebsite = true;
            },
            /**
             * @override
             */
            start: function () {
                var def = this._super.apply(this, arguments);
                return def;
            },
            _onChangePurchaseOrder: function (ev) {
                $("#point_select").empty()
                $("#remin_qty").empty()
                var po = ev.target.value;
                this._rpc({
                    route: "/my/purchase_request/receive/search/point",
                    params: {
                        po_id: parseInt(po),
                        sfrom: 'po'
                    },
                }).then(function (data) {
                    var dropdown_points = $("#point_select");
                    dropdown_points.empty();
                    dropdown_points.append($('<option value="">Select Purchase Order Point</option>'))
                    $.each(data['order_points'], function (index, item) {
                        dropdown_points.append(
                            $('<option>', {
                                value: item['id'],
                                text: `[ ${item['order_id'][1]} ] ${item['order_line_id'][1]}`
                            }, '</option>'))
                    });

                });

            },

            _onChangePoint: function (ev) {
                $('#receive_qty').empty()
                $('#remin_qty').empty()

                var point_id = ev.target.value;
                this._rpc({
                    route: "/my/purchase_request/receive/search/point",
                    params: {
                        point_id: parseInt(point_id),
                        sfrom: 'point'
                    },
                }).then(function (data) {
                    $('#remin_qty').empty()
                    $('#remin_qty').html(data['remin_qty'])
                });
            },

            _onChangeReceiveQty: function (ev) {
                console.log(ev.target.value)
            }
        });

});
