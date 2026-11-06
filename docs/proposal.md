# Pitcher Scouting Brief Assistant

## Project goal

A scouting-brief assistant that helps a baseball hitting analyst turn an opposing pitcher's recent pitch data into a short, checkable brief of that pitcher's tendencies.

## Intended user and problem

A hitting analyst or advance scout preparing hitters for an upcoming opposing pitcher. I will demo it as preparing a brief for a team like the Dodgers; I am not affiliated with any team and will use no team data. Today the analyst pulls pitch-level data, filters it by hand for each pitcher, and writes notes in a separate document. Tendencies that changed recently are easy to miss, notes are hard to find later, and nothing records which claims were checked.

## Example input

- **Pitcher:** a starting pitcher chosen from public data
- **Date range:** the last two months of the regular season
- **Analyst note:** “Seems to throw more sliders to lefties lately.”

## Sample input set

Eight inputs. Six use real public pitch data that I download once and save as CSV files, so they never change. Two are synthetic and labeled as such. For each real input I compute the key numbers myself in a spreadsheet first, so I know the right answer before testing the app. The player names are public figures and the data is public performance data; I will not use anything non-public.

| # | Input | Real or synthetic | Expected result |
|---|---|---|---|
| 1 | Starter whose slider usage vs. left-handed batters rose by at least 10 percentage points between his first and last five starts in the range | Real, with my note | Brief has a claim stating both usage values; both match my spreadsheet; note check says the note matches the data |
| 2 | Starter with a stable pitch mix; note says “seems different lately” | Real, with my note | Brief says there is no notable change and invents no tendencies; note check says the note does not match the data |
| 3 | Reliever with enough pitches in the range | Real | Brief is produced and states that the sample is small |
| 4 | Rookie with fewer pitches than the minimum sample | Real | “Insufficient sample” message; no LLM call; nothing saved |
| 5 | Pitcher who added a new pitch type mid-season | Real | Brief flags the new pitch and the date it first appears |
| 6 | Pitcher with a gap in the range (time away from games) | Real | Brief states the gap and uses only the games present |
| 7 | Misspelled or unknown pitcher name | Synthetic | “Pitcher not found”; nothing saved |
| 8 | Copy of input 1 with the velocity column removed | Synthetic | App reports that velocity data is missing and makes no velocity claims |

How I will check the synthetic ones: input 8 is derived from real input 1 with one column deleted, so its structure matches real data. Input 7 is a made-up name in the same format as real ones.

## Expected result and value

The analyst sees a one-page brief of 3 to 5 claims, each with the numbers behind it and a way to inspect the pitches it came from. They confirm, edit, or reject each claim, and the saved brief stays available for later. Three observations would show that it improves the current work:

1. At least 90% of the claims in my real test briefs match the numbers I computed by hand.
2. No claim ships without a source.
3. The time to get a checked brief is shorter than doing the same filtering by hand in a spreadsheet.

## Big-picture sketch

Numbered areas: 1 Input, 2 Evidence (one chart plus pitch rows, not a full dashboard), 3 Draft claims to review, 4 Saved work. Open questions are marked with ?.

## Workflow or component sketch

The pitcher, date range, and analyst note go in. The app loads the pitch rows from saved CSV files; an unknown pitcher or too few pitches stops here with a message. Code computes the metrics. The metrics feed both an evidence panel and the LLM, which drafts claims. A code check drops any claim containing a number that is not in the metrics. The user confirms, edits, or rejects each claim, and the results are saved.

## Data source and access

Statcast pitch-level data from Baseball Savant, pulled with the pybaseball library. I will download the data for my chosen pitchers once and save it as CSV files, then load those into the app.

Permissions: none beyond Baseball Savant's terms of use, which I will read before downloading and which will set how I credit the source and how I limit request rates. Sensitivity: this is public performance data, not personal records. I will not use any non-public team or player data, and I will confirm with the instructors if I plan to add anything beyond public data.

## Up to three core features

1. Load a pitcher's pitch data and compute tendency metrics with exact rules, shown as an evidence panel (one chart plus the pitch rows).
2. The LLM drafts claims from the computed metrics and the analyst's note; the user confirms, edits, or rejects each one.
3. Save briefs, claims, and analyst notes, linked to the pitcher, and let the user return to and search them.

## LLM role

Read the computed metrics and the analyst's note, then draft the brief as a list of claims and say whether the note matches the data.

**Input fields:** pitcher hand, date range, metrics (pitch mix by count and batter handedness, usage per start, velocity per start, whiff rate by pitch type), and the analyst note.

