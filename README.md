# Fantasy Football Front Office AI

**Fantasy Football Front Office AI** is an AI-powered fantasy football decision platform that simulates a professional football front office.

Instead of showing only raw fantasy data, the app creates a full executive decision system with a President of Football Operations, General Manager, Head Coach, Director of Analytics, Director of Scouting, Sports Medicine Director, and Football Intelligence Director.

The Owner receives roster analysis, lineup intelligence, injury risk analysis, executive recommendations, and a final front office verdict.

## Motto

**Data Wins Championships.**

---

## Project Status

**Current Version:** Beta  
**Beta Status:** Ready for Review  
**Primary Mode:** Sleeper API + Demo Roster Mode

The current beta supports live Sleeper league connection and a curated demo roster for testing product functionality before a real fantasy draft is completed.

---

## Core Features

### Owner Dashboard

Displays the connected league, owner name, current week, roster size, starters, bench, and waiver/FAAB information.

### Owner Command Center

Provides a high-level operating summary:

- Roster status
- Lineup readiness
- Injury risk level
- Executive confidence
- Owner priority brief

### Beta Launch Readiness Panel

Shows whether the beta build is ready for review by checking:

- League connected
- Roster loaded
- Lineup intelligence active
- Injury intelligence active
- Executive reports generated
- Demo mode status

### Roster Composition Intelligence

Analyzes roster balance by position:

- QB
- RB
- WR
- TE
- K
- DEF

Generates front office readouts such as roster strengths, depth concerns, and position group insights.

### Lineup Decision Intelligence

Evaluates whether the current lineup is ready by checking:

- Open starter slots
- FLEX slot usage
- Starter injury flags
- Bench options
- Head Coach recommendation

### Injury Risk Intelligence

Reviews the roster for injury concerns and provides a Sports Medicine recommendation based on:

- Injury flags
- Questionable players
- Out / IR / Doubtful players
- Overall medical risk level

### Executive Consensus Summary

Combines all executive reports into a final owner-facing verdict with:

- Final confidence score
- Departments aligned
- Key risks
- Lead department
- Owner action plan

### Live Roster Viewer

Displays the roster in a fantasy lineup format:

- QB
- RB
- RB
- WR
- WR
- TE
- FLEX
- FLEX
- K
- DEF
- Bench

### Executive Leadership Team

Includes department-specific recommendations from:

- President of Football Operations
- General Manager
- Head Coach
- Director of Analytics
- Director of Scouting
- Sports Medicine Director
- Football Intelligence Director

Each executive report includes:

- Recommendation
- Justification
- Confidence
- Evidence
- Risks
- Departments consulted

### Player Explorer

Provides a searchable and filterable NFL player database using processed Sleeper player data.

---

## Tech Stack

- Python
- Streamlit
- Pandas
- Sleeper API
- Object-Oriented Programming
- Dataclasses
- Modular project architecture
- Git / GitHub

---

## Project Architecture

```text
fantasy-football-front-office-ai/
│
├── streamlit_app.py
│
├── data/
│   ├── raw/
│   └── processed/
│
├── src/
│   ├── brain/
│   │   ├── executive_brain.py
│   │   ├── league_aware_recommendations.py
│   │   └── recommendation.py
│   │
│   ├── executives/
│   │   ├── executive.py
│   │   ├── president.py
│   │   ├── general_manager.py
│   │   ├── head_coach.py
│   │   ├── analytics_director.py
│   │   ├── scouting_director.py
│   │   ├── medical_director.py
│   │   ├── football_intelligence.py
│   │   └── front_office.py
│   │
│   ├── integrations/
│   │   └── sleeper.py
│   │
│   ├── league/
│   │   ├── league_state.py
│   │   └── sleeper_mapper.py
│   │
│   └── meetings/
│       └── executive_meeting.py
│
├── pages/
│   ├── 1_President.py
│   ├── 2_General_Manager.py
│   ├── 3_Head_Coach.py
│   ├── 4_Director_of_Analytics.py
│   ├── 5_Director_of_Scouting.py
│   ├── 6_Sports_Medicine.py
│   └── 7_Football_Intelligence.py
│
└── tests/
```

---

## How to Run Locally

Clone the repository:

```bash
git clone https://github.com/jmerch81/fantasy-football-front-office-ai.git
cd fantasy-football-front-office-ai
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the Streamlit app:

```bash
python -m streamlit run streamlit_app.py
```

---

## Sleeper Setup

The app currently supports Sleeper league import.

In the sidebar:

1. Enter Sleeper username.
2. Select season.
3. Select league.
4. Enable demo roster if the league has not drafted yet.

Demo mode allows the beta to be tested even before a real fantasy roster exists.

---

## Current Beta Capabilities

The beta can:

- Connect to a Sleeper league
- Build a league state object
- Load a curated demo roster
- Display a fantasy lineup
- Analyze roster composition
- Analyze lineup readiness
- Analyze injury risk
- Generate executive recommendations
- Produce a final front office verdict
- Validate beta launch readiness

---

## Current Limitations

The current beta does not yet include:

- Live fantasy projections
- Weekly matchup data
- Waiver wire recommendations
- Trade analyzer
- ESPN or Yahoo integration
- User authentication
- Database persistence
- Deployed production hosting

These items are planned for future versions.

---

## Future Roadmap

### Version 1.1

- Waiver Wire Advisor
- Weekly matchup analyzer
- Start/Sit recommendation engine
- Bench optimization logic

### Version 1.2

- Trade Analyzer
- Strength of schedule analysis
- Bye week planner
- Opponent scouting report

### Version 2.0

- AI Owner Chat
- ESPN integration
- Yahoo integration
- Persistent database
- User accounts
- Cloud deployment

---

## Why This Project Matters

This project demonstrates the ability to design and build a real-world data product using Python, APIs, modular software architecture, and decision intelligence.

It combines:

- Sports analytics
- Product thinking
- Data engineering
- API integration
- AI-style recommendation systems
- Front-end dashboard development

The goal is to turn fantasy football decision-making into an explainable, executive-level intelligence system.

---

## Author

**Jeremie Merchant**  
Data Science / Analytics Portfolio Project  
GitHub: [github.com/jmerch81](https://github.com/jmerch81)

