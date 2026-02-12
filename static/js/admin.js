// Admin Dashboard JavaScript

let occupancyChart, statusChart;

document.addEventListener('DOMContentLoaded', function() {
    initCharts();
    loadAnalyticsData();
    
    // Auto-refresh every 10 seconds
    setInterval(() => {
        loadAnalyticsData();
        updateStats();
    }, 10000);
});

// Initialize charts
function initCharts() {
    // Occupancy Trends Chart
    const occupancyCtx = document.getElementById('occupancyChart').getContext('2d');
    occupancyChart = new Chart(occupancyCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Occupied',
                    data: [],
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'Available',
                    data: [],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'Reserved',
                    data: [],
                    borderColor: '#f59e0b',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 70
                }
            }
        }
    });
    
    // Status Pie Chart
    const statusCtx = document.getElementById('statusChart').getContext('2d');
    statusChart = new Chart(statusCtx, {
        type: 'doughnut',
        data: {
            labels: ['Available', 'Occupied', 'Reserved'],
            datasets: [{
                data: [0, 0, 0],
                backgroundColor: ['#10b981', '#ef4444', '#f59e0b']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Load analytics data
function loadAnalyticsData() {
    fetch('/admin/api/analytics')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.trends.length > 0) {
                updateOccupancyChart(data.trends);
            }
        })
        .catch(error => {
            console.error('Error loading analytics:', error);
        });
}

// Update occupancy chart
function updateOccupancyChart(trends) {
    const labels = trends.map(t => {
        const date = new Date(t.timestamp);
        return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    });
    
    const occupied = trends.map(t => t.occupied_spots);
    const available = trends.map(t => t.available_spots);
    const reserved = trends.map(t => t.reserved_spots);
    
    occupancyChart.data.labels = labels;
    occupancyChart.data.datasets[0].data = occupied;
    occupancyChart.data.datasets[1].data = available;
    occupancyChart.data.datasets[2].data = reserved;
    occupancyChart.update();
    
    // Update status chart with latest data
    if (trends.length > 0) {
        const latest = trends[trends.length - 1];
        statusChart.data.datasets[0].data = [
            latest.available_spots,
            latest.occupied_spots,
            latest.reserved_spots
        ];
        statusChart.update();
    }
}

// Update stats in real-time
function updateStats() {
    fetch('/api/spots')
        .then(response => response.json())
        .then(data => {
            document.getElementById('admin-available').textContent = data.stats.available;
            document.getElementById('admin-occupied').textContent = data.stats.occupied;
            document.getElementById('admin-reserved').textContent = data.stats.reserved;
        })
        .catch(error => {
            console.error('Error updating stats:', error);
        });
}

// Export data functions (optional)
function exportBookingsCSV() {
    // Placeholder for CSV export functionality
    alert('Export functionality coming soon!');
}

function exportLogsCSV() {
    // Placeholder for CSV export functionality
    alert('Export functionality coming soon!');
}
