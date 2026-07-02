from app import app, db
from models import Product

products_data = [
    {"id":1, "title":"Embroidered Lawn Suit", "price":4990, "category":"Women", "stock":20, "image_path":"uploads/1.png"},
    {"id":2, "title":"Chiffon Embellished", "price":6590, "category":"Women", "stock":15, "image_path":"uploads/2.png"},
    {"id":3, "title":"Organza Festive", "price":7890, "category":"Women", "stock":10, "image_path":"uploads/3.png"},
    {"id":4, "title":"Silk Luxury Pret", "price":9290, "category":"Women", "stock":8, "image_path":"uploads/4.png"},
    {"id":5, "title":"Summer Lawn", "price":3990, "category":"Women", "stock":20, "image_path":"uploads/1.png"},
    {"id":6, "title":"Embroidered Chiffon", "price":5490, "category":"Women", "stock":15, "image_path":"uploads/2.png"},
    {"id":7, "title":"Cotton Silk", "price":4290, "category":"Women", "stock":10, "image_path":"uploads/3.png"},
    {"id":8, "title":"Breezy Organza", "price":5990, "category":"Women", "stock":12, "image_path":"uploads/4.png"},
    {"id":9, "title":"Wool Blend", "price":8990, "category":"Women", "stock":8, "image_path":"uploads/2.png"},
    {"id":10, "title":"Pashmina Luxe", "price":12990, "category":"Women", "stock":5, "image_path":"uploads/3.png"},
    {"id":11, "title":"Cashmere Shrug", "price":7490, "category":"Women", "stock":6, "image_path":"uploads/1.png"},
    {"id":12, "title":"Tweed Jacket", "price":9990, "category":"Women", "stock":4, "image_path":"uploads/4.png"},
    {"id":13, "title":"Silk Embellished", "price":10990, "category":"Women", "stock":7, "image_path":"uploads/4.png"},
    {"id":14, "title":"Digital Print", "price":6590, "category":"Women", "stock":10, "image_path":"uploads/1.png"},
    {"id":15, "title":"Handwoven", "price":8490, "category":"Women", "stock":9, "image_path":"uploads/2.png"},
    {"id":16, "title":"Festive Edit", "price":11990, "category":"Women", "stock":5, "image_path":"uploads/3.png"}
]

with app.app_context():
    for data in products_data:
        product = Product.query.get(data["id"])
        if product:
            product.title = data["title"]
            product.price = data["price"]
            product.category = data["category"]
            product.stock = data["stock"]
            product.image_path = data["image_path"]
        else:
            product = Product(**data)
            db.session.add(product)
    db.session.commit()
    print("✅ All products (1–16) inserted/updated!")