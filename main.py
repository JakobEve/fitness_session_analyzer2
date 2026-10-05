import argparse
from pathlib import Path

from fitness_analyzer.loader import read_participants, read_sessions
from fitness_analyzer.models import analyze_sessions
from fitness_analyzer.reporting import write_rejections_txt, write_report_txt, write_summary_csv


def parse_args():
    parser = argparse.ArgumentParser(description="Analyze fitness sessions from CSV files.")
    parser.add_argument("--profiles", default="data/participants.csv", help="participant CSV file")
    parser.add_argument("--sessions", default="data/fitness_sessions.csv", help="session CSV file")
    parser.add_argument("--output", default="output", help="output directory")
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        participants, participant_rejections = read_participants(args.profiles)
        sessions, session_rejections = read_sessions(args.sessions, participants)
    except (FileNotFoundError, PermissionError, ValueError) as error:
        print(f"Error: {error}")
        return 1

    results = analyze_sessions(sessions, participants)
    rejected = participant_rejections + session_rejections
    accepted_count = sum(len(data["observations"]) for data in sessions.values())

    output_dir = Path(args.output)
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        write_summary_csv(results, output_dir / "analysis_summary.csv")
        write_report_txt(results, output_dir / "analysis_report.txt")
        write_rejections_txt(rejected, output_dir / "rejected_records.txt")
    except PermissionError as error:
        print(f"Error: cannot write to {output_dir}: {error}")
        return 1

    print(f"Accepted observations: {accepted_count}")
    print(f"Rejected rows: {len(rejected)}")
    print(f"Sessions analyzed: {len(results)}")
    print(f"Created: {output_dir / 'analysis_summary.csv'}, {output_dir / 'analysis_report.txt'}, {output_dir / 'rejected_records.txt'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
