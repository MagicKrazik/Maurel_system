document.addEventListener('DOMContentLoaded', function() {
    // Existing functionality for fee items
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

    // Income chart functionality
    const incomeCtx = document.getElementById('incomeChart').getContext('2d');
    let incomeChart = new Chart(incomeCtx, {
        type: 'bar',
        data: {
            labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
            datasets: [{
                label: 'Ingresos mensuales',
                data: yearlyIncomeData,
                backgroundColor: 'rgba(75, 192, 192, 0.6)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
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
                title: {
                    display: true,
                    text: `Ingresos para ${selectedDate}`
                }
            }
        }
    });

    // Expenses chart functionality
    const expensesCtx = document.getElementById('expensesChart').getContext('2d');
    let expensesChart = new Chart(expensesCtx, {
        type: 'bar',
        data: {
            labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
            datasets: [{
                label: 'Gastos mensuales',
                data: yearlyExpensesData,
                backgroundColor: 'rgba(255, 99, 132, 0.6)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
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
                title: {
                    display: true,
                    text: `Gastos para ${selectedDate}`
                }
            }
        }
    });

    // Add event listeners for the filter forms
    const incomeFilterForm = document.getElementById('income-filter-form');
    const expensesFilterForm = document.getElementById('expenses-filter-form');

    if (incomeFilterForm) {
        incomeFilterForm.addEventListener('submit', function(event) {
            // The form will now submit normally, no need to prevent default
            // or manually update the URL
        });
    }

    if (expensesFilterForm) {
        expensesFilterForm.addEventListener('submit', function(event) {
            // The form will now submit normally, no need to prevent default
            // or manually update the URL
        });
    }
});