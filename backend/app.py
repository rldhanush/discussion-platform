from bson import ObjectId
from flask import Flask, jsonify, request, send_from_directory, session
from flask_pymongo import PyMongo
from werkzeug.utils import secure_filename
import os
from datetime import datetime

# Generate a random secret key
secret_key = os.urandom(24)

app = Flask(__name__, static_folder="../frontend", static_url_path="")
app.config["MONGO_URI"] = "mongodb+srv://dhanushrl:dhanushrl12345@clusterspine.bi9vo04.mongodb.net/spineai?retryWrites=true&w=majority"
app.config['SECRET_KEY'] = secret_key
app.config['UPLOAD_FOLDER'] = '../frontend/uploads'

mongo = PyMongo(app)

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

# Route to serve images from frontend/uploads
@app.route('/uploads/<path:filename>')
def serve_image(filename):
    return send_from_directory('../frontend/uploads', filename)

@app.route('/signup', methods=['POST'])
def signup():
    print("Request Data:", request.json)
    user_data = request.json
    # Check if mobile number is already in use
    existing_user = mongo.db.users.find_one({'mobile': user_data['mobile']})
    if existing_user:
        return jsonify({'error': 'Mobile number already in use'}), 400
    
    # Check if email is already in use
    existing_user = mongo.db.users.find_one({'email': user_data['email']})
    if existing_user:
        return jsonify({'error': 'Email already in use'}), 400
    
    # If mobile number and email are unique, insert the user data into the database
    mongo.db.users.insert_one(user_data)
    return jsonify({'message': 'User added successfully'}), 201
    
@app.route('/login', methods=['POST'])
def login():
    print("Request Data:", request.json)
    user_data = request.json
    email = user_data.get('email')
    password = user_data.get('password')

    # Find user by email
    user = mongo.db.users.find_one({'email': email})

    if not user:
        return jsonify({'error': 'User does not exist'}), 400

    if user['password'] == password:
        # Store email in session
        session['email'] = email
        return jsonify({'message': 'Login successful'}), 200
   
    return jsonify({'error': 'Invalid credentials'}), 400

@app.route('/current_user', methods=['GET'])
def current_user():
    user = mongo.db.users.find_one({'email': session['email']})
    return jsonify({'name': user['name']})

@app.route('/search_user', methods=['GET'])
def search_user():
    name = request.args.get('name')
    # Query user data from the MongoDB collection
    users = list(mongo.db.users.find({"name": {"$regex": name, "$options": "i"}}))
    # Check if any user is found
    if not users:
        return jsonify({'error': 'User not found'}), 404
    # Prepare the response data
    search_results = [{"name": user["name"], "id": str(user["_id"])} for user in users]
    return jsonify(search_results)

