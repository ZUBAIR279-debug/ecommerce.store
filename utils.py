import os
import webbrowser
import urllib.parse
from flask import current_app
from fpdf import FPDF
from datetime import datetime

# ---------- PDF Generation ----------
class InvoicePDF(FPDF):
    def __init__(self, order, customer, items):
        super().__init__()
        self.order = order
        self.customer = customer
        self.items = items
        self.company_name = current_app.config.get('COMPANY_NAME', 'Bin Maqsood')
        self.company_email = current_app.config.get('COMPANY_EMAIL', 'binmaqsoodtextilefsd@gmail.com')
        self.company_address = current_app.config.get('COMPANY_ADDRESS', 'Factory Area, 38000, Pakistan')

    def header(self):
        self.set_font('Arial', 'B', 16)
        self.set_text_color(30, 30, 30)
        self.cell(0, 10, self.company_name, ln=1, align='C')
        self.set_font('Arial', '', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, self.company_email, ln=1, align='C')
        self.cell(0, 6, self.company_address, ln=1, align='C')
        self.ln(6)

        self.set_font('Arial', 'B', 14)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, 'INVOICE', ln=1, align='C')
        self.ln(4)

        self.set_font('Arial', '', 10)
        self.cell(50, 6, f"DATE: {self.order.created_at.strftime('%d-%b-%Y')}", ln=0)
        self.cell(0, 6, f"INVOICE NO: #BM-{self.order.id:04d}", ln=1, align='R')
        self.ln(6)

    def customer_details(self):
        self.set_font('Arial', 'B', 11)
        self.cell(80, 8, 'BILL TO', ln=0)
        self.cell(0, 8, 'SHIP TO', ln=1, align='R')
        self.set_font('Arial', '', 10)
        self.cell(80, 6, self.customer.name, ln=0)
        self.cell(0, 6, self.customer.name, ln=1, align='R')
        self.cell(80, 6, self.customer.address or '', ln=0)
        self.cell(0, 6, self.customer.address or '', ln=1, align='R')
        self.cell(80, 6, f"Phone: {self.customer.whatsapp_number}", ln=0)
        self.cell(0, 6, f"Phone: {self.customer.whatsapp_number}", ln=1, align='R')
        self.ln(6)

    def items_table(self):
        self.set_font('Arial', 'B', 10)
        self.set_fill_color(230, 230, 230)
        self.cell(80, 8, 'DESCRIPTION', border=1, fill=True)
        self.cell(30, 8, 'QTY', border=1, fill=True, align='C')
        self.cell(40, 8, 'UNIT PRICE', border=1, fill=True, align='R')
        self.cell(40, 8, 'TOTAL', border=1, fill=True, align='R')
        self.ln()

        self.set_font('Arial', '', 10)
        for item in self.items:
            product = item.product
            price_float = float(item.price)
            self.cell(80, 8, product.title[:40], border=1)
            self.cell(30, 8, str(item.quantity), border=1, align='C')
            self.cell(40, 8, f"Rs. {price_float:.2f}", border=1, align='R')
            self.cell(40, 8, f"Rs. {price_float * item.quantity:.2f}", border=1, align='R')
            self.ln()
        self.ln(4)

    def totals_and_payment(self):
        subtotal = sum(float(item.price) * item.quantity for item in self.items)
        discount = 0
        tax = 0
        shipping = 0
        total = subtotal - discount + tax + shipping

        self.set_font('Arial', '', 10)
        self.cell(150, 8, 'SUBTOTAL', ln=0, align='R')
        self.cell(40, 8, f"Rs. {subtotal:.2f}", ln=1, align='R')
        
        self.set_font('Arial', 'B', 11)
        self.cell(150, 10, 'Balance Due', ln=0, align='R')
        self.cell(40, 10, f"Rs. {total:.2f}", ln=1, align='R')

        self.ln(6)
        self.set_font('Arial', '', 10)
        self.cell(0, 8, f"Payment Method: {self.order.payment_method}", ln=1)
        self.cell(0, 8, f"Order Status: {self.order.order_status}", ln=1)

    def footer(self):
        self.set_y(-20)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Thank you for shopping with {self.company_name}", align='C')

    def generate(self):
        self.add_page()
        self.customer_details()
        self.items_table()
        self.totals_and_payment()
        res = self.output(dest='S')
        if isinstance(res, str):
            return res.encode('latin1')
        return bytes(res)

def generate_invoice_pdf(order, customer, items):
    pdf = InvoicePDF(order, customer, items)
    return pdf.generate()

def save_invoice_pdf(order, customer, items):
    pdf_bytes = generate_invoice_pdf(order, customer, items)
    temp_dir = current_app.config.get('INVOICE_FOLDER', 'invoices')
    os.makedirs(temp_dir, exist_ok=True)
    filename = f"invoice_order_{order.id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.pdf"
    filepath = os.path.join(temp_dir, filename)
    with open(filepath, 'wb') as f:
        f.write(pdf_bytes)
    return filepath

# ---------- WHATSAPP DEEP LINK (FREE, NO API) ----------
def send_whatsapp_message(phone_number, message_text, pdf_path=None):
    clean_phone = phone_number.replace("+", "").replace(" ", "").replace("-", "").strip()
    if clean_phone.startswith("0"):
        clean_phone = "92" + clean_phone[1:]
    encoded_msg = urllib.parse.quote(message_text)
    url = f"https://wa.me/{clean_phone}?text={encoded_msg}"
    webbrowser.open(url)
    print(f"✅ WhatsApp opened for {phone_number}")
    return True

# ---------- NOTIFICATIONS ----------
def notify_owner_and_customer(order, customer, items, pdf_path):
    owner_number = current_app.config.get('WHATSAPP_OWNER_NUMBER', '+923080320007')

    owner_msg = (
        f"🛍️ *New Order Received!*\n\n"
        f"📋 Order ID: #BM-{order.id:04d}\n"
        f"👤 Customer: {customer.name}\n"
        f"📞 Phone: {customer.whatsapp_number}\n"
        f"📍 Address: {customer.address}\n"
        f"🏙️ City: {customer.city}\n"
        f"💳 Payment: {order.payment_method}\n"
        f"💰 Total: Rs. {float(order.total_amount):.2f}\n\n"
        f"📦 Items:\n"
    )
    for item in items:
        product = item.product
        owner_msg += f"  • {product.title} x {item.quantity} = Rs. {float(item.price) * item.quantity:.2f}\n"
    
    owner_msg += f"\n✅ Please confirm the order and arrange delivery."

    # Sirf owner ko bhejo (customer ko nahi)
    send_whatsapp_message(owner_number, owner_msg)

def send_status_update(order, new_status):
    customer = order.customer
    if new_status == 'Shipped':
        msg = f"🚚 Dear {customer.name},\n\nYour order #BM-{order.id:04d} has been *shipped*!\nYou will receive it soon.\n\nThank you for shopping with Bin Maqsood."
    elif new_status == 'Delivered':
        msg = f"🎉 Dear {customer.name},\n\nYour order #BM-{order.id:04d} has been *delivered*!\nWe hope you love it!\nPlease rate us on our website."
    else:
        msg = f"📋 Dear {customer.name},\n\nYour order #BM-{order.id:04d} status is now: *{new_status}*."
    
    send_whatsapp_message(customer.whatsapp_number, msg)