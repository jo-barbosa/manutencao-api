from typing import List, Optional
import strawberry
from sqlmodel import Session, select
from services.auth_service.database import engine
from services.auth_service.models import Superuser
from services.auth_service.security import verify_password, get_password_hash, create_access_token, decode_token

@strawberry.type
class SuperuserType:
    id: int
    nome: str
    email: str

@strawberry.type
class AuthTokenPayload:
    access_token: str
    token_type: str = "bearer"
    user: SuperuserType

@strawberry.type
class Query:
    @strawberry.field
    def superusers(self) -> List[SuperuserType]:
        with Session(engine) as session:
            users = session.exec(select(Superuser)).all()
            return [SuperuserType(id=u.id, nome=u.nome, email=u.email) for u in users]

    @strawberry.field
    def me(self, token: str) -> Optional[SuperuserType]:
        payload = decode_token(token)
        if not payload or "sub" not in payload:
            return None
        email = payload["sub"]
        with Session(engine) as session:
            user = session.exec(select(Superuser).where(Superuser.email == email)).first()
            if user:
                return SuperuserType(id=user.id, nome=user.nome, email=user.email)
        return None

@strawberry.type
class Mutation:
    @strawberry.mutation
    def login(self, email: str, password: str) -> Optional[AuthTokenPayload]:
        with Session(engine) as session:
            user = session.exec(select(Superuser).where(Superuser.email == email)).first()
            if not user or not verify_password(password, user.password_hash):
                return None
            token = create_access_token({"sub": user.email, "user_id": user.id})
            su_type = SuperuserType(id=user.id, nome=user.nome, email=user.email)
            return AuthTokenPayload(access_token=token, user=su_type)

    @strawberry.mutation
    def criar_superuser(self, nome: str, email: str, password: str) -> SuperuserType:
        with Session(engine) as session:
            existing = session.exec(select(Superuser).where(Superuser.email == email)).first()
            if existing:
                raise ValueError("Email já registado")
            hashed = get_password_hash(password)
            user = Superuser(nome=nome, email=email, password_hash=hashed)
            session.add(user)
            session.commit()
            session.refresh(user)
            return SuperuserType(id=user.id, nome=user.nome, email=user.email)

schema = strawberry.Schema(query=Query, mutation=Mutation)
