
import requests
import time
import random

# --- Configuration ---
BASE_URL = "http://127.0.0.1:8000"
ADMIN_USERNAME = "admin@example.com"
ADMIN_PASSWORD = "admin123"
BRANCH_ID = 1

# --- Helper Functions ---

def print_step(message):
    print(f"\n--- {message} ---")

def print_success(message):
    print(f"\033[92m[SUCCESS] {message}\033[0m")

def print_failure(message):
    print(f"\033[91m[FAILURE] {message}\033[0m")

def print_info(data):
    import json
    print(json.dumps(data, indent=2))

# --- Test Script ---

def run_test_flow():
    session = requests.Session()
    access_token = None
    product_id = None
    stock_lot_id = None

    try:
        # 1. Authenticate as Admin
        print_step("1. Authenticating as Admin")
        response = session.post(
            f"{BASE_URL}/auth/token",
            data={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
        )
        if response.status_code != 200:
            print_failure("Authentication failed.")
            print_info(response.json())
            return
        access_token = response.json()["access_token"]
        session.headers.update({"Authorization": f"Bearer {access_token}"})
        print_success("Authentication successful.")

        # 2. Create a New Product
        print_step("2. Creating a new product")
        product_sku = f"TEST-SKU-{int(time.time())}-{random.randint(100, 999)}"
        product_data = {
            "name": "Test Product E2E",
            "sku": product_sku,
            "description": "A product for end-to-end testing.",
            "branch_id": BRANCH_ID
        }
        response = session.post(f"{BASE_URL}/wms/products/", json=product_data)
        if response.status_code != 200:
            print_failure("Failed to create product.")
            print_info(response.json())
            return
        product_id = response.json()["id"]
        print_success(f"Product created with ID: {product_id} and SKU: {product_sku}")
        print_info(response.json())

        # 3. Create an Inbound Order (Receive Stock)
        print_step("3. Creating an inbound order (100 units PENDING)")
        inbound_data = {"product_id": product_id, "quantity": 100, "branch_id": BRANCH_ID}
        response = session.post(f"{BASE_URL}/wms/inbound/orders", json=inbound_data)
        if response.status_code != 200:
            print_failure("Failed to create inbound order.")
            print_info(response.json())
            return
        print_success("Inbound order created.")
        print_info(response.json())
        stock_lot_id = response.json()["generated_lots"][0]["id"]

        # 4. Verify Pending Stock
        print_step("4. Verifying product stock (should be 100 PENDING)")
        response = session.get(f"{BASE_URL}/wms/products/{product_id}")
        product_details = response.json()
        if product_details.get("quantity_pending") == 100 and product_details.get("quantity_available") == 0:
            print_success("Stock verification passed.")
            print_info({"quantity_available": product_details["quantity_available"], "quantity_pending": product_details["quantity_pending"]})
        else:
            print_failure("Stock verification failed.")
            print_info(product_details)
            return

        # 5. Approve Stock Lot via Quality Control
        print_step(f"5. Approving stock lot ID: {stock_lot_id}")
        quality_data = {"status": "AVAILABLE", "notes": "Approved via E2E test."}
        response = session.put(f"{BASE_URL}/api/quality/stock_lots/{stock_lot_id}", json=quality_data)
        if response.status_code != 200:
            print_failure("Failed to approve stock lot.")
            print_info(response.json())
            return
        print_success("Stock lot approved.")

        # 6. Verify Available Stock
        print_step("6. Verifying product stock (should be 100 AVAILABLE)")
        response = session.get(f"{BASE_URL}/wms/products/{product_id}")
        product_details = response.json()
        if product_details.get("quantity_available") == 100 and product_details.get("quantity_pending") == 0:
            print_success("Stock verification passed.")
            print_info({"quantity_available": product_details["quantity_available"], "quantity_pending": product_details["quantity_pending"]})
        else:
            print_failure("Stock verification failed.")
            print_info(product_details)
            return

        # 7. Create an Outbound Order (FIFO Picking)
        print_step("7. Creating an outbound order (30 units)")
        outbound_data = {"product_id": product_id, "quantity": 30, "branch_id": BRANCH_ID}
        response = session.post(f"{BASE_URL}/wms/outbound/orders", json=outbound_data)
        if response.status_code != 200:
            print_failure("Failed to create outbound order.")
            print_info(response.json())
            return
        print_success("Outbound order created.")

        # 8. Final Stock Verification
        print_step("8. Final stock verification (should be 70 AVAILABLE)")
        response = session.get(f"{BASE_URL}/wms/products/{product_id}")
        product_details = response.json()
        if product_details.get("quantity_available") == 70:
            print_success("Final stock verification passed.")
            print_info({"quantity_available": product_details["quantity_available"]})
        else:
            print_failure("Final stock verification failed.")
            print_info(product_details)
            return

        print_step("E2E Test Flow Completed Successfully!")

    except Exception as e:
        print_failure(f"An unexpected error occurred: {e}")
    finally:
        # Cleanup: Delete the product created during the test
        if product_id and access_token:
            print_step("9. Cleaning up created product")
            response = session.delete(f"{BASE_URL}/wms/products/{product_id}")
            if response.status_code == 204:
                print_success(f"Product ID {product_id} deleted.")
            else:
                # This might fail if stock lots still exist. We need to manually delete them first.
                print_failure("Could not delete product automatically.")
                print_info(response.json())


if __name__ == "__main__":
    run_test_flow()
