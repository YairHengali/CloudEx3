import requests
import pytest

@pytest.fixture(scope="module")
def base_url():
    return "http://localhost:8000"

def test_1_post_3_dishes(base_url):
    dish_names = ["orange", "spaghetti", "apple pie"]
    dish_ids = set()
    # status_codes = set()

    for dish in dish_names:
        response = requests.post(f"{base_url}/dishes", json={"name": dish})
        assert response.status_code == 201 #all got 201 code
        dish_id = int(response.text)
        dish_ids.add(dish_id)
        # status_codes.add(response.status_code)

    assert len(dish_ids) == len(dish_names)  # Unique IDs
    # assert len(status_codes) == 1 and 201 in status_codes  # All requests return 201 status code

########### #HOW TO GET THE ORANGE ID - IS IT A GOOD WAY?? (using a request to get it And not from the previous test)
def test_2_get_orange_by_id(base_url): 
        #HOW TO GET THE ORANGE ID - IS IT A GOOD WAY?? (using a request to get it And not from the previous test)
        get_orange_response = requests.get(f"{base_url}/dishes/orange")
        orange_id = get_orange_response.json().get("ID")

        response = requests.get(f"{base_url}/dishes/{orange_id}")
        assert response.status_code == 200 #the return status code from the request is 200
        orange_sodium = response.json().get("sodium")
        assert 0.9 < orange_sodium < 1.1 #the sodium field of the return JSON object is between .9 and 1.1
##########################################

def test_3_get_dishes(base_url):
        response = requests.get(f"{base_url}/dishes")
        assert response.status_code == 200 #the return status code from the GET request is 200
        dishes = response.json()
        assert len(dishes) == 3 #the returned JSON object has 3 embedded JSON objects (dishes)

def test_4_post_blah_dish(base_url):
        response = requests.post(f"{base_url}/dishes", json={"name": "blah"})
        assert response.status_code in [404, 400, 422] #the return code is 404 or 400 or 422
        assert int(response.text) == -3 #the return value is -3

def test_5_post_orange_dish(base_url):
        response = requests.post(f"{base_url}/dishes", json={"name": "orange"})
        assert response.status_code in [400, 404, 422] #the return code is 400 or 404 or 422
        assert int(response.text) == -2 #the return value is -2

def test_6_post_delicious_meal(base_url):
        #HOW TO GET THE IDs - IS IT A GOOD WAY?? (using a request to get it And not from the previous test)
        get_orange_response = requests.get(f"{base_url}/dishes/orange")
        orange_id = get_orange_response.json().get("ID")
        get_spaghetti_response = requests.get(f"{base_url}/dishes/spaghetti")
        spaghetti_id = get_spaghetti_response.json().get("ID")
        get_apple_pie_response = requests.get(f"{base_url}/dishes/apple pie")
        apple_pie_id = get_apple_pie_response.json().get("ID")

        response = requests.post(f"{base_url}/meals", json={"name": "delicious", "appetizer" : f"{orange_id}", "main" : f"{spaghetti_id}", "dessert" : f"{apple_pie_id}"})
        assert response.status_code == 201 #the return code is 201
        assert int(response.text) > 0 #the returned ID > 0

def test_7_get_meals(base_url):
        response = requests.get(f"{base_url}/meals")
        assert response.status_code == 200 #the return status code from the GET request is 200
        meals = response.json()
        assert len(meals) == 1 #the returned JSON object has 1 meal
        meal = list(meals.values())[0]
        meal_calories = meal["cal"]
        assert 400 < meal_calories < 500 #the calories of that meal is between 400 and 500

def test_8_post_meal_with_same_name(base_url):
        response = requests.post(f"{base_url}/meals", json={"name": "delicious", "appetizer" : 1, "main" : 1, "dessert" : 1})
        assert response.status_code in [400, 422] #the return status code from the request is 400 or 422
        assert int(response.text) == -2 #the code is -2 (same meal name as existing meal) 