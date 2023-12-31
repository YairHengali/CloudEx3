import requests

def query_resolver():
  with open("query.txt", "r") as file:
    for dish_name in file:
      dish_name = dish_name.strip()
      post_response = requests.post(f"http://localhost:8000/dishes", json={"name": dish_name})
      if post_response.status_code == 201:
        get_response = requests.get(f"http://localhost:8000/dishes/{dish_name}")
        calories = get_response.json().get("cal")
        sodium = get_response.json().get("sodium")
        sugar = get_response.json().get("sugar")
        print(f"{dish_name} contains {calories} calories, {sodium} mgs of sodium, and {sugar} grams of sugar")
      else:
        print("ERROR")

