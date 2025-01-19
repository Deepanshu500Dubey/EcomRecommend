
E-Commerce Recommendation System

This project is an E-Commerce Recommendation System built using Flask. It implements hybrid recommendation techniques combining collaborative filtering and content-based filtering to generate personalized product recommendations.


## Features
1) Hybrid Recommendation System

Combines content-based filtering and collaborative filtering to suggest the most relevant products to users.

Successfully implemented hybrid recommendation logic through the following functions:

recommend_similar_items: Provides recommendations based on product tags using TF-IDF and cosine similarity.

recommend_items_using_collaborative_filtering: Suggests products based on user-product interaction data.

hybrid_recommendations: Merges both recommendation techniques for a robust recommendation system.

2) User Authentication

Signup: New users can register with a username, email, and password.

Signin: Existing users can log in to access personalized recommendations.

3) Dynamic Product Display

Displays trending products with randomized images and prices.

4) Personalized Recommendations

Generates tailored recommendations for logged-in users based on their input and browsing data.
## Prerequisites

Ensure you have the following installed on your system:

Python 3.x

Flask

MySQL

Pandas

Scikit-learn
## Key Functions

1) recommend_similar_items

Uses TF-IDF vectorization and cosine similarity to recommend items with similar tags.

2) recommend_items_using_collaborative_filtering

Creates a user-item interaction matrix and suggests items based on user similarity.

3) hybrid_recommendations

Combines content-based and collaborative filtering recommendations, ensuring diverse and relevant results.
## Example Workflow

1) User signs up or logs in.

2) User inputs a product name and the number of recommendations they want.

3) The system fetches hybrid recommendations based on the user's input.

4) Results are displayed dynamically with product images, names, ratings, and more.
