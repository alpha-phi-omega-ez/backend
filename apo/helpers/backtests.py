from apo import app, db
from apo.models import Backtest, BacktestClasses

from flask import make_response
from sqlalchemy import text


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


def backtests(request_data):
    if "subject_code" not in request_data or "course_number" not in request_data:
        return make_response(
            {"response": f"requires subject_code and course_number"}, 400
        )
    
    subject_code = request_data["subject_code"].upper()
    course_number = request_data["course_number"]

    exams = db.session.execute(
        db.select(Backtest)
        .where(Backtest.subject_code == subject_code)
        .where(Backtest.course_number == course_number)
        .where(Backtest.exam == True)
    ).all()
    quizzes = db.session.execute(
        db.select(Backtest)
        .where(Backtest.subject_code == subject_code)
        .where(Backtest.course_number == course_number)
        .where(Backtest.quiz == True)
    ).all()
    midterms = db.session.execute(
        db.select(Backtest)
        .where(Backtest.subject_code == subject_code)
        .where(Backtest.course_number == course_number)
        .where(Backtest.midterm == True)
    ).all()

    app.logger.debug(f"Backtests quiered for {subject_code} {course_number}")

    if exams is None and quizzes is None and midterms is None:
        abort(404)

    if exams is not None:
        exams = sorted(
            exams, key=lambda x: (x.Backtest.year, x.Backtest.semester), reverse=True
        )
    if quizzes is not None:
        quizzes = sorted(
            quizzes, key=lambda x: (x.Backtest.year, x.Backtest.semester), reverse=True
        )
    if midterms is not None:
        midterms = sorted(
            midterms, key=lambda x: (x.Backtest.year, x.Backtest.semester), reverse=True
        )
    
    app.logger.debug(f"Backtests sorted for {subject_code} {course_number}")

    backtest_exams = {}
    if exams is not None:
        for exam in exams:
            semester = "Fall"
            if exam.Backtest.semester == 1:
                semester = "Spring"
            elif exam.Backtest.semester == 2:
                semester = "Summer"

            entry = f"{semester} {exam.Backtest.year}"
            if exam.Backtest.backtest_count > 1:
                entry += f" ({exam.Backtest.backtest_count})"

            if exam.Backtest.backtest_number in backtest_exams:
                backtest_exams[exam.Backtest.backtest_number].append(entry)
            else:
                backtest_exams[exam.Backtest.backtest_number] = [entry]

    backtest_quizzes = {}
    if quizzes is not None:
        for quiz in quizzes:
            semester = "Fall"
            if quiz.Backtest.semester == 1:
                semester = "Spring"
            elif quiz.Backtest.semester == 2:
                semester = "Summer"

            entry = f"{semester} {quiz.Backtest.year}"
            if quiz.Backtest.backtest_count > 1:
                entry += f" ({quiz.Backtest.backtest_count})"

            if quiz.Backtest.backtest_number in backtest_quizzes:
                backtest_quizzes[quiz.Backtest.backtest_number].append(entry)
            else:
                backtest_quizzes[quiz.Backtest.backtest_number] = [entry]

    backtest_midterms = {}
    if midterms is not None:
        for midterm in midterms:
            semester = "Fall"
            if midterm.Backtest.semester == 1:
                semester = "Spring"
            elif midterm.Backtest.semester == 2:
                semester = "Summer"

            entry = f"{semester} {midterm.Backtest.year}"
            if midterm.Backtest.backtest_count > 1:
                entry += f" ({midterm.Backtest.backtest_count})"

            if midterm.Backtest.backtest_number in backtest_midterms:
                backtest_midterms[midterm.Backtest.backtest_number].append(entry)
            else:
                backtest_midterms[midterm.Backtest.backtest_number] = [entry]
    
    app.logger.debug(f"Backtest response created exams: {backtest_exams}, quizzes: {backtest_quizzes}, midterms: {backtest_midterms}")

    return make_response(
        {"exams": backtest_exams, "quizzes": backtest_quizzes, "midterms": backtest_midterms}, 200
    )
