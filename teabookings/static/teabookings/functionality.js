document.addEventListener("DOMContentLoaded", function () {
  
  const addToCartButtons = document.querySelectorAll(".add-to-cart");
  const removeButtons = document.querySelectorAll(".rbtn");
  const checkoutForm = document.getElementById("checkout-form");
  const searchInput = document.querySelector(".searchinput");
  const resultsContainer = document.querySelector("#resultsContainer");
  const csrfTokenElement = document.querySelector("[name=csrfmiddlewaretoken]");
  const csrfToken = csrfTokenElement ? csrfTokenElement.value : null;
  const today = new Date().toISOString().split('T')[0];

  // Initial call to update the cart count when the page loads
  updateCartCount();
 
  // Function to update the cart count 
  function updateCartCount() {
    fetch("/cart-count/") 
      .then((response) => response.json())
      .then((data) => {
        const cartCountElem = document.querySelector(".cart-count");
        if (cartCountElem) {
          cartCountElem.textContent = data.cart_count || 0;
        } else {
          console.error("Check...");
        }
      })
      .catch((error) => console.error("Failed", error));
  }
    

  // Event Listners
  if (searchInput) {
    searchInput.addEventListener('input', function () {
      const query = searchInput.value;
      fetch('/search/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken, 
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
  }

  addToCartButtons.forEach((button) => {   
    button.addEventListener("click", function (event) {
      event.preventDefault();
      const lessonId = this.getAttribute("data-lesson-id");

      fetch(`{% url 'add_to_cart' lesson_id=0 %}`.replace("0", lessonId), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value, // CSRF token
        },
      })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          updateCartCount(); 
        } else {
          alert(data.message || "Error");
        }
      })
      .catch(() => alert("Error"));
    });

  });

  removeButtons.forEach((button) => {
    button.addEventListener("click", function (event) {
      event.preventDefault();
      const form = this.closest("form"); // Finds the closest parent form element associated with click button

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
          alert("Failed");    
        }
      })
      .catch((error) => console.error("Error removing item:", error));
    });
  });

  if (checkoutForm) {

    checkoutForm.addEventListener("submit", async function (event) {
      event.preventDefault();
      let allFieldsValid = true; 
      
      // Validate date and time inputs
      const dateInputs = document.querySelectorAll("input[type='date']");
      const timeInputs = document.querySelectorAll("input[type='time']");

      dateInputs.forEach((dateInput) => {
        const selectedDate = new Date(dateInput.value);
        if (!dateInput.value || selectedDate < new Date(today)) {
          allFieldsValid = false;
          dateInput.classList.add("is-invalid");
            alert("Please select a valid date.");
        } else {
          dateInput.classList.remove("is-invalid");
        }
      });

      timeInputs.forEach((timeInput) => {
        if (!timeInput.value) {
          allFieldsValid = false;
          timeInput.classList.add("is-invalid");
            alert("Please select a valid time.");
        } else {
          timeInput.classList.remove("is-invalid");
        }
      });

      if (!allFieldsValid) {
        return; // Prevent form submission if validation fails
      }

      // Proceed with form submission if all fields are valid
      const formData = new FormData();
      dateInputs.forEach((dateInput) => formData.append(dateInput.name, dateInput.value));
      timeInputs.forEach((timeInput) => formData.append(timeInput.name, timeInput.value));

      // Include the CSRF token in the request
      formData.append("csrfmiddlewaretoken", document.querySelector("[name=csrfmiddlewaretoken]").value);
      try {
        const response = await fetch(checkoutForm.action, {
          method: "POST",
          body: formData, // Send the form data
        });
        const data = await response.json();
        if (data.url) {
          // Redirect to Stripe Checkout URL
          window.location.href = data.url;
        } else {
          alert(data.error || "Failed to initiate checkout.");
        }
      } catch(error) {
        console.error("Error initiating checkout:", error);
      }
    });
  }

});
