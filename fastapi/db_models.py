from enum import Enum
from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
    Date,
    DateTime,
)
from sqlalchemy.orm import relationship

from .database import Base
from .enums import SemesterEnum
from .dependencies import CustomSerializerMixin


class Users(Base):
    __tablename__ = "user"
    id = Column(String(50), primary_key=True, unique=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=False)
    email = Column(String(50), nullable=False, unique=True)

    def __str__(self) -> str:
        return f"(User: {self.id}, name: {self.name}, email: {self.email})"


class SubjectCodes(Base, CustomSerializerMixin):
    __tablename__ = "subject_codes"

    serialize_only = ("subject_code",)
    serialize_rules = ()

    subject_code = Column(String(4), unique=True, primary_key=True)

    def __str__(self) -> str:
        return f"(Subject Code: {self.subject_code})"


class BacktestClasses(Base, CustomSerializerMixin):
    __tablename__ = "backtest_classes"

    serialize_only = ("subject_code", "course_number", "name_of_class")
    serialize_rules = ()

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    subject_code = Column(
        String(4),
        ForeignKey("subject_codes.subject_code"),
        nullable=False,
        unique=False,
        ondelete="CASCADE",
    )
    course_number = Column(Integer, nullable=False, unique=False)
    name_of_class = Column(String(150), nullable=False, unique=False)

    subject_code_rel = relationship("SubjectCodes")

    def __str__(self) -> str:
        return f"(Class: {self.id}, {self.subject_code} {self.course_number} {self.name_of_class})"


class Backtests(Base, CustomSerializerMixin):
    __tablename__ = "backtest"

    serialize_only = (
        "exam",
        "quiz",
        "midterm",
        "year",
        "semester",
        "backtest_number",
        "backtest_quantity",
    )
    serialize_rules = ()

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    added = Column(DateTime, nullable=False, unique=False)
    class_id = Column(
        Integer,
        ForeignKey("backtest_classes.id"),
        nullable=False,
        unique=False,
        ondelete="CASCADE",
    )
    exam = Column(Boolean, unique=False, default=False)
    quiz = Column(Boolean, unique=False, default=False)
    midterm = Column(Boolean, unique=False, default=False)
    year = Column(Integer, nullable=False, unique=False)
    semester = Column(Enum(SemesterEnum), nullable=False, unique=False)
    backtest_number = Column(Integer, nullable=False, unique=False)  # E1 or E2
    backtest_quantity = Column(Integer, nullable=False, unique=False)  # quantity

    def __str__(self) -> str:
        return f"(Backtest: {self.id}, {self.added}, {self.class_id}, {self.exam}, {self.quiz}, {self.midterm}, {self.year}, {self.semester}, {self.backtest_number}, {self.backtest_quantity})"


class Chargers(Base, CustomSerializerMixin):
    __tablename__ = "chargers"

    serialize_only = (
        "in_office",
        "checked_out",
        "description",
        "phone_area_code",
        "phone_middle",
        "phone_end",
    )
    serialize_rules = ()

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    in_office = Column(Boolean, nullable=False, unique=False)
    checked_out = Column(DateTime, nullable=False, unique=False)
    description = Column(Text, nullable=False, unique=False)
    phone_area_code = Column(Integer, nullable=True, unique=False)
    phone_middle = Column(Integer, nullable=True, unique=False)
    phone_end = Column(Integer, nullable=True, unique=False)

    def __str__(self) -> str:
        return f"Charger {self.id}, checked_out: {self.checked_out}, in office: {self.in_office}, phone: ({self.phone_area_code}){self.phone_middle}-{self.phone_end}"


class Locations(Base, CustomSerializerMixin):
    __tablename__ = "locations"

    serialize_only = ("name",)
    serialize_rules = ()

    name = Column(
        String(50), primary_key=True, unique=True, nullable=False, unique=True
    )

    def __str__(self) -> str:
        return f"Location {self.id}, {self.name}"


class ItemType(Base, CustomSerializerMixin):
    __tablename__ = "item_type"

    serialize_only = ("name",)
    serialize_rules = ()

    name = Column(
        String(50), primary_key=True, unique=True, nullable=False, unique=True
    )

    def __str__(self) -> str:
        return f"Item Type {self.name}, {self.description}"


class LostReports(Base, CustomSerializerMixin):
    __tablename__ = "lost_reports"

    serialize_only = (
        "id",
        "first_name",
        "last_name",
        "email",
        "phone",
        "description",
        "item_type",
        "date_lost",
        "added",
    )
    serialize_rules = ()

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    first_name = Column(String(40), nullable=False, unique=False)
    last_name = Column(String(50), nullable=False, unique=False)
    email = Column(String(70), nullable=False, unique=False)
    phone_area_code = Column(Integer, nullable=True, unique=False)
    phone_middle = Column(Integer, nullable=True, unique=False)
    phone_end = Column(Integer, nullable=True, unique=False)
    description = Column(Text, nullable=False, unique=False)
    item_type = Column(
        String(50), ForeignKey("item_type.name"), nullable=False, unique=False
    )
    date_lost = Column(Date, nullable=False, unique=False)
    added = Column(DateTime, nullable=False, unique=False)
    archived = Column(Boolean, nullable=False, unique=False, default=False)
    archived_dt = Column(DateTime, nullable=True, unique=False)
    # match column with LAF item

    locations_rel = relationship(
        "LostReportLocations", back_populates="lost_report_rel", passive_deletes=True
    )

    def __str__(self) -> str:
        return f"Lost Report {self.id}, {self.first_name} {self.last_name}, {self.email}, {self.phone_area_code}-{self.phone_middle}-{self.phone_end}, {self.description}, {self.date_lost}, {self.added}"


class LostReportLocations(Base):
    __tablename__ = "lost_report_locations"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    lost_report_id = Column(
        Integer,
        ForeignKey("lost_reports.id"),
        nullable=False,
        unique=False,
        ondelete="CASCADE",
    )
    location_id = Column(
        String(50),
        ForeignKey("locations.name"),
        nullable=False,
        unique=False,
        ondelete="CASCADE",
    )

    lost_report_rel = relationship("LostReports", back_populates="locations_rel")
    location_rel = relationship("Locations")

    def __str__(self) -> str:
        return f"Lost Report Location {self.id}, Lost Report: {self.lost_report_id}, Location: {self.location_id}"


class LostItems(Base, CustomSerializerMixin):
    __tablename__ = "lost_items"

    serialize_only = ("id", "description", "item_type", "location", "date_lost")
    serialize_rules = ()

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    description = Column(Text, nullable=False, unique=False)
    item_type = Column(
        String(50), ForeignKey("item_type.name"), nullable=False, unique=False
    )
    location = Column(
        String(50), ForeignKey("locations.id"), nullable=False, unique=False
    )
    date_lost = Column(Date, nullable=False, unique=False)
    archived = Column(Boolean, nullable=False, unique=False, default=False)
    archived_dt = Column(DateTime, nullable=True, unique=False)

    def __str__(self) -> str:
        return f"Lost Item {self.id}, {self.description}, {self.item_type}, {self.location}, {self.date_lost}"
