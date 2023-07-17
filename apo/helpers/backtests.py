from collections import defaultdict

from flask import abort
from sqlalchemy import text

from apo import app, db
from apo.models import BacktestClasses, Backtests

# Constants
SUBJECT_CODE_QUERY = text("SELECT DISTINCT subject_code FROM backtest_classes")
SEMESTERS = defaultdict(str, {1: "Spring", 2: "Summer", 3: "Fall"})


def list_subject_codes() -> dict:
    subject_codes = db.session.execute(SUBJECT_CODE_QUERY).scalars()

    if subject_codes is None:
        app.logger.error("Failed to query and find subject codes")
        abort(500)

    codes = [str(code) for code in subject_codes]

    subject_code_dict = {"subject_codes": codes}

    app.logger.debug(f"Subject code list data created {subject_code_dict}")
    return subject_code_dict


def list_classes(request_data: dict) -> dict:
    if "subject_code" not in request_data:
        app.logger.debug("Missing request data to complete request")
        abort(400)

    classes = db.session.execute(
        db.select(BacktestClasses).where(
            BacktestClasses.subject_code == request_data["subject_code"].upper().strip()
        )
    ).all()

    if classes is None:
        app.logger.debug("Missing data for give subject code")
        abort(404)

    classes_dict = {}
    for bt_class in classes:
        classes_dict[bt_class.BacktestClasses.id] = {
            "name": bt_class.BacktestClasses.name_of_class,
            "course_number": bt_class.BacktestClasses.course_number,
        }

    app.logger.debug(f"classes list data created {classes_dict}")

    return classes_dict


def query_backtests(subject_code: str, course_number: int):
    bt_select = (
        db.select(Backtests)
        .where(Backtests.subject_code == subject_code)
        .where(Backtests.course_number == course_number)
        .order_by(Backtests.year.desc())
        .order_by(Backtests.semester.desc())
    )

    exams = db.session.execute(bt_select.where(Backtests.exam == True)).all()
    quizzes = db.session.execute(bt_select.where(Backtests.quiz == True)).all()
    midterms = db.session.execute(bt_select.where(Backtests.midterm == True)).all()

    app.logger.debug(f"Backtests quiered for {subject_code} {course_number}")

    return exams, quizzes, midterms


def process_backtests(bt) -> str:
    entry = f"{SEMESTERS[bt.Backtests.semester]} {bt.Backtests.year}".strip()
    bt_count = bt.Backtests.backtest_count
    if bt_count > 1:
        return entry + f" ({bt_count})"

    return entry


def backtests(request_data: dict) -> dict:
    if "subject_code" not in request_data or "course_number" not in request_data:
        app.logger.debug("Missing request data to complete request")
        abort(400)

    subject_code = request_data["subject_code"].upper().strip()
    course_number = request_data["course_number"]

    course = db.session.execute(
        db.select(BacktestClasses)
        .where(BacktestClasses.subject_code == subject_code)
        .where(BacktestClasses.course_number == course_number)
    ).first()

    if course is None:
        abort(404)

    if course.BacktestClasses.is_alias:
        subject_code = course.BacktestClasses.alias_subject_code
        course_number = course.BacktestClasses.alias_course_number

    exams, quizzes, midterms = query_backtests(subject_code, course_number)

    if exams is None and quizzes is None and midterms is None:
        abort(404)

    backtest_exams, backtest_quizzes, backtest_midterms = (
        defaultdict(list),
        defaultdict(list),
        defaultdict(list),
    )
    if exams is not None:
        for exam in exams:
            entry = process_backtests(exam)
            backtest_exams[exam.Backtests.backtest_number].append(entry)

    if quizzes is not None:
        for quiz in quizzes:
            entry = process_backtests(quiz)
            backtest_quizzes[quiz.Backtests.backtest_number].append(entry)

    if midterms is not None:
        for midterm in midterms:
            entry = process_backtests(midterm)
            backtest_midterms[midterm.Backtests.backtest_number].append(entry)

    app.logger.debug(
        f"Backtest response created exams: {backtest_exams}, quizzes: {backtest_quizzes}, midterms: {backtest_midterms}"
    )

    return {
        "exams": backtest_exams,
        "quizzes": backtest_quizzes,
        "midterms": backtest_midterms,
    }
