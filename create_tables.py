from app.core.database import engine, Base

# Import all models here so that Base has them registered
from app.models import Product, Vendor, PurchaseOrder

def main():
    print("Creating database tables...")
    # The Product, Vendor, and PurchaseOrder models are now registered with Base
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

if __name__ == "__main__":
    main()
