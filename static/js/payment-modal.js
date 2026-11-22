// ==========================================================================
// Mock Payment Gateway Simulation (Razorpay / PayPal)
// ==========================================================================

function openPaymentModal() {
  // Validate delivery form first
  const form = document.getElementById('checkout-form');
  if (!form || !form.checkValidity()) {
    if (form) form.reportValidity();
    return;
  }

  const selectedMethod = document.querySelector('input[name="payment_method"]:checked')?.value;
  if (selectedMethod === 'Cash on Delivery') {
    // If COD, submit directly
    if (confirm('Confirm order with Cash on Delivery (COD)?')) {
      form.submit();
    }
    return;
  }

  // If Mock Online Gateway (Razorpay/PayPal)
  const totalAmount = document.getElementById('checkout-total-display')?.textContent || '₹0.00';
  document.getElementById('modal-pay-amount').textContent = totalAmount;

  const paymentModal = new bootstrap.Modal(document.getElementById('mockPaymentModal'));
  paymentModal.show();
}

function processMockTransaction(outcome) {
  const modalBody = document.getElementById('payment-modal-content');
  const spinner = document.getElementById('payment-processing-spinner');
  const successBox = document.getElementById('payment-success-box');
  const failureBox = document.getElementById('payment-failure-box');

  if (modalBody) modalBody.classList.add('d-none');
  if (spinner) spinner.classList.remove('d-none');

  setTimeout(() => {
    if (spinner) spinner.classList.add('d-none');

    if (outcome === 'success') {
      if (successBox) successBox.classList.remove('d-none');
      // Set payment status field in checkout form
      const statusInput = document.getElementById('payment-status-input');
      const txnInput = document.getElementById('transaction-id-input');
      if (statusInput) statusInput.value = 'Paid';
      if (txnInput) txnInput.value = 'TXN_' + Math.floor(10000000 + Math.random() * 90000000);

      setTimeout(() => {
        const form = document.getElementById('checkout-form');
        if (form) form.submit();
      }, 1200);
    } else {
      // Payment failure simulation (TC08 test case)
      if (failureBox) failureBox.classList.remove('d-none');
    }
  }, 1600);
}

function resetPaymentModal() {
  const modalBody = document.getElementById('payment-modal-content');
  const spinner = document.getElementById('payment-processing-spinner');
  const successBox = document.getElementById('payment-success-box');
  const failureBox = document.getElementById('payment-failure-box');

  if (modalBody) modalBody.classList.remove('d-none');
  if (spinner) spinner.classList.add('d-none');
  if (successBox) successBox.classList.add('d-none');
  if (failureBox) failureBox.classList.add('d-none');
}
