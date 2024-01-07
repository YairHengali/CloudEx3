from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import requests
import json

API_KEY = "bzdh0a0GhXA9m2d/AaTdpQ==N5VwCq0xTbu9UEyq"
app = Flask(__name__)
api = Api(app)


class Dish_collection:
    def __init__(self):
        self.dish_counter = 0
        self.name_to_ID = {}
        self.dishes = {}

    def filering_dish_dict_from_API(self, dict_from_api, dish_id):
        filtered_dict = {}
        filtered_dict["name"] = dict_from_api["name"]
        filtered_dict["ID"] = dish_id
        filtered_dict["cal"] = dict_from_api["calories"]
        filtered_dict["size"] = dict_from_api["serving_size_g"]
        filtered_dict["sodium"] = dict_from_api["sodium_mg"]
        filtered_dict["sugar"] = dict_from_api["sugar_g"]
        return filtered_dict

    def union_two_dishes(self, list_from_api, dish_name):
        united_dict = {}
        united_dict["name"] = dish_name
        united_dict["calories"] = list_from_api[0]["calories"] + list_from_api[1]["calories"]
        united_dict["serving_size_g"] = list_from_api[0]["serving_size_g"] + list_from_api[1]["serving_size_g"]
        united_dict["sodium_mg"] = list_from_api[0]["sodium_mg"] + list_from_api[1]["sodium_mg"]
        united_dict["sugar_g"] = list_from_api[0]["sugar_g"] + list_from_api[1]["sugar_g"]
        return united_dict


    def add_dish(self, data_from_api, dish_name):
        self.dish_counter += 1
        list_from_response = json.loads(data_from_api.content)
        if len(list_from_response) == 1:
            dish_data = list_from_response[0]
        else: # len == 2
            dish_data = self.union_two_dishes(list_from_response, dish_name)
        self.dishes[self.dish_counter] = self.filering_dish_dict_from_API(dish_data, self.dish_counter)
        self.name_to_ID[dish_data["name"]] = self.dish_counter

    def remove_dish_by_id(self, dish_id):
        del self.name_to_ID[self.dishes[dish_id]["name"]] 
        del self.dishes[dish_id]

    def remove_dish_by_name(self, dish_name): #returns the dish's ID
        dish_id = self.name_to_ID[dish_name]
        del self.dishes[dish_id]
        del self.name_to_ID[dish_name]
        return dish_id


class Dishes(Resource):
    global dish_collection

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=False) 

        #Check that the request content-type is application/json
        if request.content_type != 'application/json':
            return 0, 415

        args = parser.parse_args()

        #Check if the 'name' parameter was specified
        if not args.get('name'):
            return -1, 400

        #Check if the dish of given name already exists
        if args['name'] in dish_collection.name_to_ID.keys():
            return -2, 400

        #Trying to get data from the API:
        dish_name = args['name']
        api_url = 'https://api.api-ninjas.com/v1/nutrition?query={}'.format(dish_name)
        api_response = requests.get(api_url, headers={'X-Api-Key': API_KEY})
        
        #API does not recognize this dish name
        if api_response.text == "[]":
            return -3, 400
        
        #API was not reachable or some other server error
        elif api_response.status_code != 200:
            return -4, 400
        else:
            dish_collection.add_dish(api_response, dish_name)
            return dish_collection.dish_counter , 201

    def get(self):
        return dish_collection.dishes, 200

    def delete(self):
        return -1, 400

class DishID(Resource):
    global dish_collection

    def get(self, id):
        #Checks if id is not exists
        if id not in dish_collection.dishes.keys():
            return -5, 404
        
        #Returns the dish with the specified ID:
        else:
            return dish_collection.dishes[id], 200
        
    def delete(self, id):
        #Checks if id is not exists
        if id not in dish_collection.dishes.keys():
            return -5, 404
        
        #Removes the dish and returns its ID:
        else:
            dish_collection.remove_dish_by_id(id)
            return id, 200

class DishName(Resource):
    def get(self, name):       
        #Checks if name is not exists
        if name not in dish_collection.name_to_ID.keys():
            return -5, 404
        
        #Returns the dish with the specified name:
        else:
            return dish_collection.dishes[dish_collection.name_to_ID[name]], 200
        

    def delete(self, name):
        #Checks if name is not exists
        if name not in dish_collection.name_to_ID.keys():
            return -5, 404

        #Removes the dish and returns its ID:
        else:
            return dish_collection.remove_dish_by_name(name), 200

##################################

