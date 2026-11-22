// ==========================================================================
// Floral Bliss - Main Frontend Scripts
// ==========================================================================

document.addEventListener('DOMContentLoaded', function () {
  // Initialize Bootstrap Toasts and Tooltips if present
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  initDemoLoginFill();
  initCatalogFilters();
  initCartLiveCalculator();
});

// 1. One-Click Demo Credentials Quick Fill
function initDemoLoginFill() {
  const demoButtons = document.querySelectorAll('.demo-fill-btn');
  demoButtons.forEach(btn => {
    btn.addEventListener('click', function () {
      const email = this.getAttribute('data-email');
      const password = this.getAttribute('data-password');
      const role = this.getAttribute('data-role');

      const emailInput = document.getElementById('login-email');
      const passwordInput = document.getElementById('login-password');

      if (emailInput && passwordInput) {
        emailInput.value = email;
        passwordInput.value = password;

        // Visual feedback
        this.classList.add('btn-success');
        const originalText = this.innerHTML;
        this.innerHTML = '<i class="bi bi-check2"></i> Selected!';
        setTimeout(() => {
          this.classList.remove('btn-success');
          this.innerHTML = originalText;
        }, 1200);

        // Highlight inputs
        emailInput.classList.add('is-valid');
        passwordInput.classList.add('is-valid');
      }
    });
  });
}

// 2. Catalog Live Filters (Category, Color, Occasion, Price Slider)
function initCatalogFilters() {
  const searchInput = document.getElementById('catalog-search');
  const categorySelect = document.getElementById('catalog-category');
  const colorSelect = document.getElementById('catalog-color');
  const priceRange = document.getElementById('catalog-price-range');
  const priceDisplay = document.getElementById('catalog-price-val');
  const flowerCards = document.querySelectorAll('.catalog-item');

  if (!flowerCards.length) return;

  function applyFilters() {
    const query = (searchInput ? searchInput.value.toLowerCase().trim() : '');
    const selectedCategory = (categorySelect ? categorySelect.value : 'all');
    const selectedColor = (colorSelect ? colorSelect.value.toLowerCase() : 'all');
    const maxPrice = (priceRange ? parseFloat(priceRange.value) : 99999);

    let matchCount = 0;

    flowerCards.forEach(card => {
      const name = (card.getAttribute('data-name') || '').toLowerCase();
      const category = (card.getAttribute('data-category') || '').toLowerCase();
      const color = (card.getAttribute('data-color') || '').toLowerCase();
      const price = parseFloat(card.getAttribute('data-price') || 0);

      const matchesSearch = !query || name.includes(query) || category.includes(query);
      const matchesCategory = (selectedCategory === 'all' || category === selectedCategory.toLowerCase());
      const matchesColor = (selectedColor === 'all' || color === selectedColor);
      const matchesPrice = price <= maxPrice;

      if (matchesSearch && matchesCategory && matchesColor && matchesPrice) {
        card.style.display = '';
        matchCount++;
      } else {
        card.style.display = 'none';
      }
    });

    const noResultsMsg = document.getElementById('no-catalog-results');
    if (noResultsMsg) {
      noResultsMsg.style.display = matchCount === 0 ? 'block' : 'none';
    }

    const countDisplay = document.getElementById('catalog-count');
    if (countDisplay) {
      countDisplay.textContent = matchCount;
    }
  }

  if (searchInput) searchInput.addEventListener('input', applyFilters);
  if (categorySelect) categorySelect.addEventListener('change', applyFilters);
  if (colorSelect) colorSelect.addEventListener('change', applyFilters);
  if (priceRange) {
    priceRange.addEventListener('input', function () {
      if (priceDisplay) priceDisplay.textContent = '₹' + this.value;
      applyFilters();
    });
  }
}

