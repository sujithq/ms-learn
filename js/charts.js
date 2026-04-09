// Chart registry: maps canvasId -> Chart instance
const _charts = {};

function destroyChart(canvasId) {
    if (_charts[canvasId]) {
        _charts[canvasId].destroy();
        delete _charts[canvasId];
    }
}

window.createBarChart = function (canvasId, labels, data, label, color) {
    destroyChart(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    _charts[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: data,
                backgroundColor: color || 'rgba(13, 110, 253, 0.8)',
                borderColor: color || 'rgba(13, 110, 253, 1)',
                borderWidth: 1,
                borderRadius: 4,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false },
                tooltip: { mode: 'index', intersect: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { stepSize: 1 },
                    grid: { color: 'rgba(0,0,0,0.05)' }
                },
                x: {
                    grid: { display: false }
                }
            }
        }
    });
};

window.createDoughnutChart = function (canvasId, labels, data) {
    destroyChart(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    const colors = [
        '#0d6efd', '#198754', '#ffc107', '#dc3545',
        '#0dcaf0', '#6f42c1', '#fd7e14', '#20c997'
    ];
    _charts[canvasId] = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors.slice(0, data.length),
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { boxWidth: 12, padding: 10, font: { size: 11 } }
                }
            }
        }
    });
};

window.createSparklineChart = function (canvasId, labels, data, color) {
    destroyChart(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    _charts[canvasId] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                borderColor: color || 'rgba(13, 110, 253, 1)',
                backgroundColor: 'rgba(13, 110, 253, 0.12)',
                borderWidth: 2,
                fill: true,
                tension: 0.35,
                pointRadius: 2,
                pointHoverRadius: 3,
                pointBackgroundColor: color || 'rgba(13, 110, 253, 1)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: { enabled: true }
            },
            scales: {
                x: { display: false },
                y: { display: false, beginAtZero: true }
            },
            elements: {
                line: { capBezierPoints: true }
            }
        }
    });
};

window.destroyChart = destroyChart;
