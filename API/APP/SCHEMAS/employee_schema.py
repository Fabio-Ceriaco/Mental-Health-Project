from pydantic import BaseModel, ConfigDict, EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber
from enum import Enum
from datetime import date
from typing import Optional


# =================== Base Employee Schema ===================#
class EmployeeBase(BaseModel):

    id: Optional[int]
    name: str
    email: EmailStr
    phone_number: PTPhone
    gender_id: Optional[int]
    date_of_birth: date
    zip_code: str
    location: str
    marital_status_id: int
    num_children: int
    hire_date: date
    contract_type_id: int
    department_id: int
    role_id: int
    role_name: Optional[str]

    model_config = ConfigDict(from_attributes=True)


# =================== Create Employee Schema ===================#


class EmployeeCreate(BaseModel):
    name: str
    email: EmailStr = Field(
        ..., description="Employee's email address", examples=["employee@example.com"]
    )
    phone_number: PTPhone = Field(
        ...,
        description="Employee's phone number in E164 format",
        examples=["+351912345678"],
    )
    gender_id: GenderEnum = Field(
        ...,
        description="ID representing the employee's gender example: 1-Masculino, 2-Feminino, 3-Nao_Binario, 4-Outro, 5-Prefiro_nao_dizer",
    )
    date_of_birth: date = Field(..., description="Employee's date of birth")
    zip_code: str = Field(..., description="Employee's ZIP code")
    location: str = Field(..., description="Employee's location")
    marital_status_id: MaritalStatusEnum = Field(
        ...,
        description="ID representing the employee's marital status example: 1-Solteiro, 2-Casado, 3-Divorciado, 4-Viuvo, 5-Outro",
    )
    num_children: int = Field(
        ..., ge=0, description="Number of children the employee has"
    )
    hire_date: date = Field(..., description="Employee's hire date")
    contract_type_id: ContractTypeEnum = Field(
        ...,
        description="ID representing the type of contract example: 1-Sem_Termo, 2-Termo_Certo, 3-Termo_Incerto, 4-Trabalho_Temporário, 5-Prestação_de_Serviços, 6-Estágio_Profissional, 7-Aprendizagem, 8-Regime_de_Part_Time",
    )
    department_id: DepartmentEnum = Field(
        ...,
        description="ID representing the employee's department example: 1-Produção, 2-Qualidade, 3-Pesquisa_e_Desenvolvimento, 4-Vendas, 5-Marketing, 6-Atendimento_ao_Cliente, 7-Finanças, 8-Tecnologia_da_Informação, 9-Manutenção, 10-Logistica, 11-Recursos_Humanos, 12-Engenharia, 13-Segurança_e_Higiene, 14-Administração",
    )
    role_id: OptionItem
    created_at: Optional[date]
    updated_at: Optional[date]

    model_config = ConfigDict(from_attributes=True)


# =================== Update Employee Schema ===================#


class EmployeeUpdate(BaseModel):

    name: Optional[str]
    phone_number: Optional[PTPhone]
    gender_id: Optional[int]
    date_of_birth: Optional[date]
    zip_code: Optional[str]
    location: Optional[str]
    marital_status_id: Optional[int]
    num_children: Optional[int]


# =================== Employee Response Schema ===================#


class EmployeeResponse(EmployeeBase):

    pass

    model_config = ConfigDict(from_attributes=True)


# =================== Employee Profile Response Schema ===================#


class EmployeeProfileResponse(BaseModel):

    name: str = Field(
        ..., min_length=3, max_length=50, description="Employee's full name"
    )
    phone_number: PTPhone = Field(
        ..., description="Employee's phone number in E.164 format"
    )

    gender_id: Optional[int]
    gender_label: Optional[str]

    date_of_birth: date = Field(..., description="Employee's date of birth")
    zip_code: str = Field(..., description="Employee's ZIP code")
    location: str = Field(..., description="Employee's location")

    marital_status_id: Optional[int]
    marital_status_label: Optional[str]
    num_children: int = Field(
        ..., ge=0, description="Number of children the employee has"
    )
    role_id: Optional[int]
    role_label: Optional[str]

    model_config = ConfigDict(from_attributes=True)


# =================== Employee Profile Options Schema ===================#


class OptionItem(BaseModel):
    id: int
    label: str

    model_config = ConfigDict(from_attributes=True)


# ================== Employee Profile Options Response Schema ===================#


class EmployeeProfileOptionsResponse(BaseModel):
    genders: list[OptionItem]
    marital_status: list[OptionItem]
    role: list[OptionItem]

    model_config = ConfigDict(from_attributes=True)


# ===============Phone Number Type================#


## Custom Phone Number Type for Portugal
class PTPhone(PhoneNumber):

    default_region_code = "PT"
    supported_regions = ["PT"]
    phone_format = "E164"


# ====================== Enums ===================#


class GenderEnum(int, Enum):
    Masculino = 1
    Feminino = 2
    Nao_Binario = 3
    Outro = 4
    Prefiro_nao_dizer = 5


class MaritalStatusEnum(int, Enum):
    Solteiro = 1
    Casado = 2
    Divorciado = 3
    Viuvo = 4
    Outro = 5


class ContractTypeEnum(int, Enum):
    Sem_Termo = 1
    Termo_Certo = 2
    Termo_Incerto = 3
    Trabalho_Temporário = 4
    Prestação_de_Serviços = 5
    Estágio_Profissional = 6
    Aprendizagem = 7
    Regime_de_Part_Time = 8


class DepartmentEnum(int, Enum):
    Produção = 1
    Qualidade = 2
    Pesquisa_e_Desenvolvimento = 3
    Vendas = 4
    Marketing = 5
    Atendimento_ao_Cliente = 6
    Finanças = 7
    Tecnologia_da_Informação = 8
    Manutenção = 9
    Logistica = 10
    Recursos_Humanos = 11
    Engenharia = 12
    Segurança_e_Higiene = 13
    Administração = 14


class RoleEnum(int, Enum):
    Executive = 1
    Admin = 2
    User = 3
