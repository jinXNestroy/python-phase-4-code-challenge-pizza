#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

class RestaurantListResource(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return jsonify([restaurant.to_dict() for restaurant in restaurants])
api.add_resource(RestaurantListResource, '/restaurants')

class RestaurantResource(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return make_response(jsonify({"error": "Restaurant not found"}), 404)
        return make_response(jsonify(restaurant.to_dict(include_pizzas = True)))
    
api.add_resource(RestaurantResource, '/restaurants/<int:id>')

class RestaurantDeleteResource(Resource):
    def delete(self, id):
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return jsonify({"error": "Restaurant not found"}), 404
        
        db.session.delete(restaurant)
        db.session.commit()
        return '',204
api.add_resource(RestaurantDeleteResource, '/restaurants/<int:id>')

class PizzaListResource(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return make_response(jsonify([pizza.to_dict() for pizza in pizzas]), 200)

api.add_resource(PizzaListResource, '/pizzas')

class RestaurantPizzaCreateResource(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_restaurant_pizza = RestaurantPizza(price = data['price'], pizza_id = data['pizza_id'], restaurant_id = data['restaurant_id'])
            db.session.add(new_restaurant_pizza)
            db.session.commit()
            return make_response(jsonify(new_restaurant_pizza.to_dict()), 201)
        except ValueError:
            return make_response(jsonify({"errors": ["validation errors"]}), 400)
        
api.add_resource(RestaurantPizzaCreateResource, '/restaurant_pizzas')
if __name__ == "__main__":
    app.run(port=5500, debug=True)