**Output fields:** a list of claims, each with claim text, metric name, early and recent values, evidence rows, and confidence, plus a note-matches-data answer (yes, partly, or no).

**Limits:** the model does no arithmetic; code computes every number. A second code check rejects any claim containing a number that does not appear in the metrics.

**Initial implementation scope:** connect the existing page and `/generate` endpoint to the model using supplied metrics and the analyst note. This slice adds no retrieval (RAG) or database. Code removes any claim containing a number absent from the supplied metric values and clears model-provided evidence rows; the page labels results as unverified drafts. Pitch-row evidence will be added only when a later data and evidence feature supplies real rows.

## Data use

The app looks up the pitcher's pitch rows in the date range and compares an early window to a recent window (for example, first five starts against last five) to find changes. It also looks up earlier briefs and notes for the same pitcher.

## Saved records

Five linked kinds of records:

- **Pitcher:** name and throwing hand.
- **Pitch:** belongs to a Pitcher; game date, pitch type, velocity, batter side, count, and result.
- **Brief:** belongs to a Pitcher; date range, analyst note, and status.
- **Claim:** belongs to a Brief; text, metric, values, evidence rows from Pitch, and the user's verdict (confirmed, edited, or rejected).
- **AnalystNote:** belongs to a Pitcher and optionally to a Brief; free text and date.

All of it must survive a restart, so it lives in a database file or server, not in memory.

## Searchable text

Claim text and analyst notes, for example “pitchers who changed their approach after time away” or “notes about slider usage vs. lefties”. Meaning-based search should help because the same idea gets worded differently each time. I will compare it against keyword search later in the semester.

## Human review

Every claim is a suggestion, and nothing is saved as confirmed until the user clicks Confirm. Clicking a claim highlights the chart view and pitch rows it came from, so the user can inspect the source data. The note check is shown too, so the user can see when their own impression is not supported by the data.

## One failure case

The user asks for a pitcher with fewer than the minimum number of pitches in the range, or a name that is not found. The user sees “Insufficient sample” or “Pitcher not found”, no LLM call is made, and no Pitcher, Brief, or Claim record is created or changed. Earlier saved work is unchanged.

## Three acceptance criteria

1. Given saved data for pitcher 1 (slider usage vs. left-handed batters up at least 10 percentage points from the first five to the last five starts), when I generate a brief, then it includes a claim with both usage values, and both match the numbers I computed by hand.
2. Given I confirm one claim and reject another, when I restart the app and open Saved Work, then the pitcher, brief, confirmed claim, rejected claim (marked rejected), and analyst note are all still there and linked.
3. Given a pitcher with fewer pitches than the minimum sample in the range, when I click Generate, then I see “Insufficient sample”, no LLM call is made, and the database has the same number of records as before.

## Outside version one

- Predicting pitch outcomes or building a machine-learning model
- Batter or defense scouting (pitchers only)
- Live in-game use
- A general stats dashboard or explorer with free-form filters
- Video, biomechanics, or injury analysis
- Non-public team data
- User accounts and multiple users (single user for version one)
- Other sports

## Open questions

### Decisions I need to make

- Minimum sample size (starting guess: 150 pitches in the range).
- How to compare windows: first five against last five starts, or last 30 days against the rest.
- What counts as a meaningful change (starting guess: 10 percentage points in usage).
- Which view the evidence panel shows (starting guess: pitch mix against each batter side, plus the rows).

### Details I will learn later

Database schema, charting library, and deployment.

## Feasibility uncertainties

- **Statcast fields.** Do the downloaded columns contain what I need for the tendency rules (pitch type, velocity, batter side, balls and strikes, game date, pitch result) across a full season? Investigation: download one pitcher for one month and check the columns and counts. Evidence: a CSV with those columns filled in. If a column is missing, I drop the metric that depends on it.
- **Usefulness to an analyst.** Will an analyst find the briefs useful? Investigation: show one real brief to someone who follows baseball analytics and ask which claims they would reject. Evidence: their reasons. This could change which metrics I keep.
- **Data terms.** Do Baseball Savant's terms allow the way I will use the data in a deployed class project? Investigation: read the terms and, if unclear, ask the instructors. If not allowed, the deployed version uses a small saved sample with attribution.

## Next investigation

The biggest uncertainty is whether the pitch data has the fields I need for the tendency rules. I will use pybaseball to download one starter's pitches for one month, check that each pitch has type, velocity, batter side, count, and date, and compute pitch mix by hand in a spreadsheet. If the columns are complete, I will fix the rules and the sample input set from them. If some are missing, I will drop the metrics that depend on them (for example, whiff rate) and narrow the brief to pitch mix and velocity.
