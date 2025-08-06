"""
Authentication Service
Comprehensive authentication and user management for Arusha Catholic Seminary
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import uuid
import logging

from ..core.config import settings
from ..core.security import SecurityManager, create_tokens
from ..core.exceptions import (
    AuthenticationException, ValidationException, NotFoundException,
    ConflictException, DatabaseException
)
from ..models.user import User, UserProfile, PasswordReset, UserSession, UserRole

# Configure logging
logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service for user management and authentication"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username/email and password"""
        try:
            # Find user by username or email
            user = self.db.query(User).filter(
                or_(
                    User.username == username,
                    User.email == username
                )
            ).first()
            
            if not user:
                logger.warning(f"Authentication failed: User not found - {username}")
                return None
            
            if not SecurityManager.verify_password(password, user.hashed_password):
                logger.warning(f"Authentication failed: Invalid password for user - {username}")
                return None
            
            if not user.is_active:
                logger.warning(f"Authentication failed: Inactive user - {username}")
                return None
            
            # Update last login
            user.last_login = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"User authenticated successfully: {username}")
            return user
        
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            self.db.rollback()
            raise DatabaseException(f"Authentication failed: {str(e)}")
    
    def create_user(self, user_data: Dict[str, Any]) -> User:
        """Create a new user with validation"""
        try:
            # Validate required fields
            required_fields = ["username", "email", "password", "full_name"]
            for field in required_fields:
                if not user_data.get(field):
                    raise ValidationException(f"Missing required field: {field}")
            
            # Validate email format
            if not SecurityManager.validate_email(user_data["email"]):
                raise ValidationException("Invalid email format")
            
            # Validate password strength
            is_strong, message = SecurityManager.validate_password_strength(user_data["password"])
            if not is_strong:
                raise ValidationException(f"Password validation failed: {message}")
            
            # Check if username already exists
            existing_user = self.db.query(User).filter(User.username == user_data["username"]).first()
            if existing_user:
                raise ConflictException("Username already exists")
            
            # Check if email already exists
            existing_email = self.db.query(User).filter(User.email == user_data["email"]).first()
            if existing_email:
                raise ConflictException("Email already exists")
            
            # Create user
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=SecurityManager.get_password_hash(user_data["password"]),
                full_name=user_data["full_name"],
                role=user_data.get("role", UserRole.STUDENT),
                phone=user_data.get("phone"),
                address=user_data.get("address"),
                date_of_birth=user_data.get("date_of_birth"),
                gender=user_data.get("gender"),
                passport_photo=user_data.get("passport_photo"),
                seminary_logo=user_data.get("seminary_logo")
            )
            
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"User created successfully: {user.username}")
            return user
        
        except (ValidationException, ConflictException):
            self.db.rollback()
            raise
        except Exception as e:
            logger.error(f"User creation error: {str(e)}")
            self.db.rollback()
            raise DatabaseException(f"Failed to create user: {str(e)}")
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.warning(f"User not found: {user_id}")
                return None
            
            return user
        
        except Exception as e:
            logger.error(f"Error getting user by ID: {str(e)}")
            raise DatabaseException(f"Failed to get user: {str(e)}")
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            user = self.db.query(User).filter(User.username == username).first()
            if not user:
                logger.warning(f"User not found: {username}")
                return None
            
            return user
        
        except Exception as e:
            logger.error(f"Error getting user by username: {str(e)}")
            raise DatabaseException(f"Failed to get user: {str(e)}")
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            user = self.db.query(User).filter(User.email == email).first()
            if not user:
                logger.warning(f"User not found: {email}")
                return None
            
            return user
        
        except Exception as e:
            logger.error(f"Error getting user by email: {str(e)}")
            raise DatabaseException(f"Failed to get user: {str(e)}")
    
    def update_user(self, user_id: int, update_data: Dict[str, Any]) -> Optional[User]:
        """Update user information"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                raise NotFoundException("User", str(user_id))
            
            # Update allowed fields
            allowed_fields = [
                "full_name", "phone", "address", "date_of_birth", 
                "gender", "passport_photo", "seminary_logo"
            ]
            
            for field, value in update_data.items():
                if field in allowed_fields and value is not None:
                    setattr(user, field, value)
            
            user.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"User updated successfully: {user.username}")
            return user
        
        except (NotFoundException, ValidationException):
            self.db.rollback()
            raise
        except Exception as e:
            logger.error(f"User update error: {str(e)}")
            self.db.rollback()
            raise DatabaseException(f"Failed to update user: {str(e)}")
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """Change user password"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                raise NotFoundException("User", str(user_id))
            
            # Verify current password
            if not SecurityManager.verify_password(current_password, user.hashed_password):
                raise AuthenticationException("Current password is incorrect")
            
            # Validate new password strength
            is_strong, message = SecurityManager.validate_password_strength(new_password)
            if not is_strong:
                raise ValidationException(f"Password validation failed: {message}")
            
            # Update password
            user.hashed_password = SecurityManager.get_password_hash(new_password)
            user.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Password changed successfully for user: {user.username}")
            return True
        
        except (NotFoundException, AuthenticationException, ValidationException):
            self.db.rollback()
            raise
        except Exception as e:
            logger.error(f"Password change error: {str(e)}")
            self.db.rollback()
            raise DatabaseException(f"Failed to change password: {str(e)}")
    
    def create_password_reset_token(self, email: str) -> str:
        """Create password reset token"""
        try:
            user = self.get_user_by_email(email)
            if not user:
                # Don't reveal if email exists or not
                logger.info(f"Password reset requested for non-existent email: {email}")
                return "reset_token_sent"
            
            # Invalidate existing tokens
            self.db.query(PasswordReset).filter(
                and_(
                    PasswordReset.user_id == user.id,
                    PasswordReset.is_used == False
                )
            ).update({"is_used": True})
            
            # Create new token
            token = str(uuid.uuid4())
            expires_at = datetime.utcnow() + timedelta(hours=24)
            
            reset_token = PasswordReset(
                user_id=user.id,
                token=token,
                expires_at=expires_at
            )
            
            self.db.add(reset_token)
            self.db.commit()
            
            logger.info(f"Password reset token created for user: {user.username}")
            return token
        
        except Exception as e:
            logger.error(f"Password reset token creation error: {str(e)}")
            self.db.rollback()
            raise DatabaseException(f"Failed to create password reset token: {str(e)}")
    
    def reset_password(self, token: str, new_password: str) -> bool:
        """Reset password using token"""
        try:
            # Find valid token
            reset_token = self.db.query(PasswordReset).filter(
                and_(
                    PasswordReset.token == token,
                    PasswordReset.is_used == False,
                    PasswordReset.expires_at > datetime.utcnow()
                )
            ).first()
            
            if not reset_token:
                raise ValidationException("Invalid or expired reset token")
            
            # Validate new password strength
            is_strong, message = SecurityManager.validate_password_strength(new_password)
            if not is_strong:
                raise ValidationException(f"Password validation failed: {message}")
            
            # Update user password
            user = self.get_user_by_id(reset_token.user_id)
            if not user:
                raise NotFoundException("User", str(reset_token.user_id))
            
            user.hashed_password = SecurityManager.get_password_hash(new_password)
            user.updated_at = datetime.utcnow()
            
            # Mark token as used
            reset_token.is_used = True
            reset_token.used_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"Password reset successfully for user: {user.username}")
            return True
        
        except (ValidationException, NotFoundException):
            self.db.rollback()
            raise
        except Exception as e:
            logger.error(f"Password reset error: {str(e)}")
            self.db.rollback()
            raise DatabaseException(f"Failed to reset password: {str(e)}")
    
    def create_user_session(self, user_id: int, device_info: str = None, ip_address: str = None, user_agent: str = None) -> Dict[str, str]:
        """Create user session with tokens"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                raise NotFoundException("User", str(user_id))
            
            # Create tokens
            tokens = create_tokens(user.id, user.username, user.role)
            
            # Create session record
            session = UserSession(
                user_id=user.id,
                session_token=tokens["access_token"],
                refresh_token=tokens["refresh_token"],
                device_info=device_info,
                ip_address=ip_address,
                user_agent=user_agent,
                expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
            )
            
            self.db.add(session)
            self.db.commit()
            
            logger.info(f"User session created: {user.username}")
            return tokens
        
        except (NotFoundException, ValidationException):
            self.db.rollback()
            raise
        except Exception as e:
            logger.error(f"Session creation error: {str(e)}")
            self.db.rollback()
            raise DatabaseException(f"Failed to create session: {str(e)}")
    
    def invalidate_session(self, session_token: str) -> bool:
        """Invalidate user session"""
        try:
            session = self.db.query(UserSession).filter(
                and_(
                    UserSession.session_token == session_token,
                    UserSession.is_active == True
                )
            ).first()
            
            if not session:
                logger.warning(f"Session not found for invalidation: {session_token}")
                return False
            
            session.is_active = False
            self.db.commit()
            
            logger.info(f"Session invalidated for user: {session.user_id}")
            return True
        
        except Exception as e:
            logger.error(f"Session invalidation error: {str(e)}")
            self.db.rollback()
            raise DatabaseException(f"Failed to invalidate session: {str(e)}")
    
    def get_users(self, skip: int = 0, limit: int = 100, role: str = None, active_only: bool = True) -> List[User]:
        """Get users with filtering and pagination"""
        try:
            query = self.db.query(User)
            
            if role:
                query = query.filter(User.role == role)
            
            if active_only:
                query = query.filter(User.is_active == True)
            
            users = query.offset(skip).limit(limit).all()
            return users
        
        except Exception as e:
            logger.error(f"Error getting users: {str(e)}")
            raise DatabaseException(f"Failed to get users: {str(e)}")
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user (soft delete by setting is_active to False)"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                raise NotFoundException("User", str(user_id))
            
            # Soft delete
            user.is_active = False
            user.updated_at = datetime.utcnow()
            
            # Invalidate all sessions
            self.db.query(UserSession).filter(
                and_(
                    UserSession.user_id == user_id,
                    UserSession.is_active == True
                )
            ).update({"is_active": False})
            
            self.db.commit()
            
            logger.info(f"User deleted (soft): {user.username}")
            return True
        
        except (NotFoundException, ValidationException):
            self.db.rollback()
            raise
        except Exception as e:
            logger.error(f"User deletion error: {str(e)}")
            self.db.rollback()
            raise DatabaseException(f"Failed to delete user: {str(e)}")
