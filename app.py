from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_super_secret_key'  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sunrise.db' 
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'index'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# database model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
# --- Add these new models alongside your User model ---
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    total_price = db.Column(db.Float, nullable=False)
    
    # Foreign key to link to the User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationship to link to OrderItems
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    
    # Foreign key to link to the Order
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)

#-- Create the database
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template("index.html")
@app.route('/about')
def about():
    return render_template("about.html")
@app.route('/ordering')    
def ordering():
    return render_template("ordering.html")
@app.route('/cart')
def cart():
    return render_template("cart.html") 

@app.route("/signup", methods=['POST'])
def signup():
    username = request.form.get('signup_username')
    email = request.form.get('signup_email')
    password = request.form.get('signup_password')

    # validation
    if not username or not email or not password:
        return jsonify({'status': 'error', 'message': 'All fields are required.'}), 400
    
    # Check if user already exists
    user_exists = User.query.filter_by(username=username).first()
    email_exists = User.query.filter_by(email=email).first()

    if user_exists:
        return jsonify({'status': 'error', 'message': 'Username already exists.'}), 409
    if email_exists:
        return jsonify({'status': 'error', 'message': 'Email already registered.'}), 409

    # Now it's safe to hash the password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, email=email, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    login_user(new_user) 
    return jsonify({'status': 'success', 'message': 'Account created successfully!'})

@app.route("/login", methods=['POST'])
def login():
    username = request.form.get('login_username')
    password = request.form.get('login_password')
    
    user = User.query.filter_by(username=username).first()

    # Check if user exists and password is correct
    if user and bcrypt.check_password_hash(user.password_hash, password):
        login_user(user)
        return jsonify({'status': 'success', 'message': 'Logged in successfully!'})
    
    return jsonify({'status': 'error', 'message': 'Invalid username or password.'}), 401

@app.route("/logout")
@login_required # This ensures only logged-in users can access this route
def logout():
    logout_user()
    return redirect(url_for('index'))
@app.route("/purchase", methods=['POST'])
@login_required # Ensures only logged-in users can purchase

def purchase():
    # Get the cart data sent from the JavaScript
    cart_data = request.get_json()

    if not cart_data:
        return jsonify({'status': 'error', 'message': 'Your cart is empty.'}), 400

    try:
        # Calculate total price
        total = sum(item.get('price', 0) for item in cart_data)

        # Create the main Order
        new_order = Order(user_id=current_user.id, total_price=total)
        db.session.add(new_order)
        
        db.session.flush() 

        #Create an OrderItem for each item in the cart
        for item in cart_data:
            order_item = OrderItem(
                item_name=item.get('name'),
                price=item.get('price'),
                order_id=new_order.id
            )
            db.session.add(order_item)

        # Commit all changes to the database
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': 'Purchase recorded successfully!'})

    except Exception as e:
        # rollback if any errors occur
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)