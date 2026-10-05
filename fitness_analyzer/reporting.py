import csv

SUMMARY_FIELDS = (
    "session_id",
    "participant_id",
    "total_count",
    "usable_count",
    "classification",
    "heart_rate_vs_baseline",
    "explanation",
)


def format_report(result):
    lines=[]
    lines.append("---- Session Report ----")
    lines.append(f"Participant: {result['participant_id']}")
    lines.append(f"Usable observations: {result['usable_count']} of {result['total_count']}")
    lines.append(f"Classification: {result['classification']}")
    lines.append(f"Explanation: {result['explanation']}")
    return "\n".join(lines)


def write_summary_csv(results, path):
    with open(path, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=SUMMARY_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for result in results:
            writer.writerow(result)


def write_report_txt(results, path):
    with open(path, "w", encoding="utf-8") as file:
        for result in results:
            file.write(f"Session: {result['session_id']}\n")
            file.write(format_report(result) + "\n\n")


def write_rejections_txt(rejected, path):
    with open(path, "w", encoding="utf-8") as file:
        for item in rejected:
            file.write(f"{item['source']} row {item['row']} field {item['field']}: {item['reason']}\n")
