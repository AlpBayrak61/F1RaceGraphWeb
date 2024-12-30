$(document).ready(function(){
    // Handle form submission
    $('#selectionForm').submit(function(event){
        event.preventDefault();  // Prevent the default form submission

        // Serialize the form data
        var formData = $(this).serialize();

        // Send an AJAX request to the backend to get the lap times chart
        $.ajax({
            url: '/get_lap_times',  // The URL endpoint for the request
            type: 'POST',
            data: formData,  // The data we are sending (form inputs)
            success: function(response) {
                // On success, update the image src to show the lap chart
                var imgData = 'data:image/png;base64,' + response.img_data;
                $('#lap-chart').attr('src', imgData);  // Set the src attribute of the image
            },
            error: function() {
                // Handle errors if any occur during the request
                alert("Error occurred while fetching data.");
            }
        });
    });
});
