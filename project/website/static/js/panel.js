// panel.js
document.addEventListener('DOMContentLoaded', function() {
    const apartmentCards = document.querySelectorAll('.apartment-card');
    
    apartmentCards.forEach(card => {
        const feeInputs = card.querySelectorAll('.fee-input');
        const totalValueSpan = card.querySelector('.total-value');
        const paidAmountInput = card.querySelector('.paid-amount-input');
        const pendingValueSpan = card.querySelector('.pending-value');
        
        function updateValues() {
            let total = 0;
            feeInputs.forEach(input => {
                if (input.name !== 'paid_amount') {
                    total += parseFloat(input.value) || 0;
                }
            });
            
            const paidAmount = parseFloat(paidAmountInput.value) || 0;
            const pendingAmount = Math.max(total - paidAmount, 0);
            
            totalValueSpan.textContent = total.toFixed(2);
            pendingValueSpan.textContent = pendingAmount.toFixed(2);
            
            // Update colors based on values
            pendingValueSpan.classList.toggle('negative', pendingAmount > 0);
            pendingValueSpan.classList.toggle('positive', pendingAmount === 0);
        }
        
        feeInputs.forEach(input => {
            input.addEventListener('input', updateValues);
        });
        
        // Initial calculation
        updateValues();
    });
});