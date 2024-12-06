from server.database import database
from typing import List
from datetime import datetime, timedelta

backtest_course_code_collection = database.get_collection(
    "backtest_course_code_collection"
)
backtest_courses_collection = database.get_collection("backtest_courses_collection")
backtest_collection = database.get_collection("backtest_collection")

course_code_cache = {"datetime": datetime(1970, 1, 1), "data": []}
courses_cache = {}
backtest_cache = {}


def course_helper(course) -> dict:
    return {
        "id": course["_id"],
        "name": course["name"],
    }


# Retrieve all course codes present in the database
async def retrieve_coursecodes() -> List[str]:
    return ["BIOL", "CSCI", "MATH", "PHYS", "PSYC"]
    if course_code_cache["datetime"] > datetime.now() - timedelta(hours=24):
        return course_code_cache["data"]
    course_codes = []
    async for course_code in backtest_course_code_collection.find():
        course_codes.append(course_code["code"])
    
    course_code_cache["datetime"] = datetime.now()
    course_code_cache["data"] = course_codes
    return course_codes


async def retrieve_courses(course_code: str) -> List[dict]:
    if course_code == "BIOL":
        return [
            {"id": "1", "name": "1010 Introduction to Biology"},
            {"id": "2", "name": "1050 Introduction to Biology Lab"},
        ]
    elif course_code == "CSCI":
        return [
            {"id": "3", "name": "1100 Computer Science 1"},
            {"id": "4", "name": "1200 Data Structures"},
        ]
    elif course_code == "MATH":
        return [
            {"id": "5", "name": "1010 Calculus 1"},
            {"id": "6", "name": "1020 Calculus 2"},
        ]
    elif course_code == "PHYS":
        return [
            {"id": "7", "name": "1010 Physics 1"},
            {"id": "8", "name": "1020 Physics 2"},
            {
                "id": "9",
                "name": "9999 This class has an absurdly long name because RPI is stupid sometimes",
            },
        ]
    return []
    if courses_cache.get(course_code) and courses_cache[course_code]["datetime"] > datetime.now() - timedelta(hours=24):
        return courses_cache[course_code]["data"]
    courses = []
    async for course in backtest_courses_collection.find({"code": course_code}):
        courses.append(course_helper(course))
    
    courses_cache[course_code] = {"datetime": datetime.now(), "data": courses}
    return courses


async def retrieve_backtest(backtest_id: str) -> List[dict]:
    return [
        {"type": "quiz 1", "tests": ["Fall 2019", "Spring 2022", "Fall 2024"]},
        {"type": "quiz 2", "tests": ["Fall 2019", "Spring 2023", "Fall 2024"]},
        {"type": "quiz 3", "tests": ["Fall 2020", "Spring 2022", "Fall 2024"]},
        {"type": "exam 2", "tests": ["Fall 2019", "Fall 2022", "Fall 2024"]},
        {"type": "exam 3", "tests": ["Fall 2019", "Fall 2022", "Fall 2024"]},
    ]
    if backtest_cache.get(backtest_id) and courses_cache[backtest_id]["datetime"] > datetime.now() - timedelta(hours=24):
        return courses_cache[backtest_id]["data"]
    backtest = await backtest_collection.find_one({"_id": backtest_id})
    if backtest:
        backtest_response = backtest["tests"]
        backtest_cache[backtest_id] = {"datetime": datetime.now(), "data": backtest_response}
        return backtest_response
    return []
