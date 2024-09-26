document.addEventListener('DOMContentLoaded', function() {
    // Fee items functionality
    const feeItems = document.querySelectorAll('.fee-item');
    
    feeItems.forEach(item => {
        const valueSpan = item.querySelector('span:last-child');
        const value = parseFloat(valueSpan.textContent.replace('$', ''));
        
        if (!isNaN(value)) {
            if (item.classList.contains('account-status')) {
                valueSpan.classList.add(value > 0 ? 'negative' : 'positive');
            } else {
                valueSpan.classList.add(value > 0 ? 'positive' : 'negative');
            }
        }
    });

    // Chart configuration
    const chartConfig = {
        type: 'bar',
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Monto ($)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    };

    // Income chart functionality
    const incomeCtx = document.getElementById('incomeChart');
    if (incomeCtx) {
        const incomeChart = new Chart(incomeCtx, {
            ...chartConfig,
            data: {
                labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
                datasets: [{
                    label: 'Ingresos mensuales',
                    data: yearlyIncomeData,
                    backgroundColor: 'rgba(75, 192, 192, 0.6)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }]
            }
        });
    }

    // Expenses chart functionality
    const expensesCtx = document.getElementById('expensesChart');
    if (expensesCtx) {
        const expensesChart = new Chart(expensesCtx, {
            ...chartConfig,
            data: {
                labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
                datasets: [{
                    label: 'Gastos mensuales',
                    data: yearlyExpensesData,
                    backgroundColor: 'rgba(255, 99, 132, 0.6)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                }]
            }
        });
    }

    // Filter functionality
    const dateFilter = document.getElementById('date-filter');
    const filterButton = document.getElementById('filter-button');

    if (dateFilter && filterButton) {
        filterButton.addEventListener('click', function() {
            const selectedDate = dateFilter.value;
            if (selectedDate) {
                window.location.href = `?date=${selectedDate}`;
            }
        });

        // Enable keyboard navigation for the date filter
        dateFilter.addEventListener('keydown', function(event) {
            if (event.key === 'Enter') {
                filterButton.click();
            }
        });
    }

    // Responsive design adjustments
    function handleResize() {
        const width = window.innerWidth;
        if (width <= 768) {
            // Adjust chart options for smaller screens
            Chart.defaults.font.size = 10;
            if (incomeChart) incomeChart.options.scales.x.ticks.maxRotation = 90;
            if (expensesChart) expensesChart.options.scales.x.ticks.maxRotation = 90;
        } else {
            // Reset chart options for larger screens
            Chart.defaults.font.size = 12;
            if (incomeChart) incomeChart.options.scales.x.ticks.maxRotation = 0;
            if (expensesChart) expensesChart.options.scales.x.ticks.maxRotation = 0;
        }
        if (incomeChart) incomeChart.update();
        if (expensesChart) expensesChart.update();
    }

    // Initial call and event listener for resize
    handleResize();
    window.addEventListener('resize', handleResize);
});