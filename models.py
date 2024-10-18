from sqlalchemy import Column, String, SmallInteger, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.schema import MetaData

Base = declarative_base(metadata=MetaData())


class TypePerson(Base):
    __tablename__ = 'type_person'  # noqa

    value = Column(String(16), primary_key=True)


class Counterparties(Base):
    __tablename__ = 'counterparties'  # noqa

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=True)
    internal_name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    person: Mapped[str] = mapped_column(String(16), ForeignKey('type_person.value'), nullable=False, default='Юр. лицо')
    INN: Mapped[str] = mapped_column(String(12), nullable=False, unique=True)
    KPP: Mapped[str] = mapped_column(String(9))
    OGRN: Mapped[str] = mapped_column(String(15), unique=True)
    heads: Mapped[dict] = mapped_column(JSON, nullable=False,
                                        default={"Фамилия Имя Отчество": {"position": "Должность", "surname": "Фамилия",
                                                                          "first_name": "Имя",
                                                                          "middle_name": "Отчество", "sex": "Пол",
                                                                          "act_upon": "Устава",
                                                                          "from_date_of": "2000-01-01",
                                                                          "up_to_date_of": ""}})
    banks: Mapped[dict] = mapped_column(JSON, nullable=False,
                                        default={"Название банка": {"account": "00000000000000000000",
                                                                    "name": "Наименование банка",
                                                                    "corr_account": "00000000000000000000",
                                                                    "bik": "000000000"}})
    full_name: Mapped[str] = mapped_column(String(512), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
