document.addEventListener("DOMContentLoaded", function () {
    const cartCountElem = document.querySelector(".nav .cart-count");
    const addToCartButtons = document.querySelectorAll(".add-to-cart");

    // Function to update the cart count dynamically
    function updateCartCount() {
        fetch("/cart-count/")
            .then((response) => response.json())
            .then((data) => {
                // Update the cart count element if it exists
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

    // Initial call to update the cart count when the page loads
    updateCartCount();
});
