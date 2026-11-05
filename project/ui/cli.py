from application.sale_service import SaleService
from application.return_service import ReturnService
from infrastructure.repositories import (
    InMemoryProductRepository,
    InMemorySaleRepository,
    InMemoryReturnRepository,
)


class POSApp:
    def __init__(self):
        self.product_repo = InMemoryProductRepository()
        self.sale_repo = InMemorySaleRepository()
        self.return_repo = InMemoryReturnRepository()
        self.sale_service = SaleService(self.product_repo, self.sale_repo)
        self.return_service = ReturnService(
            self.product_repo, self.sale_repo, self.return_repo)

    def run(self):
        while True:
            print("\n" + "=" * 46)
            print("        Mini-Mart POS System")
            print("=" * 46)
            print("1. Process Sale")
            print("2. Handle Returns")
            print("3. View Products & Stock")
            print("0. Exit")
            choice = input("Select an option: ").strip()
            if choice == "1":
                self.process_sale()
            elif choice == "2":
                self.handle_return()
            elif choice == "3":
                self.show_products()
            elif choice == "0":
                print("Goodbye!")
                break
            else:
                print("Invalid option, please try again.")

    def show_products(self):
        print("\n--- Product Catalogue ---")
        print(f"{'ID':<8}{'Name':<32}{'Price':<10}{'Stock':<6}")
        for p in self.product_repo.all():
            print(f"{p.product_id:<8}{p.name:<32}{str(p.price):<10}{p.stock:<6}")

    # ---------- Process Sale ----------
    def process_sale(self):
        print("\n--- New Sale ---")
        sale = self.sale_service.start_sale()
        print(f"Sale ID: {sale.sale_id}")
        print("Enter a Product ID and quantity (type 'done' to check out).")

        while True:
            raw = input("Product ID (or 'done' to check out): ").strip()
            if raw.lower() == "done":
                break
            if not raw:
                continue
            try:
                qty_raw = input("Quantity (default 1): ").strip()
                qty = int(qty_raw) if qty_raw else 1
                self.sale_service.scan_item(raw, qty)

                s = self.sale_service.current_sale
                print(f"  Running total: {s.total}")
                for item in s.items:
                    print(f"    {item.name} x{item.quantity}  {item.subtotal}")
            except Exception as e:
                print(f"  Error: {e}")

        cur = self.sale_service.current_sale
        if not cur or not cur.items:
            print("Cart is empty - sale cancelled.")
            self.sale_service.cancel_sale()
            return

        print(f"\nAmount due: {cur.total}")
        try:
            tendered = float(input("Cash tendered: ").strip())
            sale = self.sale_service.make_payment(tendered)
            self.print_receipt(sale)
        except Exception as e:
            print(f"Payment failed: {e}")
            self.sale_service.cancel_sale()

    def print_receipt(self, sale):
        print("\n" + "-" * 40)
        print("                RECEIPT")
        print("-" * 40)
        print(f"Sale ID : {sale.sale_id}")
        print(f"Time    : {sale.created_at:%Y-%m-%d %H:%M:%S}")
        print("-" * 40)
        for item in sale.items:
            print(f"{item.name} x{item.quantity}  {item.subtotal}")
        print("-" * 40)
        print(f"Total    : {sale.total}")
        print(f"Tendered : {sale.payment.tendered}")
        print(f"Change   : {sale.change}")
        print("-" * 40)
        print("Thank you for shopping with us!\n")

    # ---------- Handle Returns ----------
    def handle_return(self):
        print("\n--- Handle Returns ---")
        sale_id = input("Enter the original Sale ID: ").strip()
        try:
            record = self.return_service.start_return(sale_id)
        except Exception as e:
            print(f"Error: {e}")
            return

        print(f"Return ID: {record.return_id}")
        print("Enter the Product ID and quantity to return "
              "(type 'done' to confirm).")
        while True:
            raw = input("Product ID (or 'done' to confirm): ").strip()
            if raw.lower() == "done":
                break
            if not raw:
                continue
            try:
                qty_raw = input("Return quantity (default 1): ").strip()
                qty = int(qty_raw) if qty_raw else 1
                self.return_service.add_item(raw, qty)
                r = self.return_service.current_return
                print(f"  Added to return. Refund total: {r.total_refund}")
            except Exception as e:
                print(f"  Error: {e}")

        cur = self.return_service.current_return
        if not cur or not cur.items:
            print("No items selected - return cancelled.")
            self.return_service.cancel_return()
            return

        try:
            record = self.return_service.confirm()
            print(f"\nReturn completed. Refund amount: {record.total_refund}")
            print("Stock has been updated.")
        except Exception as e:
            print(f"Confirmation failed: {e}")