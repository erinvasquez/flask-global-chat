document.addEventListener('DOMContentLoaded', function() {
    // Retrieve the ids and selectedId from the hidden script element
    var dataElement = document.getElementById('data');
    var data = JSON.parse(dataElement.textContent);

    var ids = data.ids;
    var selectedId = data.selected_id;

    // Populate the dropdown
    var select = document.getElementById('id');
    ids.forEach(function(id) {
        var option = document.createElement('option');
        option.value = id;
        option.textContent = id;
        if (id == selectedId) {
            option.selected = true;
        }
        select.appendChild(option);
    });

    // Update the XZ plot image source
    var xzPlotImg = document.getElementById('xzPlot');
    if (selectedId) {
        xzPlotImg.src = '/static/plots/plot_' + selectedId + '.png';
    } else {
        xzPlotImg.src = '/static/plots/plot_1.png'; // Default image
    }
});

document.getElementById('selectionForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission

    var id = document.getElementById('id').value;
    var xzPlotImg = document.getElementById('xzPlot');

    // Update the XZ plot image source
    xzPlotImg.src = '/static/plots/plot_' + id + '.png';
});
