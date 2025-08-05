document.addEventListener('DOMContentLoaded', function() {
    var canvas = document.getElementById('userStatisticsChart');
    
    if (canvas) {
        var filteredCount = canvas.getAttribute('data-filtered-count');
        var unfilteredCount = canvas.getAttribute('data-unfiltered-count');

        filteredCount = parseInt(filteredCount, 10);
        unfilteredCount = parseInt(unfilteredCount, 10);

        var ctx = canvas.getContext('2d');
        var userStatisticsChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['Filtered Count', 'Unfiltered Count'],
                datasets: [{
                    label: '# of Objects',
                    data: [filteredCount, unfilteredCount],
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.5)',
                        'rgba(75, 192, 192, 0.5)'
                    ],
                    borderColor: [
                        'rgba(0, 0, 0, 0.5)',
                        'rgba(0, 0, 0, 0.5)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: false,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                }
            }
        });
    }
});
