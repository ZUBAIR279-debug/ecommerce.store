// ================================================================
//  BIN MAQSOOD – CART LOGIC (localStorage)
// ================================================================

// -------- Helpers --------
function getCart() {
    try {
        return JSON.parse(localStorage.getItem('cart')) || [];
    } catch {
        return [];
    }
}

function saveCart(cart) {
    localStorage.setItem('cart', JSON.stringify(cart));
    updateBadge();
}

// -------- Update Badge --------
function updateBadge() {
    const cart = getCart();
    const total = cart.reduce((sum, item) => sum + (item.qty || 0), 0);
    const badge = document.getElementById('cart-badge');
    if (badge) {
        badge.textContent = total;
        if (total > 0) {
            badge.classList.remove('hidden');
            badge.classList.add('pulse');
            setTimeout(() => badge.classList.remove('pulse'), 300);
        } else {
            badge.classList.add('hidden');
        }
    }
}

// -------- ADD TO CART (with Toast) --------
function addToCart(product, qty = 1) {
    if (!product || !product.id) {
        console.error('❌ Invalid product');
        return;
    }

    const cart = getCart();
    const existing = cart.find(item => item.id === product.id);

    if (existing) {
        existing.qty = (existing.qty || 0) + qty;
    } else {
        cart.push({
            id: product.id,
            title: product.title || 'Product',
            price: product.price || 0,
            img: product.img || '/static/uploads/1.png',
            qty: qty
        });
    }

    saveCart(cart);
    console.log(`✅ Added "${product.title}" (x${qty}) to cart`);

    // ----- Netflix style Toast Notification -----
    if (typeof showToast === 'function') {
        showToast(`✨ ${product.title} added to cart!`);
    } else {
        // Fallback: simple alert agar showToast available nahi
        alert(`✨ ${product.title} added to cart!`);
    }
}

// -------- Remove --------
function removeFromCart(productId) {
    let cart = getCart();
    cart = cart.filter(item => item.id !== productId);
    saveCart(cart);
    renderCart();
}

// -------- Update Qty --------
function updateCartQty(productId, delta) {
    const cart = getCart();
    const item = cart.find(i => i.id === productId);
    if (!item) return;

    const newQty = (item.qty || 0) + delta;
    if (newQty <= 0) {
        removeFromCart(productId);
        return;
    }

    item.qty = newQty;
    saveCart(cart);
    renderCart();
}

// -------- Render Cart Page --------
function renderCart() {
    const container = document.getElementById('cart-container');
    if (!container) return;

    const cart = getCart();

    if (cart.length === 0) {
        container.innerHTML = `
            <div class="text-center py-12">
                <i class="fas fa-shopping-bag text-5xl text-gray-300 mb-4"></i>
                <p class="text-[#1C1B19]/60 text-lg">Your cart is empty.</p>
                <a href="/" class="inline-block mt-4 bg-[#9A7B56] hover:bg-[#8a6a48] text-white px-6 py-2.5 rounded-full text-sm transition">Start Shopping</a>
            </div>
        `;
        return;
    }

    let html = `
        <div class="overflow-x-auto">
            <table class="w-full text-sm">
                <thead>
                    <tr class="border-b border-[#e8e3da] text-left text-[#1C1B19]/60">
                        <th class="pb-3 font-medium">Product</th>
                        <th class="pb-3 font-medium">Price</th>
                        <th class="pb-3 font-medium text-center">Quantity</th>
                        <th class="pb-3 font-medium text-right">Total</th>
                        <th class="pb-3 font-medium text-right">Action</th>
                    </tr>
                </thead>
                <tbody>
    `;

    let grandTotal = 0;

    cart.forEach(item => {
        const total = item.price * item.qty;
        grandTotal += total;

        html += `
            <tr class="border-b border-[#e8e3da]/50">
                <td class="py-4 flex items-center gap-4">
                    <img src="${item.img}" alt="${item.title}" class="w-16 h-16 rounded-lg object-cover" />
                    <span class="font-medium text-[#1C1B19]">${item.title}</span>
                </td>
                <td class="py-4">Rs. ${Number(item.price).toLocaleString()}</td>
                <td class="py-4">
                    <div class="flex items-center justify-center gap-2">
                        <button onclick="updateCartQty(${item.id}, -1)" class="qty-btn text-sm">−</button>
                        <span class="w-8 text-center font-medium">${item.qty}</span>
                        <button onclick="updateCartQty(${item.id}, 1)" class="qty-btn text-sm">+</button>
                    </div>
                </td>
                <td class="py-4 text-right font-semibold">Rs. ${total.toLocaleString()}</td>
                <td class="py-4 text-right">
                    <button onclick="removeFromCart(${item.id})" class="text-red-400 hover:text-red-600 transition text-sm">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });

    html += `
                </tbody>
            </table>
        </div>

        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mt-6 pt-4 border-t border-[#e8e3da]">
            <div>
                <p class="text-sm text-[#1C1B19]/60">Subtotal</p>
                <p class="text-2xl font-bold text-[#1C1B19]">Rs. ${grandTotal.toLocaleString()}</p>
                <p class="text-xs text-[#1C1B19]/40 mt-1">Delivery charges calculated at checkout</p>
            </div>
            <div class="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
                <a href="/" class="text-center border border-[#1C1B19] hover:bg-[#1C1B19] hover:text-white text-[#1C1B19] font-medium px-6 py-3 rounded-full transition">Continue Shopping</a>
                <a href="/checkout" class="text-center bg-[#1C1B19] hover:bg-[#9A7B56] text-white font-medium px-8 py-3 rounded-full transition shadow-lg hover:shadow-xl">Proceed to Checkout</a>
            </div>
        </div>
    `;

    container.innerHTML = html;
}

// -------- Init on page load --------
document.addEventListener('DOMContentLoaded', function() {
    updateBadge();
    if (document.getElementById('cart-container')) {
        renderCart();
    }
    console.log('🛒 Cart system ready!');
});

// Expose to global scope
window.addToCart = addToCart;
window.removeFromCart = removeFromCart;
window.updateCartQty = updateCartQty;
window.renderCart = renderCart;
window.updateBadge = updateBadge;