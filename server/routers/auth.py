from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import UserCreate, UserLogin, UserProfile, Token, User
from ..utils.auth import (
    get_password_hash, 
    authenticate_user, 
    create_access_token,
    get_user_by_email,
    get_user_by_id,
    verify_token
)
from ..utils.logging import logger, log_error

router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=UserProfile)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    logger.info(f"Registration attempt for email: {user.email}")
    
    try:
        # Check if user already exists
        db_user = get_user_by_email(db, email=user.email)
        if db_user:
            logger.warning(f"Registration failed: Email {user.email} already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            hashed_password=hashed_password,
            first_name=user.first_name,
            age=user.age,
            preferred_language=user.preferred_language,
            state=user.state
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"User registered successfully: {user.email} (ID: {db_user.id})")
        
        return UserProfile(
            id=str(db_user.id),
            email=db_user.email,
            first_name=db_user.first_name,
            age=db_user.age,
            preferred_language=db_user.preferred_language,
            state=db_user.state,
            created_at=db_user.created_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, "user_registration", email=user.email)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )

@router.post("/login", response_model=Token)
def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return JWT token."""
    logger.info(f"Login attempt for email: {user_credentials.email}")
    
    try:
        user = authenticate_user(db, user_credentials.email, user_credentials.password)
        if not user:
            logger.warning(f"Login failed: Invalid credentials for {user_credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            logger.warning(f"Login failed: Inactive user {user_credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        # Create user profile for response
        user_profile = UserProfile(
            id=str(user.id),
            email=user.email,
            first_name=user.first_name,
            age=user.age,
            preferred_language=user.preferred_language,
            state=user.state,
            created_at=user.created_at.isoformat()
        )
        
        logger.info(f"User logged in successfully: {user.email} (ID: {user.id})")
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_profile
        )
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, "user_login", email=user_credentials.email)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )

@router.get("/me", response_model=UserProfile)
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current user profile."""
    token = credentials.credentials
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_user_by_id(db, user_id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return UserProfile(
        id=str(user.id),
        email=user.email,
        first_name=user.first_name,
        age=user.age,
        preferred_language=user.preferred_language,
        state=user.state,
        created_at=user.created_at.isoformat()
    )
