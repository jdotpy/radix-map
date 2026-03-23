function calculateTotal(price, tax) {
    const raw = applyDiscount(price);
    return raw + tax;
}

function applyDiscount(p) {
    return p * 0.9;
}

const a = 10;

const foobar = () => {
    console.log('im an arrow function')
}

const anonymousExpress = function(a, b) {
    return a + b;
};