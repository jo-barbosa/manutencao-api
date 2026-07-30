from datetime import datetime
from enum import Enum
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


# ==========================================
# 1. ENUMS
# ==========================================

class EstadoSistema(str, Enum):
    OPERACIONAL = "OPERACIONAL"  # Verde
    DEGRADADO = "DEGRADADO"      # Amarelo (Impacto Parcial)
    PARADO = "PARADO"            # Vermelho (Impacto Total)


class StatusAcao(str, Enum):
    ABERTA = "ABERTA"
    FECHADA = "FECHADA"


class Impacto(str, Enum):
    TOTAL = "TOTAL"
    PARCIAL = "PARCIAL"
    NENHUM = "NENHUM"


# ==========================================
# 2. AGREGADO: FORNECEDOR & SUPERUSER
# ==========================================

class Fornecedor(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    contacto: Optional[str] = None

    # Relacionamento: Um fornecedor pode fornecer vários sistemas
    sistemas: List["Sistema"] = Relationship(back_populates="fornecedor")


class Superuser(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    email: str = Field(unique=True, index=True)
    password_hash: str

    # Relacionamento: Um superuser pode ser responsável por várias ações
    acoes: List["Acao"] = Relationship(back_populates="responsavel")


# ==========================================
# 3. AGREGADO: ESTRUTURA FABRIL
# ==========================================

class Fabrica(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    localizacao: Optional[str] = None

    # Relacionamento: 1 Fábrica -> Muitas Linhas
    linhas: List["Linha"] = Relationship(back_populates="fabrica")


class Linha(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str

    # Ligação a Fábrica (FK)
    fabrica_id: Optional[int] = Field(default=None, foreign_key="fabrica.id")
    fabrica: Optional[Fabrica] = Relationship(back_populates="linhas")

    # Relacionamento: 1 Linha -> Muitos Sistemas
    sistemas: List["Sistema"] = Relationship(back_populates="linha")


class Sistema(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    estado_atual: EstadoSistema = Field(default=EstadoSistema.OPERACIONAL)

    # Ligação a Linha (FK)
    linha_id: Optional[int] = Field(default=None, foreign_key="linha.id")
    linha: Optional[Linha] = Relationship(back_populates="sistemas")

    # Ligação a Fornecedor (FK)
    fornecedor_id: Optional[int] = Field(default=None, foreign_key="fornecedor.id")
    fornecedor: Optional[Fornecedor] = Relationship(back_populates="sistemas")

    # Relacionamento: 1 Sistema -> Muitas Ações
    acoes: List["Acao"] = Relationship(back_populates="sistema")


# ==========================================
# 4. AGREGADO: OPERAÇÕES & MANUTENÇÃO
# ==========================================

class Acao(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    comentario: Optional[str] = None
    status: StatusAcao = Field(default=StatusAcao.ABERTA)
    impacto: Impacto = Field(default=Impacto.NENHUM)

    # Value Object: IntervaloTempo (Achatado em colunas datetime)
    data_criacao: datetime = Field(default_factory=datetime.now)
    data_prevista_conclusao: Optional[datetime] = None
    data_conclusao: Optional[datetime] = None

    # Ligação ao Sistema (FK)
    sistema_id: Optional[int] = Field(default=None, foreign_key="sistema.id")
    sistema: Optional[Sistema] = Relationship(back_populates="acoes")

    # Ligação ao Responsável/Superuser (FK)
    responsavel_id: Optional[int] = Field(default=None, foreign_key="superuser.id")
    responsavel: Optional[Superuser] = Relationship(back_populates="acoes")

# ==========================================
# 5. AGREGADO: REGISTO DE AUDITORIA
# ==========================================

class RegistoAuditoria(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    utilizador_email: str
    acao_realizada: str  # Ex: "CRIAR_ACAO", "ALTERAR_ESTADO_SISTEMA"
    detalhes: str        # Descrição em texto do que mudou
    timestamp: datetime = Field(default_factory=datetime.now)