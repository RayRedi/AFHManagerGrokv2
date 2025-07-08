$(document).ready(function() {
    // Initialize jQuery UI Autocomplete
    $('#medication_name').autocomplete({
        source: function(request, response) {
            $.ajax({
                url: '/api/medication-suggestions',
                dataType: 'json',
                data: {
                    term: request.term
                },
                success: function(data) {
                    response(data);
                }
            });
        },
        minLength: 2, // Start suggesting after 2 characters
        select: function(event, ui) {
            // Pre-fill form fields when a suggestion is selected
            $('#medication_dosage').val(ui.item.dosage);
            $('#medication_frequency').val(ui.item.frequency);
            $('#medication_notes').val(ui.item.notes);
        }
    });

    // Ensure form is visible when editing
    $('#medication_form_container').show();
});