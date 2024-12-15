# Satori Sips

## About

    Satori Sips is a full-stack ecommerce web application designed to give users an experience of Japanese tea ceremonies virtually. The web application is built for a business owner trying to market his services to the global audience. This also bridges the gap between performing this study traditionally under a tea master and learning through modern digital ways which eliminates the need to travel far,
    making this cultural experience accessible to everyone.
    Built with Python and Django, the application handles tasks like user authentication, data management and order processing seamlessly. The frontend is built with Javascript for interactivity and Bootstrap is used for efficent styling ensuring elements are responsive across different devices. External API feature is incorporated using mock payment integration.
    I have utilised code structure and functions for a basic setup using Project 2: Commerce and enhanced UI and add features according to my project objectives.

### Key Features

    1. Registration Features - Users can LogIn/ SignUp and access personal favorites,   previous orders and manage bookings.
    2. Filtering/ Search - Users can seamlessly search for tea classes or filter classes based on difficult thus narrowing down their options according to their interests.
    3. Ecommerce Functionality - Interactive Shopping Cart experience and secure payment getaway with Stripe.
    4. Mobile Responsive Views - Seamless performance across different devices. 


## Design
    The application is designed to provide a seamless user experience ensuring code modularity and maintainibility. The context processor for cart_count is designed to ensure global access across all tempaltes without needing to duplicate code. A check is added to ensure the logic only runs for authenticated users, thus optimising performance and unnecessary database queries. Aditionally, I accounted for cases where user has no items in the cart wiht a default value: 0.
    The Javascript code is utilised for real-time interactivity updates. Using the DOMContentLoaded, I ensured the script runs only after the DOM is loaded. All the forms use Django's CSRF tokens preventing preventing cross-site request forgery attacks and ensuring a secure user experience. fetch() is used to perform asynchronous requests allowing a sleek "Add to Cart" and "Remove from cart" features.
    By designing validations for for date and time during checkout, backend errors are reduced. This is achieved by providing users friendly alerts on wrong inputs.
    By extending Django's AbstractUser, further customizations are made flexible while ensuring robust user authentication system. The use of ManyToManyField for favorites ensures that users can easily interact with their favorite tea lesson, making the platform user-centric. The design of the database is structured to support smooth booking and cart functionalities, ensuring users can easily manage their orders.


## Organization
    This urlpatterns list in the urls.py defines the routing for the application. Each path maps a URL pattern to a specific view function in the views.py file. The views.py file contains the core logic for handling requests and rendering responses.
    - index                 : Renders the home page (branding).
    - tealessons            : Renders all tea lessons with available filtering options.
    - displayFilter         : Displays all tealessons based on user selection.
    - search_tealessons     : Searches tea lessons based on user queries.
    - addFavList            : Adds item to a users favorite list.
    - removeFavList         : Removes an item from a users favorite list.
    - displayFavorite       : Displays all the lessons in a users favorite list.
    - add_to_cart           : Adds an item to a cart or updates its quantity.
    - cart_count            : Returns the number of items in a cart.
    - displaycart           : Displays cart items with total price and allows user for 
                            date/time selection.
    - remove_from_cart      : Removes items from a cart.
    - stripe_checkout       : Proceeds the user to a stripe page for checkout
    - payment_success       : Indicates successful payment.
    - displaybookings       : Renders all bookings past + upcoming.
    - login_view/register   : Handles user authentication /login.
      logout_view
    
    Some other prominent features:-

    - The context_processors.py file contains reusable context logic. The function cart_count provides total number of cart contents which is accessible across all templates.
    - The updateCartCount function present in Javascript file dynamically updates the cart count by fetching the latest cart count and updating the UI.
    - The stripe_checkout method validates inputs before preparing a Stripe Checkout session (Usage of external API Features).


## Getting Started
    - To set up the project, first extract the zipped folder to your desired directory.
    - Head into the folder teaceremony.
    - Install all the dependances required.
    - Run the development server

## Video
    [Demo](https://www.youtube.com/watch?v=PsXSyu8GQVs)


