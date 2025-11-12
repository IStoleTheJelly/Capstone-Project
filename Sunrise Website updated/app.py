from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import datetime
from functools import wraps # For the admin decorator

# --- App Initialization ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sunrise.db' 
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'index'

# --- Login Manager ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Database Models ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False) # Added admin flag
    orders = db.relationship('Order', backref='user', lazy=True)
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(100), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0) # Inventory tracking

    def __repr__(self):
        return f"Product('{self.name}', 'Stock: {self.stock}')"

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    total_price = db.Column(db.Float, nullable=False)
    
    # Foreign key to link to the User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Relationship to link to OrderItems
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    # Foreign key to link to the Order
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)

# --- Admin Decorator ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# --- Database & App Initialization ---
def init_database():
    """Creates database tables, seeds products, and creates admin user."""
    db.create_all()

    # Create Admin User if it doesn't exist
    admin_user = User.query.filter_by(username='sunrise_admin').first()
    if not admin_user:
        hashed_password = bcrypt.generate_password_hash('password').decode('utf-8')
        admin_user = User(
            username='sunrise_admin', 
            email='admin@sunrisecafe.com', 
            password_hash=hashed_password, 
            is_admin=True
        )
        db.session.add(admin_user)
    
    # Seed Products if the table is empty
    if Product.query.count() == 0:
        products = [
            Product(name="Croissant", description="Flaky, buttery pastry perfect for breakfast.", price=2.99, image_url="Images/croissant.jpg", stock=100),
            Product(name="Scone", description="Buttery scone with your choice of fruit.", price=3.49, image_url="Images/scone.jpeg", stock=100),
            Product(name="Bagel", description="Bagel, served with cream cheese.", price=2.49, image_url="Images/bagel.jpg", stock=100),
            Product(name="Blueberry Muffin", description="Sweet muffin loaded with fresh blueberries.", price=2.99, image_url="Images/blueberry.jpg", stock=100),
            Product(name="Apple Pie", description="Classic apple pie with a flaky crust.", price=4.99, image_url="Images/applepie.jpg", stock=50),
            Product(name="Yogurt Parfait", description="Layers of yogurt, granola, and berries.", price=3.99, image_url="Images/yogurt.png", stock=75),
            Product(name="Oatmeal", description="Warm oatmeal with brown sugar and fruit.", price=3.49, image_url="Images/oatmeal.jpg", stock=100),
            Product(name="Breakfast Sandwich", description="Egg, cheese, and bacon.", price=4.49, image_url="Images/BaconandEgg.jpg", stock=80),
            Product(name="Pancakes", description="Stack of pancakes with maple syrup.", price=4.29, image_url="Images/pancakes.jpg", stock=100),
            Product(name="Quiche", description="Egg and cheese quiche with spinach.", price=4.99, image_url="Images/quiche.jpg", stock=40),
            Product(name="French Toast", description="Golden-brown French toast with syrup.", price=4.29, image_url="Images/frenchtoast.jpg", stock=100),
            Product(name="Fruit Smoothie", description="Fresh fruit blended into a cool smoothie.", price=3.99, image_url="Images/smoothie.jpg", stock=100),
            Product(name="Fresh Brewed Coffee", description="Hot, aromatic coffee.", price=2.29, image_url="Images/coffee.jpg", stock=500),
            Product(name="Herbal Tea", description="Relaxing herbal tea blend, served hot.", price=2.49, image_url="Images/tea.jpg", stock=500),
            Product(name="Espresso", description="Rich, bold espresso shot.", price=2.99, image_url="Images/espresso.jpg", stock=500),
            Product(name="Chai Latte", description="Spiced chai tea with steamed milk.", price=3.29, image_url="Images/chai.jpg", stock=500)
        ]
        db.session.bulk_save_objects(products)
    
    db.session.commit()

# Create the database and admin/products on first run
with app.app_context():
    init_database()

# --- Main Routes ---
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/ordering')
def ordering():
    # Now fetches products dynamically from the database
    products = Product.query.order_by(Product.name).all()
    return render_template("ordering.html", products=products)

@app.route('/cart')
def cart():
    return render_template("cart.html") 

# --- Admin Routes ---
@app.route('/admin', methods=['GET'])
@admin_required
def admin():
    products = Product.query.order_by(Product.name).all()
    users = User.query.order_by(User.username).all()

    return render_template('admin.html', products=products, users=users)

