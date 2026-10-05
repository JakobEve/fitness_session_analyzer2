import unittest
from pathlib import Path

from fitness_analyzer.exceptions import InvalidRecordError
from fitness_analyzer.loader import convert_session, read_participants, read_sessions
from fitness_analyzer.models import Observation

DATA = Path(__file__).parent / "data"

VALID_SESSION_ROW = {
    "session_id": "FIT-2026-001",
    "participant_id": "P001",
    "timestamp": "0",
    "heart_rate": "70",
    "skin_response": "1.2",
    "temperature": "32.4",
    "activity_level": "0.1",
    "signal_quality": "0.5",
}


class TestFitnessAnalyzer(unittest.TestCase):

    def test_valid_participants_file_is_accepted(self):
        participants, rejected = read_participants(DATA / "participants.csv")
        self.assertEqual(len(rejected), 0)
        self.assertEqual(len(participants), 3)

    def test_invalid_file_rejects_bad_rows(self):
        participants, _ = read_participants(DATA / "participants.csv")
        _, rejected = read_sessions(DATA / "fitness_sessions_invalid.csv", participants)
        self.assertEqual(len(rejected), 10)

    def test_missing_file_raises_error(self):
        with self.assertRaises(FileNotFoundError):
            read_participants(DATA / "does_not_exist.csv")

    def test_signal_quality_at_minimum_is_accepted(self):
        session = convert_session(VALID_SESSION_ROW)
        self.assertEqual(session["signal_quality"], 0.5)

    def test_signal_quality_just_below_minimum_is_rejected(self):
        bad_row = dict(VALID_SESSION_ROW, signal_quality="0.49")
        with self.assertRaises(InvalidRecordError):
            convert_session(bad_row)

    def test_observation_with_missing_heart_rate_is_invalid(self):
        observation = Observation(0, None, 1.5, 32.0, 0.2, 0.9)
        self.assertFalse(observation.get_is_valid())


if __name__ == "__main__":
    unittest.main()
