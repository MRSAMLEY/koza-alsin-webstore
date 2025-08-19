// Mobile Menu Toggle
const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
const mainNav = document.querySelector('.main-nav');
const closeMenu = document.querySelector('.close-menu');

mobileMenuBtn.addEventListener('click', () => {
    mainNav.classList.add('active');
});

closeMenu.addEventListener('click', () => {
    mainNav.classList.remove('active');
});

// Close menu when clicking on a link
document.querySelectorAll('.main-nav a').forEach(link => {
    link.addEventListener('click', () => {
        mainNav.classList.remove('active');
    });
});

// Sample product data
const products = [
    {
        id: 1,
        name: "Wireless Headphones",
        price: 59.99,
        image: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60",
        rating: 4
    },
    {
        id: 2,
        name: "Smart Watch",
        price: 129.99,
        image: "https://images.unsplash.com/photo-1523275335684-37898b6baf30?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60",
        rating: 5
    },
    {
        id: 3,
        name: "Bluetooth Speaker",
        price: 39.99,
        image: "https://images.unsplash.com/photo-1572569511254-d8f925fe2cbb?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60",
        rating: 4
    },
    {
        id: 4,
        name: "Phone Case",
        price: 19.99,
        image: "https://images.unsplash.com/photo-1601784551446-20c9e07cdbdb?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60",
        rating: 3
    },
    {
        id: 5,
        name: "Laptop Backpack",
        price: 49.99,
        image: "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60",
        rating: 5
    },
    {
        id: 6,
        name: "Wireless Charger",
        price: 29.99,
        image: "https://images.unsplash.com/photo-1583394838336-acd977736f90?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60",
        rating: 4
    }
];

// Display products
const productsGrid = document.querySelector('.products-grid');

products.forEach(product => {
    const productElement = document.createElement('div');
    productElement.classList.add('product');
    
    let stars = '';
    for (let i = 0; i < 5; i++) {
        if (i < product.rating) {
            stars += '<i class="fas fa-star"></i>';
        } else {
            stars += '<i class="far fa-star"></i>';
        }
    }
    
    productElement.innerHTML = `
        <img src="${product.image}" alt="${product.name}" class="product-img">
        <div class="product-info">
            <h3 class="product-title">${product.name}</h3>
            <div class="product-rating">${stars}</div>
            <span class="product-price">$${product.price.toFixed(2)}</span>
            <button class="add-to-cart" data-id="${product.id}">Add to Cart</button>
        </div>
    `;
    
    productsGrid.appendChild(productElement);
});

// Cart functionality
let cart = [];

document.querySelectorAll('.add-to-cart').forEach(button => {
    button.addEventListener('click', () => {
        const productId = parseInt(button.getAttribute('data-id'));
        const product = products.find(p => p.id === productId);
        
        // Check if product already in cart
        const existingItem = cart.find(item => item.id === productId);
        
        if (existingItem) {
            existingItem.quantity += 1;
        } else {
            cart.push({
                ...product,
                quantity: 1
            });
        }
        
        updateCartCount();
        
        // Show added to cart feedback
        button.textContent = 'Added!';
        button.style.backgroundColor = '#4CAF50';
        
        setTimeout(() => {
            button.textContent = 'Add to Cart';
            button.style.backgroundColor = '';
        }, 1500);
    });
});

function updateCartCount() {
    const totalItems = cart.reduce((total, item) => total + item.quantity, 0);
    document.querySelector('.cart-count').textContent = totalItems;
}