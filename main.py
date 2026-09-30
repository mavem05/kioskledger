import os
import json
import httpx
from fastapi import FastAPI, Request, Depends
from dotenv import load_dotenv
from sqlalchemy.orm import Session

# Import AI engine
from ai_engine import route_and_process

# Import Database configurations
from database import SessionLocal, engine
import models

# Automatically create tables in Supabase if they don't exist yet
models.Base.metadata.create_all(bind=engine)

load_dotenv()

app = FastAPI()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Telegram Outbound Messenger
def send_telegram_receipt(chat_id: str, text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        httpx.post(url, json=payload)
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

# Database session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    return {"status": "KioskLedger API is running on Telegram!"}

# Inbound Message Processing Endpoint for Telegram
@app.post("/webhook")
async def receive_message(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    
    try:
        # Telegram webhook parsing
        if "message" in body and "text" in body["message"]:
            message_data = body["message"]
            
            # Telegram uses 'chat' ID instead of phone numbers for routing
            sender_id = str(message_data["chat"]["id"])
            raw_text = message_data["text"]
            
            print(f"\n--- NEW TELEGRAM MESSAGE FROM {sender_id} ---")
            print(f"Message content: {raw_text}")
            
            # Step A: Get or Create Merchant by Telegram ID
            merchant = db.query(models.Merchant).filter(
                models.Merchant.whatsapp_phone == sender_id
            ).first()
            
            if not merchant:
                merchant = models.Merchant(
                    whatsapp_phone=sender_id, # Reusing whatsapp_phone column for Telegram ID
                    business_name="My Kiosk"
                )
                db.add(merchant)
                db.commit()
                db.refresh(merchant)

            # Step B: Route to AI Engine for Extraction
            structured_data = route_and_process("text", raw_text)
            
            # SAFETY NET: If AI fails, tell the user and stop processing gracefully
            if not structured_data:
                send_telegram_receipt(sender_id, "❌ AI failed to read that. Try again.")
                return {"status": "error"}
            
            customer_name = structured_data.get("customer_name")
            customer_id = None
            customer = None
            # Step C: Handle Customer Record for Credit/Repayment
            if customer_name:
                customer = db.query(models.Customer).filter(
                    models.Customer.merchant_id == merchant.id,
                    models.Customer.full_name.ilike(customer_name)
                ).first()
                
                if not customer:
                    customer = models.Customer(
                        merchant_id=merchant.id,
                        full_name=customer_name,
                        total_debt=0.0
                    )
                    db.add(customer)
                    db.commit()
                    db.refresh(customer)
                
                customer_id = customer.id
                
                # Update customer debt ledger
                if tx_type == "CREDIT":
                    customer.total_debt += total_amount
                elif tx_type in ["REPAYMENT", "PAYMENT"]:
                    customer.total_debt = max(0.0, customer.total_debt - total_amount)
                
                db.commit()
                db.refresh(customer)

            # Step D: Save Transaction to Supabase
            new_tx = models.Transaction(
                merchant_id=merchant.id,
                customer_id=customer_id,
                items_summary=structured_data.get("items_summary", []),
                total_amount=total_amount,
                transaction_type=tx_type
            )
            db.add(new_tx)
            db.commit()
            print("💾 Transaction successfully saved to Supabase!")

            # Step E: Send Telegram Confirmation Receipt
            if customer and customer_id:
                receipt_text = f"✅ Saved!\n{customer.full_name}'s updated balance is #{customer.total_debt:,.2f}"
            else:
                receipt_text = f"✅ Cash transaction of #{total_amount:,.2f} recorded!"
            
            send_telegram_receipt(sender_id, receipt_text)
            print("---------------------------------------\n")

    except Exception as e:
        print(f"Error processing webhook: {e}")

    # Telegram expects a standard 200 OK status to confirm receipt
    return {"status": "ok"}