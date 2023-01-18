from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

import random
app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def get_dict(self):
        dic={}
        for column in self.__table__.columns:
            dic[column.name] = getattr(self,column.name)
        return dic

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/random")
def random_cafe():
    allcafes = db.session.query(Cafe).all()
    random_cafe = random.choice(allcafes)
    return jsonify(cafe={
        "can_take_calls": random_cafe.can_take_calls,
        "coffee_price": random_cafe.coffee_price,
        "has_sockets": random_cafe.has_sockets,
        "has_toilets": random_cafe.has_toilet,
        "has_wifi": random_cafe.has_wifi,
        "id": random_cafe.id,
        "img_url": random_cafe.img_url,
        "location": random_cafe.location,
        "map_url": random_cafe.map_url,
        "name": random_cafe.name,
        "seats": random_cafe.seats,
    })


## HTTP GET - Read Record
@app.route("/all")
def get_cafe():
    allcafes=db.session.query(Cafe).all()
    return jsonify(cafes=[cafe.get_dict() for cafe in allcafes])

@app.route("/search")
def search():
    locate = request.args.get("loc")
    allcafe = db.session.query(Cafe).filter_by(location=locate).all()
    if allcafe:
        return jsonify(cafe=[cafe.get_dict() for cafe in allcafe])
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})


## HTTP POST - Create Record
@app.route("/add", methods=['POST'])
def add():
    newCafe=Cafe(
        name = request.form.get('name'),
        map_url = request.form.get('map_url'),
        img_url = request.form.get('img_url'),
        location = request.form.get('loc'),
        seats = request.form.get('seat'),
        has_toilet = bool(request.form.get('toilet')),
        has_wifi = bool(request.form.get('wifi')),
        has_sockets = bool(request.form.get('sockets')),
        can_take_calls = bool(request.form.get('calls')),
        coffee_price = request.form.get('coffee_prices')
    )
    db.session.add(newCafe)
    db.session.commit()
    return jsonify(response={"success": "successfully added new cafe"})
## HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:cafe_id>", methods=['PATCH'])
def update_price(cafe_id):
    newPrice=request.args.get('new_price')
    cafe=db.session.query(Cafe).get(cafe_id)
    if cafe:
        cafe.coffee_price=newPrice
        db.session.commit()
        return jsonify(response={"success": "successfully updated coffee price"})
    else:
        return jsonify(error={"Not found": "Sorry a cafe with that id was not found in the database."})

## HTTP DELETE - Delete Record
@app.route("/report-closed/<int:cafe_id>",methods=['DELETE'])
def delete(cafe_id):
    user_api=request.args.get('secret_api')
    if user_api=='1234567890':
        if db.session.query(Cafe).filter_by(id=cafe_id):
            db.session.query(Cafe).filter_by(id=cafe_id).delete()
            db.session.commit()
            return jsonify(response={"success": "Cafe closed successsfully"})
        else:
            return jsonify(error={"Not found": "Sorry a cafe with that id was not found in the database."})
    else:
        return jsonify(error={"Error": "Sorry you rae not authorised to delete a cafe."})
if __name__ == '__main__':
    app.run(debug=True)
