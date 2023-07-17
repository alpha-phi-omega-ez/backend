import sys
import random
from datetime import datetime, date, timezone

from apo import app, db
from apo.models import *

if len(sys.argv) < 2:
    sys.exit("No argument or exsisting argument found")

if sys.argv[1] == "clear":
    with app.app_context():
        db.drop_all()

elif sys.argv[1] == "create":
    with app.app_context():
        db.create_all()

        courses = (
            ("CSCI", 1100, "Computer Science I"),
            ("CSCI", 1200, "Data Structures"),
            ("CSCI", 2200, "FOCS"),
            ("CSCI", 2500, "Computer Organizations"),
            ("CSCI", 2300, "Intro to Algo"),
            ("CSCI", 2500, "Principals of Software"),
            ("CSCI", 4210, "Operating Systems"),
        )

        for bt_class in courses:
            print(f"Added {bt_class[0]} {bt_class[1]} {bt_class[2]}")
            new_backtest_class = BacktestClasses(
                subject_code=bt_class[0],
                course_number=bt_class[1],
                name_of_class=bt_class[2],
                is_alias=False,
            )

            db.session.add(new_backtest_class)
            db.session.commit()

        courses2 = (
            ("MATH", 1010, "Calculus I"),
            ("MATH", 1020, "Calculus II"),
            ("MATH", 2010, "Multivariable Calculus"),
            ("MATH", 2400, "Differential Equations"),
        )

        for bt_class in courses2:
            print(f"Added {bt_class[0]} {bt_class[1]} {bt_class[2]}")
            new_backtest_class = BacktestClasses(
                subject_code=bt_class[0],
                course_number=bt_class[1],
                name_of_class=bt_class[2],
                is_alias=False,
            )

            db.session.add(new_backtest_class)
            db.session.commit()
        
        exam_type = (
                        "exam",
                        "quiz",
                        "midterm",
                        "exam",
                        "exam",
                        "quiz",
                        "quiz",
                        "quiz",
                        "quiz",
                        "quiz",
                    )
        
        exam_years = (
                            2016,
                            2017,
                            2018,
                            2019,
                            2020,
                            2021,
                            2022,
                            2023,
                        )

        for bt_class in courses:
            for j in range(0, 20):
                bt_type = random.choice(exam_type)
                exam = False
                quiz = False
                midterm = False
                if bt_type == "exam":
                    exam = True
                elif bt_type == "quiz":
                    quiz = True
                else:
                    midterm = True

                bt = Backtests(
                    subject_code=bt_class[0],
                    added=date.today(),
                    course_number=bt_class[1],
                    name_of_class=bt_class[2],
                    exam=exam,
                    quiz=quiz,
                    midterm=midterm,
                    year=random.choice(exam_years),
                    semester=random.choice([1, 2, 3]),
                    backtest_number=random.choice([1, 2, 3, 4, 5, 6]),
                    backtest_count=random.choice([1, 2, 3]),
                )

                db.session.add(bt)
                db.session.commit()

        for bt_class in courses2:
            for j in range(0, 20):
                bt_type = random.choice(exam_type)
                exam = False
                quiz = False
                midterm = False
                if bt_type == "exam":
                    exam = True
                elif bt_type == "quiz":
                    quiz = True
                else:
                    midterm = True

                bt = Backtests(
                    subject_code=bt_class[0],
                    added=date.today(),
                    course_number=bt_class[1],
                    name_of_class=bt_class[2],
                    exam=exam,
                    quiz=quiz,
                    midterm=midterm,
                    year=random.choice(exam_years),
                    semester=random.choice([1, 2, 3]),
                    backtest_number=random.choice((1, 2, 3, 4, 5, 6)),
                    backtest_count=random.choice((1, 2, 3)),
                )

                db.session.add(bt)
                db.session.commit()

        chargers = (
            "usb c macbook charger",
            "magsafe macbook charger",
            "lenovo charger",
            "hp charger",
            "iphone lightning charger",
        )

        for charger in chargers:
            print(f"Added {charger}")
            new_charger = Chargers(
                in_office=True,
                checked_out=datetime.now(timezone.utc),
                description=charger,
                phone_area_code=None,
                phone_middle=None,
                phone_end=None,
            )

            db.session.add(new_charger)
            db.session.commit()

        lost_reports = (
            ("Alfred", "Glump", "glump@rpi.edu", 518, 276, 6516, "teal hand made glump with wood peg foot", "Miscellaneous", "Union"),
            ("Dean Arno", "Nowotny", "nowotny@rpi.edu", 518, 276, 6516, "the greatest service program", "Umbrella", "Union,DCC,JEC"),
            ("Josiah", "Frank", "frank@rpi.edu", 518, 276, 6516, "the history of apo", "Apparel", "Westhall,Folsom Library"),
            ("M. R.", "Disborough", "disborough@rpi.edu", 518, 276, 6516, "scouting", "Waterbottle", "Union,DCC,JEC,West hall,Folsom Library,MRC,SLL,RSDH,Commons,Sage,Walker"),
        )

        for report in lost_reports:
            print(f"Added {report}")
            new_lost_report = LostReports(
                first_name=report[0],
                last_name=report[1],
                email=report[2],
                phone_area_code=report[3],
                phone_middle=report[4],
                phone_end=report[5],
                description=report[6],
                item_type=report[7],
                locations=report[8],
                date_lost=date.today(),
                date_added=date.today(),
            )

            db.session.add(new_lost_report)
            db.session.commit()
else:
    sys.exit("No argument or existing argument found")
