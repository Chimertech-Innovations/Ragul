import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Farm(Base):
    __tablename__ = "farms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), default="GreenPastures Dairy Farm")
    owner_name = Column(String(100), default="Ragul Farmer")
    location = Column(String(100), default="Coimbatore, Tamil Nadu")
    total_cows = Column(Integer, default=50)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Cattle(Base):
    __tablename__ = "cattle"
    
    id = Column(Integer, primary_key=True, index=True) # cow_id (e.g. 37)
    tag_number = Column(String(50), unique=True, index=True)
    name = Column(String(50), nullable=True)
    breed = Column(String(50), default="Holstein Friesian Cross")
    age_years = Column(Float, default=4.2)
    lactation_stage = Column(String(50), default="Mid Lactation")
    parity = Column(Integer, default=2) # 2nd calving
    daily_average_milk = Column(Float, default=16.0)
    health_status = Column(String(50), default="Healthy") # "Healthy", "Under Observation", "High Risk"
    mastitis_risk = Column(String(20), default="Low") # "Low", "Moderate", "High"
    affected_quarter = Column(String(50), nullable=True) # "Left Rear", etc.
    in_estrus = Column(Boolean, default=False)
    days_in_milk = Column(Integer, default=120)
    
    milk_readings = relationship("MilkReading", back_populates="cow", cascade="all, delete-orphan")
    health_events = relationship("HealthEvent", back_populates="cow", cascade="all, delete-orphan")
    feed_records = relationship("FeedRecord", back_populates="cow", cascade="all, delete-orphan")

class MilkReading(Base):
    __tablename__ = "milk_readings"
    
    id = Column(Integer, primary_key=True, index=True)
    cow_id = Column(Integer, ForeignKey("cattle.id"))
    session = Column(String(20), default="Morning") # "Morning", "Evening"
    yield_litres = Column(Float, nullable=False)
    fat_percentage = Column(Float, default=4.1)
    snf_percentage = Column(Float, default=8.5)
    somatic_cell_count = Column(Integer, default=150000) # SCC (indicator for mastitis)
    recorded_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    cow = relationship("Cattle", back_populates="milk_readings")

class HealthEvent(Base):
    __tablename__ = "health_events"
    
    id = Column(Integer, primary_key=True, index=True)
    cow_id = Column(Integer, ForeignKey("cattle.id"))
    event_type = Column(String(50), nullable=False) # "Mastitis Risk", "Estrus", "Lameness", "Fever", "Vaccination"
    severity = Column(String(20), default="Moderate") # "Low", "Moderate", "High", "Critical"
    affected_quarter = Column(String(50), nullable=True)
    description = Column(Text, nullable=False)
    recommended_action = Column(Text, nullable=True)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    cow = relationship("Cattle", back_populates="health_events")

class FeedRecord(Base):
    __tablename__ = "feed_records"
    
    id = Column(Integer, primary_key=True, index=True)
    cow_id = Column(Integer, ForeignKey("cattle.id"))
    intake_kg = Column(Float, nullable=False)
    target_kg = Column(Float, default=20.0)
    feed_type = Column(String(100), default="Silage + Green Fodder + Dairy Concentrate")
    water_intake_litres = Column(Float, default=75.0)
    recorded_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    cow = relationship("Cattle", back_populates="feed_records")

class FarmTask(Base):
    __tablename__ = "farm_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    cow_id = Column(Integer, nullable=True)
    title = Column(String(200), nullable=False)
    priority = Column(String(20), default="Normal") # "Low", "Normal", "High", "Urgent"
    status = Column(String(20), default="Pending") # "Pending", "Completed"
    assigned_to = Column(String(100), default="Ragul")
    due_date = Column(DateTime, default=datetime.datetime.utcnow)

class FarmWorker(Base):
    __tablename__ = "farm_workers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    role = Column(String(100), default="Milker") # "Head Herdsman", "Senior Milker", "Feed & Silage Operator", "Vet Assistant"
    phone = Column(String(20), default="+91 98421 00000")
    shift = Column(String(50), default="05:00 AM - 01:00 PM (Morning Shift)")
    status = Column(String(30), default="Active") # "Active", "On Duty", "On Leave"
    duties = Column(String(200), default="Milking, teat dipping, and bulk cooler sanitation")

class MonthlyMetric(Base):
    __tablename__ = "monthly_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    month_year = Column(String(50), nullable=False) # e.g. "Last Month (September 2026)"
    total_milk_produced_litres = Column(Float, default=21850.0)
    avg_daily_yield_litres = Column(Float, default=728.3)
    total_feed_consumed_kg = Column(Float, default=28500.0)
    total_revenue_inr = Column(Float, default=764750.0)
    veterinary_expenses_inr = Column(Float, default=18400.0)
    lactating_cows_count = Column(Integer, default=46)
    ai_inseminations_performed = Column(Integer, default=6)
    calves_born = Column(Integer, default=3)

class ConversationSession(Base):
    __tablename__ = "conversation_sessions"
    
    id = Column(String(100), primary_key=True)
    user_id = Column(String(100), default="farmer_1")
    farm_id = Column(Integer, default=1)
    language_preference = Column(String(20), default="tanglish") # "tanglish", "tamil", "hindi", "english"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), ForeignKey("conversation_sessions.id"))
    role = Column(String(20), nullable=False) # "user", "assistant", "system", "tool"
    content = Column(Text, nullable=False)
    tool_calls = Column(JSON, nullable=True)
    tool_results = Column(JSON, nullable=True)
    audio_duration_sec = Column(Float, nullable=True)
    detected_language = Column(String(20), default="tanglish")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
