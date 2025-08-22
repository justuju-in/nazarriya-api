from database import engine, SessionLocal
from models import Base, User, ChatSession, ChatMessage
from sqlalchemy.orm import Session
import uuid

def init_db():
    """Initialize the database with tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

def create_sample_data():
    """Create sample data for testing"""
    db = SessionLocal()
    try:
        # Check if we already have users
        existing_user = db.query(User).first()
        if existing_user:
            print("Sample data already exists, skipping...")
            return
        
        print("Creating sample data...")
        
        # Create a sample user
        sample_user = User(
            id=uuid.uuid4(),
            email="test@nazarriya.com",
            hashed_password="hashed_password_here",  # In production, this would be properly hashed
            first_name="Test",
            age=25,
            preferred_language="English",
            state="Maharashtra"
        )
        db.add(sample_user)
        db.commit()
        
        # Create a sample chat session
        sample_session = ChatSession(
            id=uuid.uuid4(),
            user_id=sample_user.id,
            title="Sample Conversation",
            session_data={"topic": "gender and consent", "language": "English"}
        )
        db.add(sample_session)
        db.commit()
        
        # Create sample messages
        sample_messages = [
            ChatMessage(
                id=uuid.uuid4(),
                session_id=sample_session.id,
                sender_type="user",
                content="What does mutual consent mean?",
                message_data={"timestamp": "2024-01-01T10:00:00Z"}
            ),
            ChatMessage(
                id=uuid.uuid4(),
                session_id=sample_session.id,
                sender_type="bot",
                content="Mutual consent means that all parties involved in any activity must freely and willingly agree to participate. It's about clear communication and respect for boundaries.",
                message_data={"sources": ["consent_guide.pdf"], "timestamp": "2024-01-01T10:01:00Z"}
            )
        ]
        
        for message in sample_messages:
            db.add(message)
        
        db.commit()
        print("Sample data created successfully!")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    create_sample_data()
