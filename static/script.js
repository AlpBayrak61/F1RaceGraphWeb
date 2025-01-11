$(document).ready(function() {
    $('#selectionForm').submit(function(event) {
        event.preventDefault();

        var formData = $(this).serialize();

        $.ajax({
            url: '/get_lap_times',
            type: 'POST',
            data: formData,
            success: function(response) {
                var graphData = JSON.parse(response.graph_json);
                Plotly.newPlot('lap-chart', graphData.data, graphData.layout);
            },
            error: function() {
                alert("Error occurred while fetching data.");
            }
        });
    });
});
