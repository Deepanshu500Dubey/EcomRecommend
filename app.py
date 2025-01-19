from flask import Flask, request, render_template
import pandas as pd
import random
from flask_sqlalchemy import SQLAlchemy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity





app = Flask(__name__)


trending_products = pd.read_csv("models/trending_products.csv")
train_data = pd.read_csv("models/clean_data.csv")

app.secret_key = "alskdjfwoeieiurlskdjfslkdjf"
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:@localhost/ecom"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Signup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)


class Signin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)


def truncate(text, length):
    if len(text) > length:
        return text[:length] + "..."
    else:
        return text
    
# Register the custom filter
app.jinja_env.filters['truncate'] = truncate



from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def recommend_similar_items(train_data, item_name, recommendations_count=10):
    if item_name not in train_data['Name'].values:
        print(f"Item '{item_name}' not found in the dataset.")
        return pd.DataFrame()
    
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(train_data['Tags'])
    similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
    target_index = train_data[train_data['Name'] == item_name].index[0]
    similarity_scores = list(enumerate(similarity_matrix[target_index]))
    sorted_similarities = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
    top_recommendations = sorted_similarities[1:recommendations_count+1]
    recommended_indices = [item[0] for item in top_recommendations]
    recommended_items = train_data.iloc[recommended_indices][['Name', 'ReviewCount', 'Brand', 'ImageURL', 'Rating']]
    return recommended_items





def recommend_items_using_collaborative_filtering(train_data, target_user_id, recommendations_count=10):
    
    user_item_matrix = train_data.pivot_table(index='ID', columns='ProdID', values='Rating', aggfunc='mean').fillna(0)
    similarity_matrix = cosine_similarity(user_item_matrix)
    target_user_index = user_item_matrix.index.get_loc(target_user_id)
    target_user_similarities = similarity_matrix[target_user_index]
    similar_users_indices = target_user_similarities.argsort()[::-1][1:]
    recommended_items_list = [] 

    for similar_user_index in similar_users_indices:
        similar_user_ratings = user_item_matrix.iloc[similar_user_index]
        unrated_by_target_user = (similar_user_ratings == 0) & (user_item_matrix.iloc[target_user_index] == 0)
        recommended_items_list.extend(user_item_matrix.columns[unrated_by_target_user][:recommendations_count])

    recommended_items = train_data[train_data['ProdID'].isin(recommended_items_list)][['Name', 'ReviewCount', 'Brand', 'ImageURL', 'Rating']]

    return recommended_items.head(10)



def hybrid_recommendations(train_data,target_user_id, item_name, top_n=10):
    
    recommend_simi = recommend_similar_items(train_data,item_name, top_n)
    collaborative_filtering_rec = recommend_items_using_collaborative_filtering(train_data,target_user_id, top_n)
    hybrid_rec = pd.concat([recommend_simi, collaborative_filtering_rec]).drop_duplicates()
    
    return hybrid_rec.head(10)


random_image_urls = [
    "static/img/img_1.png",
    "static/img/img_2.png",
    "static/img/img_3.png",
    "static/img/img_4.png",
    "static/img/img_5.png",
    "static/img/img_6.png",
    "static/img/img_7.png",
    "static/img/img_8.png",
]


@app.route("/")
def index():
    random_product_image_urls = [random.choice(random_image_urls) for _ in range(len(trending_products))]
    price = [40, 50, 60, 70, 100, 122, 106, 50, 30, 50]
    return render_template('index.html',trending_products=trending_products.head(8),truncate = truncate,
                           random_product_image_urls=random_product_image_urls,
                           random_price = random.choice(price))

@app.route("/main")
def main():
    hybrid_recommend = hybrid_recommendations(train_data,1, "gel", top_n=10) 
    return render_template('main.html', hybrid_recommend=hybrid_recommend)



@app.route("/index")
def indexredirect():
    random_product_image_urls = [random.choice(random_image_urls) for _ in range(len(trending_products))]
    price = [40, 50, 60, 70, 100, 122, 106, 50, 30, 50]
    return render_template('index.html', trending_products=trending_products.head(8), truncate=truncate,
                           random_product_image_urls=random_product_image_urls,
                           random_price=random.choice(price))

from flask import session

@app.route("/signup", methods=['POST','GET'])
def signup():
    if request.method=='POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        new_signup = Signup(username=username, email=email, password=password)
        db.session.add(new_signup)
        db.session.commit()

        # Create a list of random image URLs for each product
        random_product_image_urls = [random.choice(random_image_urls) for _ in range(len(trending_products))]
        price = [40, 50, 60, 70, 100, 122, 106, 50, 30, 50]
        return render_template('index.html', trending_products=trending_products.head(8), truncate=truncate,
                               random_product_image_urls=random_product_image_urls, random_price=random.choice(price),
                               signup_message='User signed up successfully!'
                               )

@app.route('/signin', methods=['POST', 'GET'])
def signin():
    if request.method == 'POST':
        username = request.form['signinUsername']
        password = request.form['signinPassword']
        
        user = Signin.query.filter_by(username=username).first()
        if user :
            session['user_id'] = user.id
            session['username'] = user.username 
            random_product_image_urls = [random.choice(random_image_urls) for _ in range(len(trending_products))]
            price = [40, 50, 60, 70, 100, 122, 106, 50, 30, 50]
            
            return render_template(
                'index.html',
                trending_products=trending_products.head(8),
                truncate=truncate,
                random_product_image_urls=random_product_image_urls,
                random_price=random.choice(price),
                signup_message=f'Welcome back, {user.username}!'
            )
        else:
            return render_template('index.html',trending_products=trending_products.head(8), random_product_image_urls=random_product_image_urls,error='Invalid username or password.')





@app.route("/recommendations", methods=['POST', 'GET'])
def recommendations():
    if request.method == 'POST':
        user_id = session.get('user_id')
        if not user_id:
            return render_template('signin.html', error='Please sign in to view recommendations.')

        prod = request.form.get('prod')
        nbr = request.form.get('nbr')

        if not prod or not nbr:
            return render_template('main.html', message="Invalid input. Please try again.")

        nbr = int(nbr)  # Convert to integer as it comes as a string from form
        
        # Fetch recommendations
        hybrid_recommend = hybrid_recommendations(train_data, target_user_id=user_id, item_name=prod, top_n=nbr)

        # If no recommendations found
        if hybrid_recommend is None or hybrid_recommend.empty:
            message = "No recommendations available for this product."
            return render_template('main.html', message=message, hybrid_recommend=hybrid_recommend)
        else:
            # Prepare random product image URLs and prices
            random_product_image_urls = [random.choice(random_image_urls) for _ in range(len(hybrid_recommend))]
            price = [40, 50, 60, 70, 100, 122, 106, 50, 30, 50]

            message = "Recommendations generated successfully."
            
            return render_template(
                'main.html',
                hybrid_recommend=hybrid_recommend if hybrid_recommend is not None else [],  # Ensures it returns an empty list if None
                truncate=truncate,
                random_product_image_urls=random_product_image_urls,
                random_price=random.choice(price),
                user_message=f'Recommendations for User ID: {user_id}',
                message=message
            )



if __name__=='__main__':
    app.run(debug=True)