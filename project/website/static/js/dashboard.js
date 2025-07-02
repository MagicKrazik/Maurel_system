document.addEventListener('DOMContentLoaded', function() {
    // Auto-submit form when year or month changes
    const yearSelect = document.getElementById('year-select');
    const monthSelect = document.getElementById('month-select');
    
    if (yearSelect) {
        yearSelect.addEventListener('change', function() {
            this.form.submit();
        });
    }
    
    if (monthSelect) {
        monthSelect.addEventListener('change', function() {
            this.form.submit();
        });
    }

    // Enhanced chart configuration
    const baseChartConfig = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false
            },
            tooltip: {
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                titleColor: '#ffffff',
                bodyColor: '#ffffff',
                borderColor: '#4a90e2',
                borderWidth: 1,
                cornerRadius: 6,
                displayColors: false
            }
        },
        scales: {
            x: {
                grid: {
                    color: 'rgba(255, 255, 255, 0.1)',
                    borderColor: 'rgba(255, 255, 255, 0.2)'
                },
                ticks: {
                    color: '#ffffff',
                    font: {
                        size: 11
                    }
                }
            },
            y: {
                beginAtZero: true,
                grid: {
                    color: 'rgba(255, 255, 255, 0.1)',
                    borderColor: 'rgba(255, 255, 255, 0.2)'
                },
                ticks: {
                    color: '#ffffff',
                    font: {
                        size: 11
                    },
                    callback: function(value) {
                        return '$' + value.toLocaleString('es-MX');
                    }
                }
            }
        },
        animation: {
            duration: 800,
            easing: 'easeInOutQuart'
        }
    };

    // Income Chart - Updated for both monthly and yearly view
    const incomeCtx = document.getElementById('incomeChart');
    if (incomeCtx && yearlyIncomeData) {
        let displayData = [...yearlyIncomeData];
        let displayLabels = [...yearlyLabels];
        
        // For specific month selection, show only that month's data
        if (selectedMonth !== 'all') {
            // Show only the selected month's data
            const monthIndex = displayLabels.length - 1; // Last element for specific month view
            displayData = [displayData[monthIndex]];
            displayLabels = [displayLabels[monthIndex]];
        }

        new Chart(incomeCtx, {
            type: 'bar',
            data: {
                labels: displayLabels,
                datasets: [{
                    label: 'Ingresos',
                    data: displayData,
                    backgroundColor: displayData.map(value => 
                        value > 0 ? 'rgba(76, 175, 80, 0.7)' : 'rgba(76, 175, 80, 0.3)'
                    ),
                    borderColor: 'rgba(76, 175, 80, 1)',
                    borderWidth: 2,
                    borderRadius: 4,
                    borderSkipped: false,
                }]
            },
            options: {
                ...baseChartConfig,
                plugins: {
                    ...baseChartConfig.plugins,
                    tooltip: {
                        ...baseChartConfig.plugins.tooltip,
                        callbacks: {
                            label: function(context) {
                                return `Ingresos: $${context.parsed.y.toLocaleString('es-MX', {
                                    minimumFractionDigits: 2,
                                    maximumFractionDigits: 2
                                })}`;
                            }
                        }
                    }
                },
                scales: {
                    ...baseChartConfig.scales,
                    y: {
                        ...baseChartConfig.scales.y,
                        title: {
                            display: true,
                            text: 'Ingresos ($)',
                            color: '#4CAF50',
                            font: {
                                weight: 'bold'
                            }
                        }
                    }
                }
            }
        });
    }

    // Expenses Chart - Updated for both monthly and yearly view
    const expensesCtx = document.getElementById('expensesChart');
    if (expensesCtx && yearlyExpensesData) {
        let displayData = [...yearlyExpensesData];
        let displayLabels = [...yearlyLabels];
        
        // For specific month selection, show only that month's data
        if (selectedMonth !== 'all') {
            const monthIndex = displayLabels.length - 1;
            displayData = [displayData[monthIndex]];
            displayLabels = [displayLabels[monthIndex]];
        }

        new Chart(expensesCtx, {
            type: 'bar',
            data: {
                labels: displayLabels,
                datasets: [{
                    label: 'Gastos',
                    data: displayData,
                    backgroundColor: displayData.map(value => 
                        value > 0 ? 'rgba(244, 67, 54, 0.7)' : 'rgba(244, 67, 54, 0.3)'
                    ),
                    borderColor: 'rgba(244, 67, 54, 1)',
                    borderWidth: 2,
                    borderRadius: 4,
                    borderSkipped: false,
                }]
            },
            options: {
                ...baseChartConfig,
                plugins: {
                    ...baseChartConfig.plugins,
                    tooltip: {
                        ...baseChartConfig.plugins.tooltip,
                        callbacks: {
                            label: function(context) {
                                return `Gastos: $${context.parsed.y.toLocaleString('es-MX', {
                                    minimumFractionDigits: 2,
                                    maximumFractionDigits: 2
                                })}`;
                            }
                        }
                    }
                },
                scales: {
                    ...baseChartConfig.scales,
                    y: {
                        ...baseChartConfig.scales.y,
                        title: {
                            display: true,
                            text: 'Gastos ($)',
                            color: '#f44336',
                            font: {
                                weight: 'bold'
                            }
                        }
                    }
                }
            }
        });
    }

    // Balance Chart (Line Chart) - Keep the same logic but update for month/year
    const balanceCtx = document.getElementById('balanceChart');
    if (balanceCtx && yearlyBalanceData) {
        let displayData = [...yearlyBalanceData];
        let displayLabels = [...yearlyLabels];

        new Chart(balanceCtx, {
            type: 'line',
            data: {
                labels: displayLabels,
                datasets: [{
                    label: 'Balance Acumulado',
                    data: displayData,
                    backgroundColor: function(context) {
                        const chart = context.chart;
                        const {ctx, chartArea} = chart;
                        if (!chartArea) return;
                        
                        const gradient = ctx.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);
                        gradient.addColorStop(0, 'rgba(74, 144, 226, 0.1)');
                        gradient.addColorStop(1, 'rgba(74, 144, 226, 0.3)');
                        return gradient;
                    },
                    borderColor: function(context) {
                        const value = context.parsed?.y;
                        return value >= 0 ? 'rgba(76, 175, 80, 1)' : 'rgba(244, 67, 54, 1)';
                    },
                    pointBackgroundColor: function(context) {
                        const value = context.parsed?.y;
                        return value >= 0 ? 'rgba(76, 175, 80, 1)' : 'rgba(244, 67, 54, 1)';
                    },
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                ...baseChartConfig,
                plugins: {
                    ...baseChartConfig.plugins,
                    tooltip: {
                        ...baseChartConfig.plugins.tooltip,
                        callbacks: {
                            label: function(context) {
                                const value = context.parsed.y;
                                const status = value >= 0 ? 'Positivo' : 'Negativo';
                                return `Balance ${status}: $${Math.abs(value).toLocaleString('es-MX', {
                                    minimumFractionDigits: 2,
                                    maximumFractionDigits: 2
                                })}`;
                            }
                        }
                    }
                },
                scales: {
                    ...baseChartConfig.scales,
                    y: {
                        ...baseChartConfig.scales.y,
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: 'Balance Acumulado ($)',
                            color: '#4a90e2',
                            font: {
                                weight: 'bold'
                            }
                        },
                        grid: {
                            ...baseChartConfig.scales.y.grid,
                            drawBorder: true,
                            borderDash: [5, 5],
                        }
                    }
                },
                elements: {
                    point: {
                        hoverBackgroundColor: '#ffffff',
                        hoverBorderWidth: 3
                    }
                }
            }
        });
    }

    // Add loading states and error handling
    function showChartLoading(canvasId) {
        const canvas = document.getElementById(canvasId);
        if (canvas) {
            const wrapper = canvas.parentElement;
            wrapper.innerHTML = '<div class="chart-loading">Cargando datos del gráfico...</div>';
        }
    }

    // Responsive chart updates
    function handleChartResize() {
        const charts = Chart.instances;
        Object.values(charts).forEach(chart => {
            if (chart) {
                chart.resize();
            }
        });
    }

    // Update charts on window resize
    let resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(handleChartResize, 250);
    });

    // Add smooth scrolling to charts when they come into view
    const chartSections = document.querySelectorAll('.chart-section');
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const chartObserver = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    chartSections.forEach(section => {
        chartObserver.observe(section);
    });

    // Add data export functionality (optional)
    function exportChartData() {
        const data = {
            year: selectedYear,
            month: selectedMonth,
            income: yearlyIncomeData,
            expenses: yearlyExpensesData,
            balance: yearlyBalanceData,
            labels: yearlyLabels
        };
        
        const dataStr = JSON.stringify(data, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        const url = URL.createObjectURL(dataBlob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `dashboard_data_${selectedYear}_${selectedMonth}.json`;
        link.click();
        
        URL.revokeObjectURL(url);
    }

    // Make export function available globally (optional)
    window.exportChartData = exportChartData;

    console.log(`Dashboard loaded for ${selectedMonth === 'all' ? 'year' : 'month'} ${selectedMonth} of ${selectedYear}`);
});