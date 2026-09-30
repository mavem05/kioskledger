import uuid
from sqlalchemy import Column, String, Float, ForeignKey, DateTime, Enum, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import enum
from database import Base

class TxType(str, enum.Enum):
    CASH = "CASH"
    CREDIT = "CREDIT"
    REPAYMENT = "REPAYMENT" # When someone pays back their debt

class Merchant(Base):
    __tablename__ = "merchants"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    business_name = Column(String(100), nullable=False)
    whatsapp_phone = Column(String(20), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Customer(Base):
    __tablename__ = "customers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id = Column(UUID(as_uuid=True), ForeignKey("merchants.id", ondelete="CASCADE"))
    full_name = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=True)
    total_debt = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id = Column(UUID(as_uuid=True), ForeignKey("merchants.id", ondelete="CASCADE"))
    item_name = Column(String(100), nullable=False)
    stock_qty = Column(Integer, default=0)
    unit_price = Column(Float, nullable=False)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id = Column(UUID(as_uuid=True), ForeignKey("merchants.id", ondelete="CASCADE"))
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="SET NULL"), nullable=True)
    items_summary = Column(JSON, nullable=False) # Stores the array of items sold
    total_amount = Column(Float, nullable=False)
    transaction_type = Column(Enum(TxType), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())