class Meal_collection:
    global dish_collection

    def __init__(self):
        self.meal_counter = 0
        self.name_to_ID = {}
        self.meals = {}

    def add_meal(self, meal_name, appetizer, main, dessert):
        self.meal_counter += 1
        meal = {}
        meal["name"] = meal_name
        meal["ID"] = self.meal_counter
        meal["appetizer"] = appetizer
        meal["main"] = main
        meal["dessert"] = dessert
        meal["cal"] = dish_collection.dishes[appetizer]["cal"] + dish_collection.dishes[main]["cal"] + dish_collection.dishes[dessert]["cal"]
        meal["sodium"] = dish_collection.dishes[appetizer]["sodium"] + dish_collection.dishes[main]["sodium"] + dish_collection.dishes[dessert]["sodium"]
        meal["sugar"] = dish_collection.dishes[appetizer]["sugar"] + dish_collection.dishes[main]["sugar"] + dish_collection.dishes[dessert]["sugar"]
        
        self.meals[self.meal_counter] = meal
        self.name_to_ID[meal_name] = self.meal_counter

        return meal["ID"]
    
    def update_meal(self,meal_id, meal_name, appetizer, main, dessert):
        
        old_meal_name = self.meals[meal_id]["name"]
        self.name_to_ID.pop(old_meal_name)
        self.name_to_ID[meal_name] = meal_id

        self.meals[meal_id]["name"] = meal_name
        self.meals[meal_id]["appetizer"] = appetizer
        self.meals[meal_id]["main"] = main
        self.meals[meal_id]["dessert"] = dessert
        self.meals[meal_id]["cal"] = dish_collection.dishes[appetizer]["cal"] + dish_collection.dishes[main]["cal"] + dish_collection.dishes[dessert]["cal"]
        self.meals[meal_id]["sodium"] = dish_collection.dishes[appetizer]["sodium"] + dish_collection.dishes[main]["sodium"] + dish_collection.dishes[dessert]["sodium"]
        self.meals[meal_id]["sugar"] = dish_collection.dishes[appetizer]["sugar"] + dish_collection.dishes[main]["sugar"] + dish_collection.dishes[dessert]["sugar"]

        return id
        

    def remove_meal_by_id(self, meal_id):
        del self.name_to_ID[self.meals[meal_id]["name"]]
        del self.meals[meal_id]

    
    def remove_meal_by_name(self, meal_name): #returns the dish's ID
        meal_id = self.name_to_ID[meal_name]
        del self.meals[meal_id]
        del self.name_to_ID[meal_name]
        return meal_id


class Meals(Resource):
    global dish_collection
    global meal_collection

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=False) 
        parser.add_argument('appetizer', type=str, required=False) 
        parser.add_argument('main', type=str, required=False) 
        parser.add_argument('dessert', type=str, required=False) 

        #Check that the request content-type is application/json
        if request.content_type != 'application/json':
            return 0, 415

        args = parser.parse_args()

        #Check if the parameters were specified correctly
        if not args.get('name') or not args.get('appetizer') or not args.get('main') or not args.get('dessert'):
            return -1, 400

        #Check if the meal of given name already exists
        if args['name'] in meal_collection.name_to_ID.keys():
            return -2, 400

        #Check if one of the dish IDs does not exists
        if int(args['appetizer']) not in dish_collection.dishes.keys() or int(args['main']) not in dish_collection.dishes.keys() or int(args['dessert']) not in dish_collection.dishes.keys():
            return -5, 400

        else:
            meal_id = meal_collection.add_meal(args['name'], int(args['appetizer']), int(args['main']), int(args['dessert']))
            return meal_id , 201

    def get(self):
        return meal_collection.meals, 200
    
    def delete(self):
        return -1, 400

class MealID(Resource):
    def get(self, id):
        #Checks if id is not exists
        if id not in meal_collection.meals.keys():
            return -5, 404
        
        #Returns the meal with the specified ID:
        else:
            return meal_collection.meals[id], 200
        
    def delete(self, id):
        #Checks if id is not exists
        if id not in meal_collection.meals.keys():
            return -5, 404

        #Removes the meal and returns its ID:
        else:
            meal_collection.remove_meal_by_id(id)
            return id, 200
        

    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=False) 
        parser.add_argument('appetizer', type=str, required=False) 
        parser.add_argument('main', type=str, required=False) 
        parser.add_argument('dessert', type=str, required=False) 

        #Check that the request content-type is application/json
        if request.content_type != 'application/json':
            return 0, 415
        

        #Checks if id is not exists
        if id not in meal_collection.meals.keys():
            return -5, 404
        
        args = parser.parse_args()
    

        #Check if the parameters were specified correctly
        if not args.get('name') or not args.get('appetizer') or not args.get('main') or not args.get('dessert'):
            return -1, 400



        #Check if one of the dish IDs does not exists
        if int(args['appetizer']) not in dish_collection.dishes.keys() or int(args['main']) not in dish_collection.dishes.keys() or int(args['dessert']) not in dish_collection.dishes.keys():
            return -5, 400

        else:
            meal_collection.update_meal(id, args['name'], int(args['appetizer']), int(args['main']), int(args['dessert']))
            return id , 200
       
class MealName(Resource):
    def get(self, name):
        #Checks if name is not exists
        if name not in meal_collection.name_to_ID.keys():
            return -5, 404
        
        #Returns the meal with the specified name:
        else:
            return meal_collection.meals[meal_collection.name_to_ID[name]], 200
        
    def delete(self, name):
        #Checks if name is not exists
        if name not in meal_collection.name_to_ID.keys():
            return -5, 404

        #Removes the meal and returns its ID:
        else:
            return meal_collection.remove_meal_by_name(name), 200


dish_collection = Dish_collection()
meal_collection = Meal_collection()

api.add_resource(Dishes, '/dishes')
api.add_resource(DishID, '/dishes/<int:id>')
api.add_resource(DishName, '/dishes/<string:name>')
api.add_resource(Meals, '/meals')
api.add_resource(MealID, '/meals/<int:id>')
api.add_resource(MealName, '/meals/<string:name>')


if __name__ == '__main__':
    app.run('0.0.0.0', 8000)
