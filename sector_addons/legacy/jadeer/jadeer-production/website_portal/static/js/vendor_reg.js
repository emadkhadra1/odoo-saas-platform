$(document).ready(function() {

    $("#addProduct").click(function() {
//        var clone = $('#qualifications > tbody tr:last').clone();
//        clone.find('input').val('');
//        clone.insertAfter('#qualifications > tbody tr:last');

        $('#qualifications_head').show();
         var markup = "<tr><td><input  type='text' name='pro_name' class='form-control'  required='required'/></td><td> <input  type='text' name='description' class='form-control'  required='required'/></td><td> <button class='btn btn-danger remove'><i class='fa fa-trash' aria-hidden='true'></i> Remove  </button> </td></tr>";
        $("table tbody").append(markup);
    });

    $(document).on('click', '.remove', function() {
        event.preventDefault()
        var lenRow = $('#qualifications tbody tr').length;
       if (lenRow == 1 || lenRow <= 1) {
            $('#qualifications_head').hide();
            $(this).parents('tr').remove();
       } else {

            $(this).parents('tr').remove();
       }
    });


       $(document).on('change', '.pr_product_id', function() {
        event.preventDefault()
            var pr_product_id = $("option:selected", this).text()
            $(this).closest('td').next('td').find('input').val(pr_product_id.trim())
        });

     $(document).on('click','.remove_pr',function(){
      event.preventDefault()
         var lenRow = $('.item').length;

         if (lenRow == 1 || lenRow <= 1) {
        alert("Can't remove all row!");
    } else {

        $(this).parents('tr').remove();
    }
    });

$('table').on('mouseup keyup', 'input[type=number]', () => calculateTotals());

$('.btn-add-row').on('click', () => {
    event.preventDefault()
  const $lastRow = $('.item:last');
  const $newRow = $lastRow.clone();

  $newRow.find('input').val('');
  $newRow.find('td:last').text('0.00');
  $newRow.insertAfter($lastRow);

  $newRow.find('input:first').focus();
});

function calculateTotals() {
  const subtotals = $('.item').map((idx, val) => calculateSubtotal(val)).get();
  const total = subtotals.reduce((a, v) => a + Number(v), 0);
  $('.total td:eq(1)').text(formatAsCurrency(total));
}

function calculateSubtotal(row) {
  const $row = $(row);
  const inputs = $row.find('input');
  const subtotal = inputs[1].value * inputs[2].value;

  $row.find('td:last').text(formatAsCurrency(subtotal));

  return subtotal;
}

function formatAsCurrency(amount) {
  return Number(amount).toFixed(2);
}



       $(document).on('change', '#salary_request_type', function() {
        event.preventDefault()
        if($('#salary_related_to_bank').val()=='True' && $("option:selected", this).val() == 'adddefine'){

            $('#salary_related_to_bank_msg').show()
            $('#salary_related_to_bank_required').attr('required',true)
        }else{
            $('#salary_related_to_bank_msg').hide()
            $('#salary_related_to_bank_required').removeAttr("required");
        }

        });

});
