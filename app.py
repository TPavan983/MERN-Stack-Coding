from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///transactions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    price = db.Column(db.Float, nullable=False)
    date_of_sale = db.Column(db.Date, nullable=False)
    sold = db.Column(db.Boolean, nullable=False)
    category = db.Column(db.String(100), nullable=False)

#app.before_first_request
def create_tables():
    db.create_all()
    seed_data()

def seed_data():
    response = requests.get('https://s3.amazonaws.com/roxiler.com/product_transaction.json')
    data = response.json()
    for item in data:
        date_of_sale = datetime.datetime.strptime(item['dateOfSale'], '%Y-%m-%d').date()
        transaction = Transaction(
            title=item['title'],
            description=item['description'],
            price=item['price'],
            date_of_sale=date_of_sale,
            sold=item['sold'],
            category=item['category']
        )
        db.session.add(transaction)
    db.session.commit()

@app.route('/transactions', methods=['GET'])
def list_transactions():
    month = request.args.get('month', type=str)
    search = request.args.get('search', type=str, default='')
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=10)

    query = Transaction.query.filter(db.extract('month', Transaction.date_of_sale) == datetime.datetime.strptime(month, '%B').month)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            db.or_(
                Transaction.title.ilike(search_pattern),
                Transaction.description.ilike(search_pattern),
                Transaction.price.ilike(search_pattern)
            )
        )

    transactions = query.paginate(page, per_page, False).items

    return jsonify([t.as_dict() for t in transactions])

@app.route('/statistics', methods=['GET'])
def statistics():
    month = request.args.get('month', type=str)

    total_sale_amount = db.session.query(db.func.sum(Transaction.price)).filter(
        db.extract('month', Transaction.date_of_sale) == datetime.datetime.strptime(month, '%B').month,
        Transaction.sold == True
    ).scalar() or 0

    total_sold_items = db.session.query(db.func.count(Transaction.id)).filter(
        db.extract('month', Transaction.date_of_sale) == datetime.datetime.strptime(month, '%B').month,
        Transaction.sold == True
    ).scalar()

    total_not_sold_items = db.session.query(db.func.count(Transaction.id)).filter(
        db.extract('month', Transaction.date_of_sale) == datetime.datetime.strptime(month, '%B').month,
        Transaction.sold == False
    ).scalar()

    return jsonify({
        'total_sale_amount': total_sale_amount,
        'total_sold_items': total_sold_items,
        'total_not_sold_items': total_not_sold_items
    })

@app.route('/bar-chart', methods=['GET'])
def bar_chart():
    month = request.args.get('month', type=str)

    price_ranges = [
        (0, 100), (101, 200), (201, 300), (301, 400), (401, 500),
        (501, 600), (601, 700), (701, 800), (801, 900), (901, float('inf'))
    ]

    result = {}
    for lower, upper in price_ranges:
        count = db.session.query(db.func.count(Transaction.id)).filter(
            db.extract('month', Transaction.date_of_sale) == datetime.datetime.strptime(month, '%B').month,
            Transaction.price >= lower,
            Transaction.price <= upper
        ).scalar()
        result[f'{lower}-{upper if upper != float("inf") else "above"}'] = count

    return jsonify(result)

@app.route('/pie-chart', methods=['GET'])
def pie_chart():
    month = request.args.get('month', type=str)

    categories = db.session.query(Transaction.category, db.func.count(Transaction.id)).filter(
        db.extract('month', Transaction.date_of_sale) == datetime.datetime.strptime(month, '%B').month
    ).group_by(Transaction.category).all()

    result = {category: count for category, count in categories}

    return jsonify(result)

@app.route('/combined', methods=['GET'])
def combined():
    month = request.args.get('month', type=str)

    transactions_response = list_transactions().get_json()
    statistics_response = statistics().get_json()
    bar_chart_response = bar_chart().get_json()
    pie_chart_response = pie_chart().get_json()

    combined_response = {
        'transactions': transactions_response,
        'statistics': statistics_response,
        'bar_chart': bar_chart_response,
        'pie_chart': pie_chart_response
    }

    return jsonify(combined_response)

if __name__ == '__main__':
    app.run(debug=True)
