from email.policy import default
from flask_login import UserMixin
from sqlalchemy import Enum

from apo import db
from apo.enums import SemesterEnum


class Users(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.String(50), primary_key=True, unique=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, unique=False)
    email = db.Column(db.String(50), nullable=False, unique=True)

    def __str__(self) -> str:
        return f"(User: {self.id}, name: {self.name}, email: {self.email})"


class SubjectCodes(db.Model):
    __tablename__ = "subject_codes"
    subject_code = db.Column(db.String(4), unique=True, primary_key=True)

    classes = db.relationship("BacktestClasses", back_populates="subject_code_rel")

    def __str__(self) -> str:
        return f"(Subject Code: {self.subject_code})"


class BacktestClasses(db.Model):
    __tablename__ = "backtest_classes"
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    subject_code = db.Column(
        db.String(4),
        db.ForeignKey("subject_codes.subject_code"),
        nullable=False,
        unique=False,
    )
    course_number = db.Column(db.Integer, nullable=False, unique=False)
    name_of_class = db.Column(db.String(150), nullable=False, unique=False)

    subject_code_rel = db.relationship("SubjectCodes", back_populates="classes")
    backtest_rel = db.relationship("Backtests", back_populates="class_rel")

    def __str__(self) -> str:
        return f"(Class: {self.id}, {self.subject_code} {self.course_number} {self.name_of_class})"


class Backtests(db.Model):
    __tablename__ = "backtest"
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    added = db.Column(db.Date, nullable=False, unique=False)
    class_id = db.Column(
        db.Integer,
        db.ForeignKey("backtest_classes.id"),
        nullable=False,
        unique=False,
    )
    exam = db.Column(db.Boolean, unique=False, default=False)
    quiz = db.Column(db.Boolean, unique=False, default=False)
    midterm = db.Column(db.Boolean, unique=False, default=False)
    year = db.Column(db.Integer, nullable=False, unique=False)
    semester = db.Column(Enum(SemesterEnum), nullable=False, unique=False)
    backtest_number = db.Column(db.Integer, nullable=False, unique=False)  # E1 or E2
    backtest_count = db.Column(db.Integer, nullable=False, unique=False)  # quantitiy

    class_rel = db.relationship("BacktestClasses", back_populates="backtest_rel")

    def __str__(self) -> str:
        if self.quiz:
            f"{self.subject_code} {self.course_number} {self.name_of_class} Quiz {self.backtest_number} {self.year} {self.semester} count: {self.backtest_count}, id: {self.id}, added {self.added}"
        elif self.exam:
            return f"{self.subject_code} {self.course_number} {self.name_of_class} Exam {self.backtest_number} {self.year} {self.semester} count: {self.backtest_count}, id: {self.id}, added {self.added}"
        return f"{self.subject_code} {self.course_number} {self.name_of_class} Midterm {self.backtest_number} {self.year} {self.semester} count: {self.backtest_count}, id: {self.id}, added {self.added}"


class Chargers(db.Model):
    __tablename__ = "chargers"
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    in_office = db.Column(db.Boolean, nullable=False, unique=False)
    checked_out = db.Column(db.DateTime, nullable=False, unique=False)
    description = db.Column(db.Text, nullable=False, unique=False)
    phone_area_code = db.Column(db.Integer, nullable=True, unique=False)
    phone_middle = db.Column(db.Integer, nullable=True, unique=False)
    phone_end = db.Column(db.Integer, nullable=True, unique=False)

    def __str__(self) -> str:
        return f"Charger {self.id}, checked_out: {self.checked_out}, in office: {self.in_office}, phone: ({self.phone_area_code}){self.phone_middle}-{self.phone_end}"


class Locations(db.Model):
    __tablename__ = "locations"
    name = db.Column(db.String(50), primary_key=True, nullable=False, unique=True)

    lost_reports = db.relationship(
        "LostReportsLocations", back_populates="location_rel", passive_deletes=True
    )
    lost_item_rel = db.relationship("LostItems", back_populates="location_rel")

    def __str__(self) -> str:
        return f"Location {self.name}"


class ItemTypes(db.Model):
    __tablename__ = "item_types"
    name = db.Column(db.String(30), primary_key=True, nullable=False, unique=True)

    lost_reports = db.relationship("LostReports", back_populates="item_type_rel")
    lost_item = db.relationship("LostItems", back_populates="item_type_rel")

    def __str__(self) -> str:
        return f"LAF Item Type {self.name}"


class LostReports(db.Model):
    __tablename__ = "lost_reports"
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    first_name = db.Column(db.String(40), nullable=False, unique=False)
    last_name = db.Column(db.String(50), nullable=False, unique=False)
    email = db.Column(db.String(100), nullable=False, unique=False)
    phone_area_code = db.Column(db.Integer, nullable=True, unique=False)
    phone_middle = db.Column(db.Integer, nullable=True, unique=False)
    phone_end = db.Column(db.Integer, nullable=True, unique=False)
    description = db.Column(db.Text, nullable=False, unique=False)
    item_type = db.Column(
        db.String(30),
        db.ForeignKey("laf_item_types.name"),
        nullable=False,
        unique=False,
    )
    date_lost = db.Column(db.Date, nullable=False, unique=False)
    date_added = db.Column(db.Date, nullable=False, unique=False)
    archived = db.Column(db.Boolean, nullable=False, unique=False, default=False)
    archived_dt = db.Column(db.DateTime, nullable=True, unique=False)

    locations = db.relationship(
        "LostReportsLocations", back_populates="lost_report_rel", passive_deletes=True
    )
    item_type_rel = db.relationship("ItemTypes", back_populates="lost_reports")

    def __str__(self) -> str:
        return f"Lost Report {self.id}, {self.first_name} {self.last_name} {self.email} ({self.phone_area_code}){self.phone_middle}-{self.phone_end}, description: {self.description}, {self.item_type}, locations: {self.locations}, lost: {self.date_lost}, added: {self.date_added}"


class LostReportsLocations(db.Model):
    __tablename__ = "lost_reports_locations"
    lost_report_id = db.Column(
        db.Integer,
        db.ForeignKey("lost_reports.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        unique=False,
    )
    location = db.Column(
        db.String(50),
        db.ForeignKey("locations.name", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        unique=False,
    )

    lost_report_rel = db.relationship("LostReports", back_populates="locations")
    location_rel = db.relationship("Locations", back_populates="lost_reports")

    def __str__(self) -> str:
        return f"Lost Report Location {self.id}, lost report: {self.lost_report_id}, location: {self.location}"


class LostItems(db.Model):
    __tablename__ = "lost_items"
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    description = db.Column(db.Text, nullable=False, unique=False)
    item_type = db.Column(
        db.String(30), db.ForeignKey("item_types.name"), nullable=False, unique=False
    )
    location = db.Column(
        db.String(30), db.ForeignKey("locations.name"), nullable=False, unique=False
    )
    date_lost = db.Column(db.Date, nullable=False, unique=False)
    archived = db.Column(db.Boolean, nullable=False, unique=False, default=False)
    archived_dt = db.Column(db.DateTime, nullable=True, unique=False)

    location_rel = db.relationship(
        "Locations", back_populates="lost_item_rel", passive_deletes=True
    )
    item_type_rel = db.relationship("ItemTypes", back_populates="lost_item")

    def __str__(self) -> str:
        return f"Lost Item {self.id}, {self.description}, {self.item_type}, {self.date_lost}"
