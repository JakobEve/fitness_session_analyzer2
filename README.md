# Smart Fitness Session Analyzer
by Jakob Oliver Evensen

Student number: s385406

## Description

This program reads fitness data from CSV files: one with participants and their normal baseline values, and one file with session measurements. It checks every row for bad or missing data, skips the rows that dont pass, and analyzes the rest. For each session it compares the measurements to the participants baseline and decides how the session should be classified. Lastly, the results, a readable report, and a list of all rejected rows are saved to three output files. 

This is built on top of Assignment1. The analysis classes are basically the same. 

## Package and module design

exceptions.py - Two custom error classes, both save which field was wrong and why

loader.py - opens the CSV files, turns the text values into numbers, checks id with regex, checks value ranges, and groups the rows into sessions. If a row fails a check it gets rejected and the program just moves on to the next row

models.py - The same classes from assignment1 plus one new function `analyze_sessions`, that turns the data from loader.py into these objects and runs the analysis.¨

reporting.py - makes the text report and saves three output files

main.py - reads the command-line arguments, calls the loader and the analysis, creates the output folder, saves the reports and prints a short summary

## Class design
Participant - Represents a session participant and their personal baseline values.

Observation - Represents a single window of measurement. 

Session - Groups a Paticipant with a list of Obseration objects

SessionAnalyzer - Takes a Session and makes the full analysis, summary, baseline comparison etc.

Standalone functions: compute_summary, compare_to_baseline, detect_recovery, format_report".

Separated to fulfill the assignment as well as handling calculations and presentation independently so they could be reused and tested on their own. 


## Composition, encapsulation and custom exceptions

Composition (not changed since last assigment):

Session has a Participant and a list of Observation objects. SessionAnalyzer has a Session. Composition is used to model them because none has relationships that are "is-a". 

Encapsulation (not cahnged since last assigment):

every class stores its data in private variables so you cant directly access these from outside the class. I made get-methods instead that return the value. By doing this i ensure that the class is in control of its own data rather than other code being able to just overwrite it.

Custom exceptions:

`InvalidIdentifierError` and `InvalidRecordError` are used in `loader.py` for badly formatted ID, missing or empty field, a value that cant be turned into a number, value out of range or a session pointing to a missing participant. THey get caught in `read_participants` and `read_sessions`, where the row is rejected and the loop just continues. 

## Regular-expression validation

Participant ID - `P\d{3}`

Fitness session ID - `FIT-\d{4}-\d{3}`

Both are checked with `re.fullmatch` so that the whole string has to match and not just part of it. Normal number ranges are checked with plain < and >, not regex.


## Assumptions and classification rules

Based on the "DATA_DESCRIPTION.md" i used the following ranges for validation:

- heart_rate: 35-205 bpm

- skin_response: 0 or greater

- temperature: 25-42 C

- activity_level: 0-1

- signal_quality: 0-1 

Values below 0.5 are treated as poor signal quality and rejected. I chose 0.5 since the assignment only asks for a clearly documented rule, not a specific number

- timestamp: 0 or more

A row gets rejected if a field is missing or empty, cant be converted to a number, is outside its range, has an ID in the wrong format, or belongs to a participant that isnt in `participants.csv`. Only the first problem found in a row gets recorded, even if the row has more than one.

Classification:

Insufficient data: fewer than 3 valid observations in the session

Recovering: average heart rate in the second half of the sessionis at least 10 bpm lower than in the first half AND the overall average is still 15 bpm above baseline. 

Resting: average heart rate is within 15 bpm of baseline

Moderate activity: average heart rate is 15-45 bpm above baseline

High activity: average heart rate is more than 45 bpm above baseline


## Installation and running instructions

No third-party packages are required

```bash
git clone https://github.com/JakobEve/fitness_session_analyzer2.git
cd fitness_session_analyzer2
python main.py
```

Running the rest requires only
```bash
python tests.py
```

## Example output
Console after python main.py:
```
Accepted observations: 24
Rejected rows: 5
Sessions analyzed: 4
Created: output\analysis_summary.csv, output\analysis_report.txt, output\rejected_records.txt
```
`output/analysis_summary.csv`
```
session_id,participant_id,total_count,usable_count,classification,heart_rate_vs_baseline,explanation
FIT-2026-001,P001,6,6,resting,0.83,Heart rate is close to the participants basline
FIT-2026-002,P002,6,6,moderate activity,28.0,Heart rate is moderately elevated above baseline
FIT-2026-003,P003,6,6,high activity,69.5,heart rate is very elevated above baseline
FIT-2026-004,P001,6,6,recovering,45.17,Heart rate is falling toward baseline after elevated activity
```

`output/rejected_records.txt`:
```
fitness_sessions.csv row 26 field signal_quality: 0.34 is below 0.5
fitness_sessions.csv row 27 field signal_quality: 0.29 is below 0.5
fitness_sessions.csv row 28 field signal_quality: 0.25 is below 0.5
fitness_sessions.csv row 29 field signal_quality: 0.31 is below 0.5
fitness_sessions.csv row 30 field signal_quality: 0.28 is below 0.5
```


## Known limitations

- Only the first problem in a row gets recorded. This results in that a row with several mistakes wont show all of them.

- The program has only been tested on data provided, not real sensor data (same as last assignment)

- Classification only looks at heart rate, not activity level, skin response or temperature (same as last assignment). 