This project is a web application built with Flask and MongoDB, designed to facilitate social interactions through discussions. Users can sign up, log in, and perform actions such as creating posts with text and images, liking posts, commenting on discussions, and following other users. The application supports searching for users and discussions based on text or hashtags, providing a dynamic and engaging platform for social interactions.

Key Features:
    User Authentication: Secure user sign-up and login functionality.
    Discussion Creation: Create posts with text, optional images, and hashtags.
    Interaction Features: Like posts, comment on discussions, and follow other users.
    Search Functionality: Search for users and discussions based on text or hashtags.
    Dynamic UI: Updates in real-time with asynchronous data fetching.

Technologies Used:
    Backend: Flask, MongoDB, Flask-PyMongo for database interactions.
    Frontend: HTML, CSS, JavaScript for dynamic and responsive user interfaces.
    File Uploads: Flask's secure file handling for image uploads.
    Session Management: Flask sessions for user authentication and state management.

Setup Instructions:
    Clone the repository from [GitHub URL].
    Install dependencies from requirements.txt.
    Configure MongoDB URI in the Flask application (app.py).
    Run the Flask application (python app.py) and navigate to http://localhost:5000.


------------------------------------
Components and Responsibilities:

Application Layer (Flask App):

Routes: Handle incoming HTTP requests and delegate processing to appropriate controllers.

Controllers: Business logic handling, interacting with services and database.

Services: Encapsulate business rules and orchestrate interactions between controllers and database.

Database (MongoDB):

Collections:

- users: Store user information including name, email, password, followers, and followings.
- discussions: Store discussion posts with attributes such as text, image, hashtags, likes, and comments.
- comments: Store comments related to discussions with attributes like user name, text, and timestamps.

Detailed Design:
1. User Management:
Endpoints:
    /signup: Register a new user.
    /login: Authenticate user login.
    /current_user: Fetch details of the currently logged-in user.
    /search_user: Search for users by name.
    /follow_user/<user_name>: Follow another user.

Controllers:

UserController:
    signup(user_data): Validate and insert user into users collection.
    login(email, password): Authenticate user credentials.
    current_user(): Retrieve details of the logged-in user.
    search_user(name): Search users by name.
    follow_user(current_user_email, user_name_to_follow): Update current user's followings list.


2. Discussions and Posts:

Endpoints:
    /post_discussion: Create a new discussion post.
    /get_discussions: Fetch all discussion posts.
    /like_post/<post_id>: Like a specific discussion post.
    /modify_discussion/<discussion_id>: Update an existing discussion post.
    /delete_discussion/<discussion_id>: Delete an existing discussion post.

Controllers:
    post_discussion(text, hashtags, image): Create a new discussion post.
    get_discussions(): Retrieve all discussion posts.
    like_post(post_id): Increment like count for a post.
    modify_discussion(discussion_id, update_fields): Update an existing discussion post.
    delete_discussion(discussion_id): Remove a discussion post from the database.


3. Comments:

Endpoints:
    /comment_on_post/<post_id>: Add a comment to a specific discussion post.
    /get_comments/<post_id>: Fetch comments for a specific discussion post.
    /modify_comment/<comment_id>: Update an existing comment (if needed).
    /delete_comment/<comment_id>: Delete an existing comment.

CommentController:
    comment_on_post(post_id, user_name, text): Add a new comment to a discussion post.
    get_comments(post_id): Retrieve comments for a specific discussion post.

Interaction Flow:

User Actions:

    User signs up, logs in, searches for other users, follows/unfollows users.
    Users create discussion posts, like posts, modify/delete their posts.
    Users comment on posts.

Data Flow:

    Requests are received by Flask routes, which delegate to controllers.
    Controllers interact with services to validate inputs and perform business logic.
    Services handle database interactions through MongoDB queries.