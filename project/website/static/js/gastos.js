$(document).ready(function() {
    $('#expense-form').on('submit', function(e) {
        e.preventDefault();
        var formData = new FormData(this);

        $.ajax({
            url: '{% url "gastos" %}',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                if (response.success) {
                    $('#upload-status').html('<div class="alert alert-success">' + response.message + '</div>');
                    $('#expense-form')[0].reset();
                } else {
                    $('#upload-status').html('<div class="alert alert-danger">Error: ' + response.errors + '</div>');
                }
            },
            error: function() {
                $('#upload-status').html('<div class="alert alert-danger">Error al subir el comprobante.</div>');
            }
        });
    });
});