@app.route('/admin/update_stock', methods=['POST'])
@admin_required
def update_stock():
    try:
        product_id = request.form.get('product_id')
        new_stock_str = request.form.get('new_stock')
        
        if not product_id or new_stock_str is None:
            return redirect(url_for('admin'))

        product = Product.query.get(product_id)
        new_stock = int(new_stock_str)

        if product and new_stock >= 0: # Prevent negative stock
            product.stock = new_stock
            db.session.commit()
    
    except Exception as e:
        db.session.rollback()
        
    return redirect(url_for('admin'))

# --- Auth Routes ---
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

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    # Admin flag is False by default
    new_user = User(username=username, email=email, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    login_user(new_user) 
    # Return username so frontend can update
    return jsonify({'status': 'success', 'message': 'Account created successfully!', 'username': new_user.username})

@app.route("/login", methods=['POST'])
def login():
    username = request.form.get('login_username')
    password = request.form.get('login_password')
    
    user = User.query.filter_by(username=username).first()

    if user and bcrypt.check_password_hash(user.password_hash, password):
        login_user(user)
        # Return username so frontend can update
        return jsonify({'status': 'success', 'message': 'Logged in successfully!', 'username': user.username})
    
    return jsonify({'status': 'error', 'message': 'Invalid username or password.'}), 401

@app.route("/logout")
@login_required 
def logout():
    logout_user()
    return redirect(url_for('index'))

# --- Guest Order History Route ---
@app.route('/history/guests')
@login_required
@admin_required
def guest_history():
    # Find all orders that have no user_id
    orders = Order.query.filter_by(user_id=None).order_by(Order.order_date.desc()).all()
    
    #Guest user representation
    class GuestUser:
        username = "(Guest Orders)"
        
    guest_user = GuestUser()

    # Re-use user_history.html template
    return render_template('user_history.html', user=guest_user, orders=orders)

# --- Purchase Route (With Inventory Logic) ---
@app.route("/purchase", methods=['POST'])

def purchase():

    cart_data = request.get_json()

    if not cart_data:
        return jsonify({'status': 'error', 'message': 'Your cart is empty.'}), 400

    try:
        # Group items by name to get quantities
        item_quantities = {}
        for item in cart_data:
            item_name = item.get('name')
            item_quantities[item_name] = item_quantities.get(item_name, 0) + 1
        
        # Check stock for all items BEFORE processing
        for name, quantity in item_quantities.items():
            product = Product.query.filter_by(name=name).first()
            if not product:
                return jsonify({'status': 'error', 'message': f'Sorry, {name} is no longer available.'}), 400
            elif product.stock < quantity:
                return jsonify({'status': 'error', 'message': f'Sorry, we only have {product.stock} of {name} in stock.'}), 400
        
        # Determine the user ID (guests will be None)
        user_id = None
        if current_user.is_authenticated:
            user_id = current_user.id

        # Create Order
        total = sum(item.get('price', 0) for item in cart_data)
        
        new_order = Order(user_id=user_id, total_price=total)
        db.session.add(new_order)
        db.session.flush()

        # Create OrderItems and NOW, decrement stock
        for name, quantity in item_quantities.items():
            product = Product.query.filter_by(name=name).first()
            
            product.stock -= quantity # Decrement stock

            order_item = OrderItem(
                item_name=name,
                price=product.price * quantity, # Total price for this line item
                quantity=quantity,
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

# --- purchase history for admins ---
@app.route('/history/<int:user_id>')
@login_required
@admin_required
def user_history(user_id):
    # Get the user
    user = User.query.get_or_404(user_id)
    
    # Get all orders for that user, most recent first
    # This works because your Order model has user_id
    orders = Order.query.filter_by(user_id=user.id).order_by(Order.order_date.desc()).all()
    
    # Pass the user and their orders to the new template
    return render_template('user_history.html', user=user, orders=orders)

# --- purchase history for users ---
@app.route('/my_history')
@login_required  
def my_history():
    # The user is the one currently logged in
    user = current_user
    
    # Find all orders for this specific user, most recent first
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.order_date.desc()).all()
    
    
    return render_template('user_history.html', user=user, orders=orders)

# --- Run the App ---
if __name__ == '__main__':
    app.run(debug=True)

