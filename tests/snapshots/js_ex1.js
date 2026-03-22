function calculateTotal(price, tax) {
    const raw = applyDiscount(price);
    return raw + tax;
}

function applyDiscount(p) {
    return p * 0.9;
}