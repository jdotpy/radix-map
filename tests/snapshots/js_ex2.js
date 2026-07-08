// ============================================================================
// 1. MODULE EXPORTS & ADVANCED DEFINITIONS
// ============================================================================

// Named Export Class
export class OrderManager {
    constructor(id) {
        this.id = id;
    }

    // Standard Class Method definition (should be captured by iter_definitions)
    calculateFinalPrice(basePrice, taxRate) {
        const discount = this.getSegmentDiscount();
        return (basePrice * (1 - discount)) + taxRate;
    }

    // Async Class Method
    async syncRemoteInventory(itemCode) {
        return await fetch(`/api/inv/${itemCode}`);
    }
}

// Inline/Expression Class definition assigned to a constant
const SecondaryLogger = class InternalLogger {
    log(msg) {
        console.log(`[LOG]: ${msg}`);
    }
};


// ============================================================================
// 2. OBJECT LITERAL METHOD SHORTHANDS & PATTERNS
// ============================================================================

// Shorthand object methods and property assignments 
// (Extremely common in configuration files and older Node.js middleware)
const DatabaseController = {
    // Modern ES6 Shorthand Method Definition
    connect(connectionString) {
        return `Connected to ${connectionString}`;
    },

    // Anonymous Function Expression property assignment
    disconnect: function(force) {
        return force ? "Hard shutdown" : "Graceful shutdown";
    },

    // Arrow Function property assignment
    executeQuery: (sql, params) => {
        return `Running query: ${sql}`;
    }
};


// ============================================================================
// 3. EXPORTS, WRAPPERS, AND GHOST DEDUPLICATION TESTING
// ============================================================================

// Exported standard function (ensures parser skips 'export' keyword correctly)
export function globalUtilityService(inputCode, flags) {
    // Nested helper function inside another function
    // (Should NOT leak into your top-level iter_functions map)
    function sanitizeData(raw) {
        return raw.trim().toLowerCase();
    }
    
    return sanitizeData(inputCode);
}

// Arrow function tied directly to a default export
export const formatCurrency = (amount, symbol = '$') => {
    return `${symbol}${amount.toFixed(2)}`;
};


// ============================================================================
// 4. COMPLEX GLOBALS & CORNER CASES
// ============================================================================

// Global variable declarations (to test iter_globals)
export const RUNTIME_ENV = 'production';
let globalSessionToken = null;
var legacyGlobalCounter = 0;

// Destructured variable assignment (often triggers edge case crashes in parsers)
const { maxConnections, timeout } = { maxConnections: 100, timeout: 3000 };