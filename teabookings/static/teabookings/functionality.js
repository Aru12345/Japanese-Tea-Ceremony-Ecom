document.addEventListener("DOMContentLoaded", function () {
    const cartCountElem = document.querySelector(".nav .cart-count");
    const addToCartButtons = document.querySelectorAll(".add-to-cart");
    const removeButtons = document.querySelectorAll(".rbtn");
    const checkoutForm = document.getElementById("checkout-form");


    const searchInput = document.querySelector('.searchinput');
    const resultsContainer = document.querySelector('#resultsContainer');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
   
    // Function to update the cart count dynamically
    function updateCartCount() {
        fetch("/cart-count/") // Ensure this URL matches your URL pattern
            .then((response) => response.json())
            .then((data) => {
                const cartCountElem = document.querySelector(".cart-count");
                if (cartCountElem) {
                    cartCountElem.textContent = data.cart_count || 0;
                } else {
                    console.error("Cart count element not found.");
                }
            })
            .catch((error) => console.error("Failed to update cart count:", error));
    }
    

    // Attach event listeners to Add to Cart buttons
    addToCartButtons.forEach((button) => {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            const lessonId = this.getAttribute("data-lesson-id");

            fetch(`{% url 'add_to_cart' lesson_id=0 %}`.replace("0", lessonId), {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
                },
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.success) {
                        updateCartCount(); // Update the count dynamically
                        alert("Item added to cart!");
                    } else {
                        alert(data.message || "Failed to add item to cart.");
                    }
                })
                .catch(() => alert("An error occurred."));
        });
    });

    // Attach event listeners to Remove buttons
    removeButtons.forEach((button) => {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            const form = this.closest("form");

            fetch(form.action, {
                method: "POST",
                headers: {
                    "X-CSRFToken": form.querySelector("[name=csrfmiddlewaretoken]").value,
                },
            })
                .then((response) => {
                    if (response.ok) {
                        form.closest("li").remove(); // Remove the item from the UI
                        updateCartCount();          // Update the cart count dynamically
                        const remainingItems = document.querySelectorAll(".list-group-item");
                        if (remainingItems.length === 0) {
                            const cartContainer = document.querySelector(".container");
                            cartContainer.innerHTML = `<p class="cartUI" style="color: white; font-style: italic;">Your cart is empty.</p>`;
                        }
                    } else {
                        alert("Failed to remove item from cart.");
                    }
                })
                .catch((error) => console.error("Error removing item:", error));
        });
    });

  
    // Attach event listener to Checkout form
    if (checkoutForm) {
        checkoutForm.addEventListener("submit", async function (event) {
            event.preventDefault(); // Prevent the default form submission
            let allFieldsFilled = true;
    
            // Validate date and time inputs
            const dateInputs = document.querySelectorAll("input[type='date']");
            const timeInputs = document.querySelectorAll("input[type='time']");
    
            // Optimize validation using a single loop
            for (const input of [...dateInputs, ...timeInputs]) {
                if (!input.value) {
                    allFieldsFilled = false;
                    input.classList.add("is-invalid"); // Add a visual indicator
                } else {
                    input.classList.remove("is-invalid");
                }
            }
    
            if (!allFieldsFilled) {
                alert("Please fill in all required date and time fields.");
                return; 
            }
    
            // Proceed to Stripe Checkout
            try {
                const response = await fetch(checkoutForm.action, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
                    },
                });
    
                const data = await response.json();
    
                if (data.url) {
                    // Redirect to Stripe Checkout URL
                    window.location.href = data.url;
                } else {
                    alert(data.error || "Failed to initiate checkout.");
                }
            } catch (error) {
                console.error("Error initiating checkout:", error);
            }
        });
    }

    searchInput.addEventListener('input', function () {
        const query = searchInput.value;
        fetch('/search/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken, // Add CSRF token to headers
            },
            body: JSON.stringify({ search_query: query }),
        })
            .then(response => response.json())
            .then(data => {
                resultsContainer.innerHTML = data.html;
            })
            .catch(error => {
                console.error('Error fetching search results:', error);
            });
    });
    

    // Initial call to update the cart count when the page loads
    updateCartCount();
});
