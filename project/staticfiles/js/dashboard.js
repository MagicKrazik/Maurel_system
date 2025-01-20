document.addEventListener('DOMContentLoaded', function() {
    // Calculate yearly balance data
    const yearlyBalanceData = yearlyIncomeData.map((income, index) => {
        return income - yearlyExpensesData[index];
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

    // Balance chart functionality
    const balanceCtx = document.getElementById('balanceChart');
    if (balanceCtx) {
        const balanceChart = new Chart(balanceCtx, {
            ...chartConfig,
            data: {
                labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
                datasets: [{
                    label: 'Balance mensual',
                    data: yearlyBalanceData,
                    backgroundColor: yearlyBalanceData.map(value => 
                        value >= 0 ? 'rgba(75, 192, 75, 0.6)' : 'rgba(255, 99, 132, 0.6)'
                    ),
                    borderColor: yearlyBalanceData.map(value => 
                        value >= 0 ? 'rgba(75, 192, 75, 1)' : 'rgba(255, 99, 132, 1)'
                    ),
                    borderWidth: 1
                }]
            },
            options: {
                ...chartConfig.options,
                scales: {
                    ...chartConfig.options.scales,
                    y: {
                        ...chartConfig.options.scales.y,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)',
                            zeroLineColor: 'rgba(255, 255, 255, 0.3)'
                        }
                    }
                }
            }
        });
    }

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

    // Responsive design adjustments
    function handleResize() {
        const width = window.innerWidth;
        const charts = [balanceChart, incomeChart, expensesChart].filter(chart => chart);
        
        if (width <= 768) {
            // Adjust chart options for smaller screens
            Chart.defaults.font.size = 10;
            charts.forEach(chart => {
                if (chart.options.scales.x) chart.options.scales.x.ticks.maxRotation = 90;
            });
        } else {
            // Reset chart options for larger screens
            Chart.defaults.font.size = 12;
            charts.forEach(chart => {
                if (chart.options.scales.x) chart.options.scales.x.ticks.maxRotation = 0;
            });
        }
        
        // Update all charts
        charts.forEach(chart => chart.update());
    }

    // Initial call and event listener for resize
    handleResize();
    window.addEventListener('resize', handleResize);
});