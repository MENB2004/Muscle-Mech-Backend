from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.client_model import Client
from app.schemas.client_schema import ClientCreate, ClientUpdate, ClientResponse, ClientWithUserCreate
from app.auth.role_checker import RoleChecker
from app.auth.dependencies import get_current_user, allow_all, allow_admin, allow_staff
from app.models.user_model import User
from app.models.trainer_model import Trainer

from app.models.payment_model import Payment
from app.models.communication_model import Announcement
from app.auth.password_handler import hash_password
from app.services.payment_service import get_client_fee_status

router = APIRouter(
    prefix="/clients",
    tags=["Clients"]
)

@router.get("/", response_model=List[ClientResponse])
def get_clients(db: Session = Depends(get_db), current_user: User = Depends(allow_all)):
    query = db.query(Client)
    if current_user.role in ["admin", "trainer"]:
        clients = query.all()
    else: # client
        clients = query.filter(Client.user_id == current_user.id).all()
    
    # Inject user name and dynamic fee status
    for c in clients:
        fee_data = get_client_fee_status(db, c)
        c.membership_status = fee_data["membership_status"]
        c.next_due_date = fee_data["next_due_date"]
        c.days_remaining = fee_data["days_remaining"]
        if hasattr(c, 'user') and c.user:
            c.avatar_url = c.user.avatar_url
        else:
            c.avatar_url = None
        
    return clients

@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client(client_data: ClientCreate, db: Session = Depends(get_db), current_user: User = Depends(allow_admin)):
    # Check if user already has a client profile
    existing = db.query(Client).filter(Client.user_id == client_data.user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already has a client profile")
        
    new_client = Client(**client_data.dict())
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    return new_client

@router.post("/with-user", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client_with_user(client_data: ClientWithUserCreate, db: Session = Depends(get_db), current_user: User = Depends(allow_staff)):
    existing_user = db.query(User).filter(User.email == client_data.email).first()
    
    if existing_user:
        # Check if they already have a client profile
        existing_client = db.query(Client).filter(Client.user_id == existing_user.id).first()
        if existing_client:
            raise HTTPException(status_code=400, detail="A client with this phone number already exists.")
        
        # User exists but no client profile - we can link them
        new_user = existing_user
    else:
        # Create new user
        new_user = User(
            name=client_data.name,
            email=client_data.email,
            password=hash_password(client_data.password),
            role="client",
            avatar_url=client_data.avatar_url,
            must_change_password=True,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

    new_client = Client(
        user_id=new_user.id,
        goal=client_data.goal,
        height=client_data.height,
        weight=client_data.weight,
        phone=client_data.phone,
        monthly_fee=client_data.monthly_fee,
    )

    if current_user.role == "trainer":
        trainer = db.query(Trainer).filter(Trainer.user_id == current_user.id).first()
        if trainer:
            new_client.trainer_id = trainer.id
    
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    
    # Manually populate name for response if it's an existing user
    new_client.name = new_user.name 
    return new_client

@router.get("/{client_id}", response_model=ClientResponse)
def get_client(client_id: int, db: Session = Depends(get_db), current_user: User = Depends(allow_all)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
        
    # Permission checks
    if current_user.role in ["admin", "trainer"]:
        pass # full access
    else: # client
        if client.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to view this profile")
    
    fee_data = get_client_fee_status(db, client)
    client.membership_status = fee_data["membership_status"]
    client.next_due_date = fee_data["next_due_date"]
    client.days_remaining = fee_data["days_remaining"]
    if hasattr(client, 'user') and client.user:
        client.avatar_url = client.user.avatar_url
    else:
        client.avatar_url = None
    
    return client

@router.put("/bulk-fee", status_code=status.HTTP_200_OK)
def update_bulk_fee(fee_data: __import__('app.schemas.client_schema', fromlist=['BulkFeeUpdate']).BulkFeeUpdate, db: Session = Depends(get_db), current_user: User = Depends(allow_admin)):
    new_fee = fee_data.new_fee
    
    # Update all clients
    db.query(Client).update({Client.monthly_fee: new_fee}, synchronize_session=False)
    
    # Create system announcement
    announcement = Announcement(
        title="Fee Update",
        content=f"The standard monthly gym fee has been updated to ₹{new_fee}",
        type="alert"
    )
    db.add(announcement)
    db.commit()
    
    return {"message": "Fee updated successfully", "new_fee": new_fee}

@router.put("/{client_id}", response_model=ClientResponse)
def update_client(client_id: int, client_data: ClientUpdate, db: Session = Depends(get_db), current_user: User = Depends(allow_staff)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Logic: Trainers can update any client
    data = client_data.dict(exclude_unset=True)
    # Security: Only admins can change monthly_fee
    if current_user.role != "admin":
        data.pop("monthly_fee", None)

    # Handle avatar_url update on the User model
    if "avatar_url" in data:
        avatar_url = data.pop("avatar_url")
        if client.user:
            client.user.avatar_url = avatar_url

    for key, value in data.items():
        setattr(client, key, value)
    
    db.commit()
    db.refresh(client)
    return client

@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(client_id: int, db: Session = Depends(get_db), current_user: User = Depends(allow_staff)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    user_id = client.user_id
    

    db.query(Payment).filter(Payment.client_id == client_id).delete(synchronize_session=False)
    
    if user_id:
        db.query(Announcement).filter(
            (Announcement.recipient_id == user_id) | (Announcement.sender_id == user_id)
        ).delete(synchronize_session=False)
        user = db.query(User).filter(User.id == user_id).first()
        db.delete(client)
        if user:
            db.delete(user)
    else:
        db.delete(client)
            
    db.commit()
    return None
