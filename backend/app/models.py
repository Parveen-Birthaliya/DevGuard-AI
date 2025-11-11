from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import uuid

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index = True)
    github_id = Column(Integer, unique = True, index = True, nullable = False)
    username = Column(String, unique = True, index=True, nullable=False)
    email = Column(String, unique = True, index=True)
    avatar_url = Column(String)
    access_token = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default = func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    repositories = relationship("Repository", back_populates="user")
    scans = relationship("Scan", back_popuates="user")


class Repository(Base):
    # GitHub repositories monitored by DevGuard.
    __tablename__ = 'repositories'

    id = Column(Integer, primary_key=True, index= True)
    github_id = Column(Integer, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    full_name = Column(String,nullable=False)
    owner = Column(String, nullable=False)
    private = Column(Boolean, default=False)
    url = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="repositories")
    scans = relationship("Scan", back_populates="repository")

class Scan(Base):
    # Security scans performed on repositories.
    __tablename__ = 'scans'

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey('repositories.id'))
    pr_number = Column(Integer, nullable=False)
    pr_title = Column(String, nullable= False)
    commit_sha = Column(String, nullable=False)

    status = Column(String, default="pending")  # pending, running, completed, failed
    agents_completed = Column(Integer, default=0) 
    agents_total = Column(Integer, default=5)  
    
    findings_count = Column(Integer, default=0)
    critical_count = Column(Integer, default=0)
    high_count = Column(Integer, default=0)
    medium_count = Column(Integer, default=0)
    low_count = Column(Integer, default=0)
    
    agent_summaries = Column(JSON)  # {agent_name: {status, findings_count, summary}}
    
    user_id = Column(Integer, ForeignKey("users.id"))
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    repository = relationship("Repository", back_populates="scans")
    user = relationship("User", back_populates="scans")
    findings = relationship("Finding", back_populates="scan")


class Finding(Base):
    __tablename__ = "findings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_id = Column(Integer, ForeignKey("scans.id"))
    
    agent_name = Column(String, nullable=False, index=True) 
    
    tool = Column(String, nullable=False)
    rule_id = Column(String)  # Specific rule that triggered
    
    severity = Column(String, nullable=False)  # critical, high, medium, low, info
    category = Column(String, nullable=False)  # security, performance, logic, style
    title = Column(String, nullable=False)
    description = Column(Text)

    file_path = Column(String, nullable=False)
    line_start = Column(Integer)
    line_end = Column(Integer)
    code_snippet = Column(Text)
    
    evidence = Column(Text)  # Why this is an issue
    confidence = Column(Float, default=1.0)  # 0.0 to 1.0
    
    suggestion = Column(Text)
    fix_code = Column(Text)  
    
    status = Column(String, default="open")  # open, false_positive, fixed, ignored
    metadata = Column(JSON)  
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    scan = relationship("Scan", back_populates="findings")


class AgentExecution(Base):
    """
    Track individual agent executions for observability.
    Helps debug which agents are slow or failing.
    """
    __tablename__ = "agent_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"))
    agent_name = Column(String, nullable=False)
    
    status = Column(String, default="pending")  # pending, running, completed, failed
    findings_count = Column(Integer, default=0)
    
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    
    # Performance metrics
    execution_time_ms = Column(Integer)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())