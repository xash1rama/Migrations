from random import randint, choice
from flask import Flask, request, jsonify
from models import session, Base, engine, User, Coffee
from sqlalchemy import cast, String,func, select, text, any_
from itertools import chain
import requests
import json

app = Flask(__name__)

@app.before_first_request
def before_first_request_func():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    response_200 = 0
    names = ["Bob", "Stiffler", "Frank", "Big Smoke", "50 cent", "Lil peep", "Loo", "Pipsklick", "Joe", "Bart"]
    while response_200 != 10:
        response = requests.get("https://random-data-api.com/api/coffee/random_coffee")
        if response.status_code == 200:
            response_json = json.loads(response.text)
            title, origin = response_json["blend_name"], response_json["origin"]
            intensifier, notes = response_json["intensifier"], [response_json["notes"].split(", ")]
            coffee = Coffee(title=title,
                            origin=origin,
                            intensifier=intensifier,
                            notes=notes)

            response_200 += 1
            session.add(coffee)
    session.commit()
    while response_200 != 0:
        new_user = User()
        response = requests.get("https://random-data-api.com/api/address/random_address", timeout=10)
        if response.status_code == 200:
            response_json = json.loads(response.text)
            address = {"country": response_json["country"],
                "city": response_json["city"],
                "street_name": response_json["street_name"],
                "street_address": response_json["street_address"]}
            user = User(name=choice(names),
                        address=address,
                        coffee_id=randint(1, 10),
                        has_sale=choice([True, False]))
            response_200 -= 1
            session.add(user)
    session.commit()

@app.route("/")
def get_all():
    coffeess = session.query(Coffee).all()
    users = session.query(User).all()
    res_user = [us.to_json() for us in users]
    res_coffee = [cof.to_json() for cof in coffeess]
    return jsonify(coffees=res_coffee, users=res_user)


@app.route('/add_user', methods=["POST"])
def add_user():
    res_name = request.json.get("name")
    new_user = User()
    if not res_name:
        return "Not found 'name' for user"
    if request.json.get("name"):
        new_user.name = res_name
    if request.json.get("has_sale"):
        new_user.has_sale = request.json.get("has_sale")
    if request.json.get("address"):
        new_user.address = request.json.get("address")
    if request.json.get("coffee_id"):
        new_user.coffee_id = request.json.get("coffee_id")
    session.add(new_user)
    session.commit()
    coffee = session.query(Coffee).filter(Coffee.id==request.json.get("coffee_id"))

    return f"User {res_name} likes coffee: {coffee[0]}"

@app.route("/search_coffee",  methods=["POST"])
def search_coffee():
    title = request.json.get("title")
    if not title:
        return "Coffee's title not found"
    results = session.query(Coffee).filter(Coffee.title.ilike(f'%{title}%')).all()
    res = [cof.to_json() for cof in results]
    return jsonify(coffees=res)

@app.route("/get_notes", methods=["GET"])
def get_unique_notes():
    res = session.query(Coffee.notes).distinct().all()
    notes_list = list(chain.from_iterable(note[0] for note in res))
    unique_notes = list({tuple(note) for note in notes_list}) if notes_list else []
    res = []
    for i in unique_notes:
        res.extend(i)
    return jsonify(unique_notes=sorted(res, key=lambda x:len(x)))


@app.route("/search_country", methods=["POST"])
def search_county():
    country_name = request.json.get("country")
    if not country_name:
        return "Response not found"
    stmt = select(User).where(text(f"address ->> 'country' SIMILAR TO '{country_name}'"))
    results = session.execute(stmt).scalars().all()
    if results:
        names = [name.to_json() for name in results]
        return jsonify(users_from_county=names)
    return f"Country: {country_name} - not found"




if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)