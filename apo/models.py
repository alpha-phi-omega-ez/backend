from flask_login import UserMixin

from apo import db


class Users(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.String(50), primary_key=True, unique=True)
    name = db.Column(db.String(50), nullable=False, unique=False)
    email = db.Column(db.String(50), nullable=False, unique=True)

    def __str__(self) -> str:
        return f"(User: {self.id}, name: {self.name}, email: {self.email})"


class BacktestClasses(db.Model):
    __tablename__ = "backtest_classes"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    subject_code = db.Column(db.String(4), nullable=False, unique=False)
    course_number = db.Column(db.Integer, nullable=False, unique=False)
    name_of_class = db.Column(db.String(150), nullable=False, unique=False)
    is_alias = db.Column(db.Boolean, nullable=False, unique=False)
    alias_subject_code = db.Column(db.String(4), nullable=True, unique=False)
    alias_course_number = db.Column(db.Integer, nullable=True, unique=False)

    def __str__(self) -> str:
        if self.is_alias:
            return f"(Class: {self.id}, {self.subject_code} {self.course_number} {self.name_of_class}), is alias to {self.alias_subject_code} {self.course_number}"
        return f"(Class: {self.id}, {self.subject_code} {self.course_number} {self.name_of_class})"


class Backtests(db.Model):
    __tablename__ = "backtest"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    added = db.Column(db.Date, nullable=False, unique=False)
    subject_code = db.Column(db.String(4), nullable=False, unique=False)
    course_number = db.Column(db.Integer, nullable=False, unique=False)
    name_of_class = db.Column(db.Text, nullable=False, unique=False)
    exam = db.Column(db.Boolean, unique=False, default=False)
    quiz = db.Column(db.Boolean, unique=False, default=False)
    midterm = db.Column(db.Boolean, unique=False, default=False)
    year = db.Column(db.Integer, nullable=False, unique=False)
    # 1 = Spring, 2 = Summer, 3 = Fall
    semester = db.Column(db.Integer, nullable=False, unique=False)
    backtest_number = db.Column(db.Integer, nullable=False, unique=False)  # E1 or E2
    backtest_count = db.Column(db.Integer, nullable=False, unique=False)  # quantitiy

    def __str__(self) -> str:
        if self.quiz:
            f"{self.subject_code} {self.course_number} {self.name_of_class} Quiz {self.backtest_number} {self.year} {self.semester} count: {self.backtest_count}, id: {self.id}, added {self.added}"
        elif self.exam:
            return f"{self.subject_code} {self.course_number} {self.name_of_class} Exam {self.backtest_number} {self.year} {self.semester} count: {self.backtest_count}, id: {self.id}, added {self.added}"
        return f"{self.subject_code} {self.course_number} {self.name_of_class} Midterm {self.backtest_number} {self.year} {self.semester} count: {self.backtest_count}, id: {self.id}, added {self.added}"


class Chargers(db.Model):
    __tablename__ = "chargers"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    in_office = db.Column(db.Boolean, nullable=False, unique=False)
    checked_out = db.Column(db.DateTime, nullable=False, unique=False)
    description = db.Column(db.Text, nullable=False, unique=False)
    phone_area_code = db.Column(db.Integer, nullable=True, unique=False)
    phone_middle = db.Column(db.Integer, nullable=True, unique=False)
    phone_end = db.Column(db.Integer, nullable=True, unique=False)

    def __str__(self) -> str:
        return f"Charger {self.id}, checked_out: {self.checked_out}, in office: {self.in_office}, phone: ({self.phone_area_code}){self.phone_middle}-{self.phone_end}"


class LostReports(db.Model):
    __tablename__ = "lost_reports"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    first_name = db.Column(db.String(40), nullable=False, unique=False)
    last_name = db.Column(db.String(50), nullable=False, unique=False)
    email = db.Column(db.String(100), nullable=False, unique=False)
    phone_area_code = db.Column(db.Integer, nullable=True, unique=False)
    phone_middle = db.Column(db.Integer, nullable=True, unique=False)
    phone_end = db.Column(db.Integer, nullable=True, unique=False)
    description = db.Column(db.Text, nullable=False, unique=False)
    item_type = db.Column(db.String(15), nullable=False, unique=False)
    locations = db.Column(db.Text, nullable=False, unique=False)
    date_lost = db.Column(db.Date, nullable=False, unique=False)
    date_added = db.Column(db.Date, nullable=False, unique=False)

    def __str__(self) -> str:
        return f"Lost Report {self.id}, {self.first_name} {self.last_name} {self.email} ({self.phone_area_code}){self.phone_middle}-{self.phone_end}, description: {self.description}, {self.item_type}, locations: {self.locations}, lost: {self.date_lost}, added: {self.date_added}"


class ArchivedLostReports(db.Model):
    __tablename__ = "archived_lost_reports"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    first_name = db.Column(db.String(40), nullable=False, unique=False)
    last_name = db.Column(db.String(50), nullable=False, unique=False)
    email = db.Column(db.String(100), nullable=False, unique=False)
    phone_area_code = db.Column(db.Integer, nullable=True, unique=False)
    phone_middle = db.Column(db.Integer, nullable=True, unique=False)
    phone_end = db.Column(db.Integer, nullable=True, unique=False)
    description = db.Column(db.Text, nullable=False, unique=False)
    item_type = db.Column(db.String(25), nullable=False, unique=False)
    locations = db.Column(db.Text, nullable=False, unique=False)
    date_lost = db.Column(db.Date, nullable=False, unique=False)
    date_added = db.Column(db.Date, nullable=False, unique=False)
    date_archived = db.Column(db.Date, nullable=False, unique=False)
    found = db.Column(db.Boolean, nullable=False, unique=False)
    # laf_id = db.Column(db.Integer, unique=True, nullable=True)

    def __str__(self) -> str:
        return f"Archived Lost Report {self.id}, {self.first_name} {self.last_name} {self.email} ({self.phone_area_code}){self.phone_middle}-{self.phone_end}, description: {self.description}, {self.item_type}, locations: {self.locations}, lost: {self.date_lost}, added: {self.date_added}, found: {self.found}, archived: {self.date_archived}"


# class LostItems(db.Model):
#     __tablename__ = "lost_items"
#     id = db.Column(db.Integer, primary_key=True, unique=True)
#     description = db.Column(db.Text, nullable=False, unique=False)
#     lost_report_match = db.Column(db.Integer, unique=True, nullable=True)
#     item_type = db.Column(db.String(25), nullable=False, unique=False)
#     locations = db.Column(db.Text, nullable=False, unique=False)
#     date_lost = db.Column(db.Date, nullable=False, unique=False)


# class ArchivedLostItems(db.Model):
#     __tablename__ = "archived_lost_items"
#     id = db.Column(db.Integer, primary_key=True, unique=True)
#     description = db.Column(db.Text, nullable=False, unique=False)
#     # lost_report_match = db.Column(db.Integer, unique=True, nullable=True)
#     item_type = db.Column(db.String(15), nullable=False, unique=False)
#     locations = db.Column(db.Text, nullable=False, unique=False)
#     date_lost = db.Column(db.Date, nullable=False, unique=False)
#     date_archived = db.Column(db.Date, nullable=False, unique=False)
#     found = db.Column(db.Boolean, nullable=False, unique=False)


# Metrics models