// 3. Cart Live Calculation & Stock Validation
function initCartLiveCalculator() {
  const cartTable = document.getElementById('cart-items-container');
  if (!cartTable) return;

  calculateCartTotals();

  // Coupon code logic
  const couponBtn = document.getElementById('apply-coupon-btn');
  const couponInput = document.getElementById('coupon-code');
  if (couponBtn && couponInput) {
    couponBtn.addEventListener('click', function () {
      const code = couponInput.value.trim().toUpperCase();
      const feedback = document.getElementById('coupon-feedback');
      if (code === 'FLOWER100' || code === 'BLOSSOM100') {
        window.activeDiscount = 100.00;
        feedback.innerHTML = '<span class="text-success"><i class="bi bi-check-circle"></i> Coupon applied! ₹100 Discount added.</span>';
      } else if (code === 'WELCOME50') {
        window.activeDiscount = 50.00;
        feedback.innerHTML = '<span class="text-success"><i class="bi bi-check-circle"></i> Coupon applied! ₹50 Discount added.</span>';
      } else if (!code) {
        window.activeDiscount = 0.00;
        feedback.innerHTML = '<span class="text-muted">Coupon removed.</span>';
      } else {
        feedback.innerHTML = '<span class="text-danger"><i class="bi bi-exclamation-triangle"></i> Invalid coupon code. Try <b>FLOWER100</b></span>';
      }
      calculateCartTotals();
    });
  }
}

function updateCartQuantity(flowerId, change, maxStock) {
  const qtyInput = document.getElementById(`cart-qty-${flowerId}`);
  if (!qtyInput) return;

  let currentQty = parseInt(qtyInput.value) || 1;
  let newQty = currentQty + change;

  if (newQty < 1) {
    // Confirm item removal
    if (confirm('Do you want to remove this flower from your cart?')) {
      removeCartItem(flowerId);
    }
    return;
  }

  if (newQty > maxStock) {
    alert(`Out of Stock Alert: Sorry, only ${maxStock} units of this flower are available in stock!`);
    qtyInput.value = maxStock;
    return;
  }

  qtyInput.value = newQty;

  // Send update to server via fetch
  fetch('/cart/update', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ flower_id: flowerId, quantity: newQty })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      const itemSubtotal = document.getElementById(`item-subtotal-${flowerId}`);
      if (itemSubtotal) {
        itemSubtotal.textContent = '₹' + data.item_subtotal.toFixed(2);
      }
      calculateCartTotals();
    } else {
      alert(data.message || 'Error updating cart quantity.');
    }
  })
  .catch(err => {
    console.error('Cart update failed', err);
    calculateCartTotals();
  });
}

function removeCartItem(flowerId) {
  fetch('/cart/remove', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ flower_id: flowerId })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      const row = document.getElementById(`cart-row-${flowerId}`);
      if (row) row.remove();
      calculateCartTotals();
      // Reload if empty
      const remainingRows = document.querySelectorAll('.cart-row');
      if (remainingRows.length === 0) {
        window.location.reload();
      }
    }
  });
}

function calculateCartTotals() {
  const rows = document.querySelectorAll('.cart-row');
  let subtotal = 0;

  rows.forEach(row => {
    const price = parseFloat(row.getAttribute('data-price') || 0);
    const qtyInput = row.querySelector('.qty-input');
    const qty = qtyInput ? parseInt(qtyInput.value) || 0 : 0;
    subtotal += (price * qty);
  });

  const subtotalEl = document.getElementById('cart-subtotal');
  const deliveryEl = document.getElementById('cart-delivery');
  const discountEl = document.getElementById('cart-discount');
  const totalEl = document.getElementById('cart-total');

  if (!subtotalEl || !totalEl) return;

  const deliveryCharge = subtotal > 2000 || subtotal === 0 ? 0.00 : 50.00;
  const discount = window.activeDiscount || (subtotal >= 1000 ? 100.00 : 0.00);

  const totalAmount = Math.max(0, subtotal + deliveryCharge - discount);

  subtotalEl.textContent = '₹' + subtotal.toFixed(2);
  if (deliveryEl) deliveryEl.textContent = (deliveryCharge === 0 ? 'FREE' : '₹' + deliveryCharge.toFixed(2));
  if (discountEl) discountEl.textContent = '-₹' + discount.toFixed(2);
  totalEl.textContent = '₹' + totalAmount.toFixed(2);

  const hiddenTotal = document.getElementById('checkout-total-input');
  if (hiddenTotal) hiddenTotal.value = totalAmount.toFixed(2);
}
