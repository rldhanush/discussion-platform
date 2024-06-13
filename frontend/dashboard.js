document.addEventListener('DOMContentLoaded', function() {
    fetch('/current_user')
        .then(response => response.json())
        .then(data => {
            document.getElementById('welcomeMessage').textContent = `Welcome, ${data.name}`;
        });
});


async function searchUser() {
    const searchInput = document.getElementById("searchUser").value;

    try {
        const response = await fetch(`/search_user?name=${searchInput}`);
        if (!response.ok) {
            throw new Error("Failed to search user");
        }

        const searchResult = await response.json();
        displaySearchResult(searchResult);
    } catch (error) {
        console.error("Error searching user:", error);
        alert('Failed to search user');
    }
}

function displaySearchResult(searchResult) {
    const userSearchResult = document.getElementById("userSearchResult");
    userSearchResult.innerHTML = "";

    searchResult.forEach(user => {
        const userDiv = document.createElement("div");
        userDiv.classList.add("user-search-result");
        userDiv.innerHTML = `
            <h3>${user.name}</h3>
            <button onclick="followUser('${user.id}')">Follow</button>
        `;
        userSearchResult.appendChild(userDiv);
    });
}


async function followUser(userName) {
    try {
        const response = await fetch(`/follow_user/${userName}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        if (!response.ok) {
            throw new Error("Failed to follow user");
        }

        const followResult = await response.json();
        console.log(followResult); 
    } catch (error) {
        console.error("Error following user:", error);
        displayError(error.message);
    }
}

async function postDiscussion() {
    const form = document.getElementById('discussionForm');
    const formData = new FormData(form);
    
    try {
        const response = await fetch('/post_discussion', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Failed to post discussion');
        }
        const result = await response.json();
        document.getElementById('response').textContent = result.message;
        form.reset();
    } catch (error) {
        console.error('Error posting discussion:', error);
        document.getElementById('response').textContent = error.message;
    }
    // Clear the response message after 15 seconds
    setTimeout(() => {
        document.getElementById('response').textContent = '';
    }, 15000);
     
}

async function showDiscussions() {
    try {
        const response = await fetch('/get_discussions');
        if (!response.ok) {
            throw new Error('Failed to fetch discussions');
        }
        const discussions = await response.json();
        const discussionsContainer = document.getElementById('discussionsContainer');
        discussionsContainer.innerHTML = '';

        for (const discussion of discussions) {
            const discussionDiv = document.createElement('div');
            discussionDiv.classList.add('discussion');
            discussionDiv.innerHTML = `
                <p>Text : ${discussion.text}</p>
                ${discussion.image ? `<img src="/uploads/${discussion.image}" alt="Discussion Image" style="width: 100px; height: 100px;">` : ''}
                <p>Hash Tags: ${discussion.hashtags.join(', ')}</p>
                <p>Created On: ${new Date(discussion.created_on).toLocaleString()}</p>
                <p>Likes: ${discussion.likes}</p>
                <button  class="like-button" onclick="likeDiscussion('${discussion._id}')">Like</button>
                <div class="comments-section">
                    <p>Comments:</p>
                    <div class="comments-list" id="commentsList_${discussion._id}">
                        <!-- Comments will be dynamically added here -->
                    </div>
                </div>
                <textarea id="commentText_${discussion._id}" rows="2" cols="50" placeholder="Add your comment..."></textarea>
                <button onclick="commentOnDiscussion('${discussion._id}')">Comment</button>
            `;
            discussionsContainer.appendChild(discussionDiv);
            displayComments(discussion._id);

        }
    } catch (error) {
        console.error('Error fetching discussions:', error);
    }
}

function clearDiscussions() {
    document.getElementById('discussionsContainer').innerHTML = '';
}


async function likeDiscussion(postId) {
    try {
        const response = await fetch(`/like_post/${postId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        if (!response.ok) {
            throw new Error('Failed to like discussion');
        }
        const result = await response.json();
        console.log(result.message);  // Log success message
        // Optionally update UI to reflect the incremented likes count
        await showDiscussions();  // Refresh the discussions list after liking
    } catch (error) {
        console.error('Error liking discussion:', error);
        // Optionally display an error message to the user
    }
}

async function commentOnDiscussion(postId) {
    try {
        const commentTextElement = document.getElementById(`commentText_${postId}`);
        const commentText = commentTextElement.value.trim();

        if (!commentText) {
            return; 
        }

        const data = {
            text: commentText
        };

        const response = await fetch(`/comment_on_post/${postId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error('Failed to add comment');
        }

        // Update the UI to display the new comment
        const comment = await response.json();
        displayComments(postId);
        commentTextElement.value = '';
        console.log('Comment added successfully');
    } catch (error) {
        console.error('Error adding comment:', error);
    }
}

async function displayComments(postId) {
    try {
        const response = await fetch(`/get_comments/${postId}`); // Fetch comments for the post
        if (!response.ok) {
            throw new Error('Failed to fetch comments');
        }

        const comments = await response.json();
        const commentsList = document.getElementById(`commentsList_${postId}`);
        if (commentsList) {
            commentsList.innerHTML = ''; 
            comments.forEach(comment => {
                const commentDiv = document.createElement('div');
                commentDiv.classList.add('comment');
                commentDiv.innerHTML = `<strong>${comment.user_name}</strong>: ${comment.text}`;
                commentsList.appendChild(commentDiv);
            });
        }
    } catch (error) {
        console.error('Error displaying comments:', error);
    }
}
