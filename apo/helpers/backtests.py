from collections import defaultdict

from flask import make_response
from sqlalchemy import text

from apo import app, db
from apo.models import Backtest, BacktestClasses


def list_subject_codes():
    subject_codes = db.session.execute(
        text("SELECT DISTINCT subject_code FROM backtest_classes")
    ).all()

    if subject_codes is None:
        app.logger.error("Failed to query and find subject codes")
        abort(500)

    codes = []
    for code in subject_codes:
        codes.append(code[0])

    subject_code_dict = {"subject_codes": list(set(codes))}

    app.logger.debug(f"subject code list data created {subject_code_dict}")
    return subject_code_dict


def list_classes(request_data):
    if "subject_code" not in request_data:
        return make_response({"response": f"requires subject_code"}, 400)

    classes = db.session.execute(
        db.select(BacktestClasses).where(
            BacktestClasses.subject_code == request_data["subject_code"].upper()
        )
    ).all()

    if classes is None:
        abort(404)

    classes_dict = {}
    for bt_class in classes:
        classes_dict[bt_class.BacktestClasses.id] = {
            "name": bt_class.BacktestClasses.name_of_class,
            "course_number": bt_class.BacktestClasses.course_number,
        }

    app.logger.debug(f"classes list data created {classes_dict}")

    return make_response(classes_dict, 200)


def process_backtests(bt):
    semesters = defaultdict(lambda: "", {1: "Spring", 2: "Summer", 3: "Fall"})

    entry = f"{semesters[bt.Backtest.semester]} {bt.Backtest.year}".strip()
    bt_count = bt.Backtest.backtest_count
    if bt_count > 1:
        return entry + f" ({bt_count})"

    return entry


def backtests(request_data):
    if "subject_code" not in request_data or "course_number" not in request_data:
        return make_response(
            {"response": f"requires subject_code and course_number"}, 400
        )

    subject_code = request_data["subject_code"].upper()
    course_number = request_data["course_number"]

    bt_select = (
        db.select(Backtest)
        .where(Backtest.subject_code == subject_code)
        .where(Backtest.course_number == course_number)
        .order_by(Backtest.year.desc())
        .order_by(Backtest.semester.desc())
    )

    exams = db.session.execute(bt_select.where(Backtest.exam == True)).all()
    quizzes = db.session.execute(bt_select.where(Backtest.quiz == True)).all()
    midterms = db.session.execute(bt_select.where(Backtest.midterm == True)).all()

    app.logger.debug(f"Backtests quiered for {subject_code} {course_number}")

    if exams is None and quizzes is None and midterms is None:
        abort(404)

    backtest_exams = defaultdict(list)
    if exams is not None:
        for exam in exams:
            entry = process_backtests(exam)
            backtest_exams[exam.Backtest.backtest_number].append(entry)

    backtest_quizzes = defaultdict(list)
    if quizzes is not None:
        for quiz in quizzes:
            entry = process_backtests(quiz)
            backtest_quizzes[quiz.Backtest.backtest_number].append(entry)

    backtest_midterms = defaultdict(list)
    if midterms is not None:
        for midterm in midterms:
            entry = process_backtests(midterm)
            backtest_midterms[midterm.Backtest.backtest_number].append(entry)

    app.logger.debug(
        f"Backtest response created exams: {backtest_exams}, quizzes: {backtest_quizzes}, midterms: {backtest_midterms}"
    )

    return make_response(
        dict(
            exams=backtest_exams, quizzes=backtest_quizzes, midterms=backtest_midterms
        ),
        200,
    )
