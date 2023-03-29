from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "app.sqlite")

db = SQLAlchemy(app)
ma = Marshmallow(app)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String, nullable=False, unique=True)
    genre = db.Column(db.String, nullable=False)
    mpaa_rating = db.Column(db.String)
    poster_img = db.Column(db.String, unique=True)
    all_reviews = db.relationship('Review', backref='movie', cascade='all,delete,delete-orphan', lazy=True)

    def __init__(self, title, genre, mpaa_rating, poster_img):
        self.title = title
        self.genre = genre
        self.mpaa_rating = mpaa_rating
        self.poster_img = poster_img

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    star_rating = db.Column(db.Float, nullable=False)
    review_text = db.Column(db.Text(300))
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)

    def __init__(self, star_rating, review_text, movie_id):
        self.star_rating = star_rating
        self.review_text = review_text
        self.movie_id = movie_id

class ReviewSchema(ma.Schema):
    class Meta:
        fields = ('id', 'star_rating', 'review_text', 'movie_id')

review_schema = ReviewSchema()
multi_review_schema = ReviewSchema(many=True)

class MovieSchema(ma.Schema):
    all_reviews = ma.Nested(multi_review_schema)
    class Meta:
        fields = ('id', 'title', 'genre', 'mpaa_rating', 'poster_img', 'all_reviews')

movie_schema = MovieSchema()
multi_movie_schema = MovieSchema(many=True)

# **** Add Movie EndPoint ****
@app.route('/movie/add', methods=["POST"])
def add_movie():
    if request.content_type != 'application/json':
        return jsonify('Error: Data must be sent as JSON')
    
    post_data = request.get_json()
    title = post_data.get('title')
    genre = post_data.get('genre')
    mpaa_rating = post_data.get('mpaa_rating')
    poster_img = post_data.get('poster_img')

    if title == None:
        return jsonify("Error: You must provide a movie title!")
    if genre == None:
        return jsonify("Error: You must provide a movie genre!")
    
    new_record = Movie(title, genre, mpaa_rating,poster_img)
    db.session.add(new_record)
    db.session.commit()

    return jsonify(movie_schema.dump(new_record))

# **** Get Movie EndPoint ****
@app.route('/movie/get', methods=["GET"])
def get_movies():
    all_movies = db.session.query(Movie).all()
    return jsonify(multi_movie_schema.dump(all_movies))

# **** Get A Movie EndPoint ****
@app.route('/movie/get/<id>', methods=["GET"])
def get_movie(id):
    get_movie = db.session.query(Movie).filter(Movie.id == id).first()
    return jsonify(movie_schema.dump(get_movie))

# **** Edit Movie EndPoint ****
@app.route('/movie/edit/<id>', methods=["PUT"])
def edit_movie_id(id):
    if request.content_type != 'application/json':
        return jsonify("Error: Data must be sent as JSON!")
    
    put_data = request.get_json()
    title = put_data.get('title')
    genre = put_data.get('genre')
    mpaa_rating = put_data.get('mpaa_rating')
    poster_img = put_data.get('poster_img')

    edit_movie_id = db.session.query(Movie).filter(Movie.id == id).first()

    if title != None:
        edit_movie_id.title = title
    if genre != None:
        edit_movie_id.genre = genre
    if mpaa_rating != None:
        edit_movie_id.mpaa_rating = mpaa_rating
    if poster_img != None:
        edit_movie_id.poster_img = poster_img

    db.session.commit()
    return jsonify(movie_schema.dump(edit_movie_id))


# **** Delete Movie EndPoint ****

@app.route('/movie/delete/<id>', methods=["DELETE"])
def delete_movie_id(id):
    delete_movie = db.session.query(Movie).filter(Movie.id == id).first()
    db.session.delete(delete_movie)
    db.session.commit()
    return jsonify("Your movie has been deleted!", movie_schema.dump(delete_movie))


#  **** Add Many Movies EndPoint ****
@app.route('/movie/add/many', methods=["POST"])
def add_many_movies():
    if request.content_type != "application/json":
        return jsonify("Error: Your Data must be sent as JSON")
    
    post_data = request.get_json()
    movies = post_data.get('movies')

    new_movies = []

    for movie in movies:
        title = movie.get('title')
        genre = movie.get('genre')
        mpaa_rating = movie.get('mpaa_rating')
        poster_img = movie.get('poster_img')

        existing_movie_check = db.session.query(Movie).filter(Movie.title == title).first()
        if existing_movie_check is None:
            new_record = Movie(title, genre, mpaa_rating,poster_img)
            db.session.add(new_record)
            db.session.commit()
            new_movies.append(movie_schema.dump(new_record))

    return jsonify(multi_movie_schema.dump(new_movies))

# **** Add Review EndPoint ****
@app.route('/review/add', methods=["POST"])
def add_review():
    if request.content_type != 'application/json':
        return jsonify("Error: Data must be submitted as JSON!")
    
    post_data = request.get_json()
    star_rating = post_data.get('star_rating')
    review_text = post_data.get('review_text')
    movie_id = post_data.get('movie_id')

    if star_rating == None:
        return jsonify("Error: You must enter a Star Rating for your Review")
    if movie_id == None:
        return jsonify("Error: That Movie entry does not exist!")
    
    new_review = Review(star_rating, review_text, movie_id)
    db.session.add(new_review)
    db.session.commit()

    return jsonify(review_schema.dump(new_review))




if __name__ == "__main__":
    app.run(debug = True)