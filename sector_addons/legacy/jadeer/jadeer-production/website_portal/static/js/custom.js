//This is the Range Date Picker
$(document).ready(function () {

    var html = '<tr><td><select class="form-control" id="product-name"><option value="325">Floor Cleaner</option><option value="324">Pupa One Piece Paragon White -2</option></select></td><td>10</td><td></td><td></td><td><button class="btn btn-danger remove"><i class="fa fa-times" aria-hidden="true"></i></button></td></tr>';
    $("#addProduct").click(function () {
        var clone = $('#invoice > tbody tr:last').clone();
        clone.find('input').val('');
        clone.insertAfter('#invoice > tbody tr:last');
    });

    $(document).on('click', '.remove', function () {
        var lenRow = $('#invoice tbody tr').length;
        if (lenRow == 1 || lenRow <= 1) {
            alert("Can't remove all row!");
        } else {

            $(this).parents('tr').remove();
        }
    });

    $("#pd_product_id").on('change', function () {
        if ($(this).find(':selected').attr('pd') == 'True') {
            $("#pd_div").show()
            $("#pd_div select").attr('required', 'required')
            $("#pd_div select").addClass('is-invalid')
        } else {
            $("#pd_div").hide()
            $("#pd_div select").removeAttr('required')
            $("#pd_div select").removeClass('is-invalid')
            $("#pd_div select").val('')
        }

    });
});
$('#checkInDate').datepicker({

    dateFormat: 'dd/mm/yy',
    prevText: '<i class="fa fa-chevron-left"></i>',
    nextText: '<i class="fa fa-chevron-right"></i>',
    // onSelect: function(datePicked) {
    //
    //     $('#checkOutDate').datepicker('option', 'minDate', datePicked);
    // }
});

$('#checkOutDate').datepicker({
    dateFormat: 'dd/mm/yy',
    prevText: '<i class="fa fa-chevron-left"></i>',
    nextText: '<i class="fa fa-chevron-right"></i>',
});

leave_date_from_bt = flatpickr("#leave_date_from_bt", {
    enableTime: false,
    dateFormat: "Y-m-d",
    onChange: function (selectedDates, dateStr, instance) {
        leave_date_to_bt.set('minDate', selectedDates[0]);
    }
});
allocation_date_from_bt = flatpickr("#allocation_date", {
    enableTime: false,
    dateFormat: "Y-m-d",
    onChange: function (selectedDates, dateStr, instance) {
        allocation_date_to_bt.set('minDate', selectedDates[0]);
    }
});
allocation_date_to_bt = flatpickr("#allocation_date_to", {});

loan_date = flatpickr("#loan_date", {
    enableTime: false,
    dateFormat: "Y-m-d",
    onChange: function (selectedDates, dateStr, instance) {
        payment_date.set('minDate', selectedDates[0]);
    }
});
payment_date = flatpickr("#payment_date", {
    enableTime: false,
    dateFormat: "Y-m-d",

});
leave_date_to_bt = flatpickr("#leave_date_to_bt", {});

date_from_btrip = flatpickr("#date_from_btrip", {
    enableTime: false,
    dateFormat: "Y-m-d",
    onChange: function (selectedDates, dateStr, instance) {
        date_to_btrip.set('minDate', selectedDates[0]);
    }
});
date_to_btrip = flatpickr("#date_to_btrip", {});

date_from_bt = flatpickr("#date_from_bt", {
    minDate: 'today',
    enableTime: false,
    dateFormat: "Y-m-d",
    onChange: function (selectedDates, dateStr, instance) {
        date_to_bt.set('minDate', selectedDates[0]);
    }
});
date_to_bt = flatpickr("#date_to_bt", {});


$(function () {

    $('#pd_form,#reimbursement_form').validate({
        errorElement: 'span',
        errorPlacement: function (error, element) {
            error.addClass('invalid-feedback');
            element.closest('.form-group').append(error);
        },
        highlight: function (element, errorClass, validClass) {
            $(element).addClass('is-invalid');
        },
        unhighlight: function (element, errorClass, validClass) {
            $(element).removeClass('is-invalid');
        }
    });
    $.validator.addMethod('validDate', function (value, element) {
        return this.optional(element) || /^(0?[1-9]|1[012])[ /](0?[1-9]|[12][0-9]|3[01])[ /][0-9]{4}$/.test(value);
    }, 'Please provide a date in the mm/dd/yyyy format');
    $.validator.addMethod('dateBefore', function (value, element, params) {
        // if end date is valid, validate it as well
        var end = $(params);
        if (!end.data('validation.running')) {
            $(element).data('validation.running', true);
            setTimeout($.proxy(
                function () {
                    this.element(end);
                }, this), 0);
            // Ensure clearing the 'flag' happens after the validation of 'end' to prevent endless looping
            setTimeout(function () {
                $(element).data('validation.running', false);
            }, 0);
        }
        return this.optional(element) || this.optional(end[0]) || new Date(value) < new Date(end.val());

    }, 'Must be before corresponding end date');

    $.validator.addMethod('dateAfter', function (value, element, params) {
        // if start date is valid, validate it as well
        var start = $(params);
        if (!start.data('validation.running')) {
            $(element).data('validation.running', true);
            setTimeout($.proxy(
                function () {
                    this.element(start);
                }, this), 0);
            setTimeout(function () {
                $(element).data('validation.running', false);
            }, 0);
        }
        return this.optional(element) || this.optional(start[0]) || new Date(value) > new Date($(params).val());

    }, 'Must be after corresponding start date');
    $('#leave_form').validate({
        rules: {
            request_date_from: {
                dateBefore: '#request_date_to',
                required: true
            },
            request_date_to: {
                dateAfter: '#request_date_from',
                required: true
            },
            request_date_from: {greaterThan: "#StartDate"}
        },
        errorElement: 'span',
        errorPlacement: function (error, element) {
            error.addClass('invalid-feedback');
            element.closest('.form-group').append(error);
        },
        highlight: function (element, errorClass, validClass) {
            $(element).addClass('is-invalid');
        },
        unhighlight: function (element, errorClass, validClass) {
            $(element).removeClass('is-invalid');
        }
    });

    $('[data-toggle="tooltip"]').tooltip({
        delay: {
            show: 50,
            hide: 300
        }
    });
})