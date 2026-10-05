import csv
import math
import re
from pathlib import Path

from fitness_analyzer.exceptions import InvalidIdentifierError, InvalidRecordError
from fitness_analyzer.models import Participant

PARTICIPANT_ID_PATTERN = r"P\d{3}"
SESSION_ID_PATTERN = r"FIT-\d{4}-\d{3}"
PARTICIPANT_FIELDS = ("participant_id", "name", "baseline_heart_rate", "baseline_skin_response", "baseline_temperature")
SESSION_FIELDS = ("session_id", "participant_id", "timestamp", "heart_rate", "skin_response", "temperature", "activity_level", "signal_quality")
VALUE_RANGES = {
    "timestamp": (0, math.inf),
    "heart_rate": (35, 205),
    "skin_response": (0, math.inf),
    "temperature": (25, 42),
    "activity_level": (0, 1),
    "signal_quality": (0, 1),
}
MINIMUM_SIGNAL_QUALITY = 0.5


def read_rows(path):
    try:
        with open(path, encoding="utf-8", newline="") as file:
            return list(csv.DictReader(file))
    except FileNotFoundError as error:
        raise FileNotFoundError(f"Input file not found: {path}") from error
    except PermissionError as error:
        raise PermissionError(f"Cannot read input file: {path}") from error
    except csv.Error as error:
        raise ValueError(f"CSV error in {path}: {error}") from error


def read_participants(path):
    participants={}
    rejected=[]
    for row_number, row in enumerate(read_rows(path),start=2):
        try:
            profile=convert_participant(row)
            participants[profile["participant_id"]]=create_participant(profile)
        except (InvalidRecordError, InvalidIdentifierError) as error:
            rejected.append(make_rejection(path,row_number,error))
    return participants, rejected


def read_sessions(path,participants):
    sessions={}
    rejected=[]
    for row_number, row in enumerate(read_rows(path),start=2):
        try:
            observation=convert_session(row)
            if observation["participant_id"] not in participants:
                raise InvalidRecordError("participant_id",f"unknown participant '{observation['participant_id']}'")
            session=sessions.setdefault(
                observation["session_id"],
                {"participant_id": observation["participant_id"], "observations": []},
            )
            session["observations"].append(observation)
        except (InvalidRecordError, InvalidIdentifierError) as error:
            rejected.append(make_rejection(path,row_number,error))
    return sessions, rejected


def convert_participant(row):
    check_row_shape(row, PARTICIPANT_FIELDS)
    return {
        "participant_id": validate_identifier(row["participant_id"], PARTICIPANT_ID_PATTERN, "participant_id"),
        "name": row["name"],
        "baseline_heart_rate": to_number(row, "baseline_heart_rate", int),
        "baseline_skin_response": to_number(row, "baseline_skin_response", float),
        "baseline_temperature": to_number(row, "baseline_temperature", float),
    }


def convert_session(row):
    check_row_shape(row, SESSION_FIELDS)
    session = {
        "session_id": validate_identifier(row["session_id"], SESSION_ID_PATTERN, "session_id"),
        "participant_id": validate_identifier(row["participant_id"], PARTICIPANT_ID_PATTERN, "participant_id"),
        "timestamp": to_number(row, "timestamp", int),
        "heart_rate": to_number(row, "heart_rate", int),
        "skin_response": to_number(row, "skin_response", float),
        "temperature": to_number(row, "temperature", float),
        "activity_level": to_number(row, "activity_level", float),
        "signal_quality": to_number(row, "signal_quality", float),
    }
    for field in VALUE_RANGES:
        check_range(session, field)
    if session["signal_quality"] < MINIMUM_SIGNAL_QUALITY:
        raise InvalidRecordError("signal_quality", f"{session['signal_quality']} is below {MINIMUM_SIGNAL_QUALITY}")
    return session


def create_participant(profile):
    try:
        return Participant.from_profile_dict(profile)
    except ValueError as error:
        raise InvalidRecordError("baseline", str(error)) from error


def check_row_shape(row, fields):
    for field in fields:
        if row.get(field) is None:
            raise InvalidRecordError(field, "missing value or row is too short")
        if row[field].strip() == "":
            raise InvalidRecordError(field, "empty value")
    if None in row:
        raise InvalidRecordError("row", "row has more values than the header")


def validate_identifier(value, pattern, field):
    if not re.fullmatch(pattern, value):
        raise InvalidIdentifierError(field, f"'{value}' does not match {pattern}")
    return value


def to_number(row, field, converter):
    try:
        return converter(row[field])
    except ValueError:
        raise InvalidRecordError(field, f"'{row[field]}' is not a valid number")


def check_range(session, field):
    lower, upper = VALUE_RANGES[field]
    value = session[field]
    if not lower <= value <= upper:
        raise InvalidRecordError(field, f"{value} is outside the allowed range {lower}-{upper}")


def make_rejection(path, row_number, error):
    return {
        "source": Path(path).name,
        "row": row_number,
        "field": error.field,
        "reason": error.reason,
    }