@app.route('/follow_user/<user_name>', methods=['POST'])
def follow_user(user_name):
    try:
        # Get the current user from the session
        current_user = mongo.db.users.find_one({'email': session.get('email')})
        if not current_user:
            return jsonify({'error': 'User not authenticated'}), 401

        # Add the user to the current user's following list
        followings = current_user.get('followings', [])
        if user_name not in followings:
            followings.append(user_name)
            # Update the user document in the database
            mongo.db.users.update_one({'email': session['email']}, {'$set': {'followings': followings}})
            return jsonify({'message': f'You are now following {user_name}'}), 200
        else:
            return jsonify({'message': f'You are already following {user_name}'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/post_discussion', methods=['POST'])
def post_discussion():
    try:
        text = request.form['text']
        hashtags = request.form['hashtags'].split(',')
        image = request.files.get('image')
        
        image_path = None
        if image:
            image_filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image.save(image_path)
        
        discussion_data = {
            'text': text,
            'image': image_path,
            'hashtags': hashtags,
            'created_on': datetime.now(),
            'likes': 0,
            'comments': []
        }

        mongo.db.discussions.insert_one(discussion_data)
        return jsonify({'message': 'Discussion posted successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_discussions', methods=['GET'])
def get_discussions():
    discussions = mongo.db.discussions.find()
    discussions_list = []
    for discussion in discussions:
        discussion_data = {
            '_id': str(discussion['_id']),
            'text': discussion['text'],
            'image': os.path.basename(discussion['image']),
            'hashtags': discussion['hashtags'],
            'created_on': discussion['created_on'],
            'likes': discussion['likes'],
            'comments': len(discussion['comments'])
        }
        discussions_list.append(discussion_data)
    return jsonify(discussions_list)

@app.route('/like_post/<post_id>', methods=['POST'])
def like_post(post_id):
    try:
        # Update the likes count for the specified post_id
        result = mongo.db.discussions.update_one(
            {'_id': ObjectId(post_id)},
            {'$inc': {'likes': 1}}
        )

        if result.modified_count == 0:
            return jsonify({'error': 'Post not found'}), 404

        return jsonify({'message': 'Post liked successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/comment_on_post/<post_id>', methods=['POST'])
def comment_on_post(post_id):
    try:
        data = request.json
        text = data.get('text')

        # Fetch current user from session or database
        if 'email' in session:
            user = mongo.db.users.find_one({'email': session['email']})
            if user:
                user_name = user['name']
        else:
            return jsonify({'error': 'User does not exist'}), 400
        
        comment = {
            'user_name': user_name,
            'text': text,
            'created_at': datetime.now()
        }

        result = mongo.db.discussions.update_one(
            {'_id': ObjectId(post_id)},
            {'$push': {'comments': comment}}
        )

        if result.modified_count == 1:
            return jsonify(comment), 201
        else:
            return jsonify({'error': 'Failed to add comment'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

# Route to fetch comments for a specific post
@app.route('/get_comments/<post_id>', methods=['GET'])
def get_comments(post_id):
    try:
        discussion = mongo.db.discussions.find_one({'_id': ObjectId(post_id)})
        if not discussion:
            return jsonify({'error': 'Discussion not found'}), 404

        comments = discussion.get('comments', [])
        return jsonify(comments), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


#search discussion based on text and hashtags
@app.route('/search_discussions', methods=['GET'])
def search_discussions():
    try:
        query = request.args.get('query', '')
        if not query:
            return jsonify({'error': 'No search query provided'}), 400

        # Search for discussions that contain the query in the text or hashtags
        search_condition = {
            '$or': [
                {'text': {'$regex': query, '$options': 'i'}},  # case-insensitive search in text
                {'hashtags': {'$regex': query, '$options': 'i'}}  # case-insensitive search in hashtags
            ]
        }
        discussions = mongo.db.discussions.find(search_condition)
        
        result = []
        for discussion in discussions:
            discussion['_id'] = str(discussion['_id']) 
            result.append(discussion)
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


#modify discussion post based on ID
@app.route('/modify_discussion/<discussion_id>', methods=['PUT'])
def modify_discussion(discussion_id):
    try:
        data = request.json
        update_fields = {}

        if 'text' in data:
            update_fields['text'] = data['text']
        if 'hashtags' in data:
            update_fields['hashtags'] = data['hashtags']

        result = mongo.db.discussions.update_one(
            {'_id': ObjectId(discussion_id)},
            {'$set': update_fields}
        )
        
        if result.matched_count == 1:
            return jsonify({'message': 'Discussion updated successfully'}), 200
        else:
            return jsonify({'error': 'Discussion not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#delete discussion post based on ID
@app.route('/delete_discussion/<discussion_id>', methods=['DELETE'])
def delete_discussion(discussion_id):
    try:
        result = mongo.db.discussions.delete_one({'_id': ObjectId(discussion_id)})
        if result.deleted_count == 1:
            return jsonify({'message': 'Discussion deleted successfully'}), 200
        else:
            return jsonify({'error': 'Discussion not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)

