from engine import MultipleChoice, FillCommand, ScenarioChallenge, Session, run_module

LESSON = """
  Think about the phrase "it works on my machine." Every developer has heard it.
  The root cause is environment inconsistency — your app depends on specific
  runtime versions, system libraries, and OS behavior, all of which silently
  differ between your laptop, your colleague's laptop, and the production server.
  Docker's answer: don't just ship code — ship the entire environment.
"""

CHALLENGES = [
    MultipleChoice(
        question="What is the primary problem Docker was designed to solve?",
        options=[
            "Slow internet speeds",
            "Environment inconsistency across machines",
            "Lack of programming languages",
            "Expensive cloud costs",
        ],
        correct=1,
        explanation="Apps depend on runtime versions, system libraries, and OS behavior — all of which vary between machines.",
        hint_text="Think about what changes between your laptop and the production server.",
    ),
    MultipleChoice(
        question="Which of the following is an example of 'environment drift'?",
        options=[
            "Your code has a syntax error",
            "Dev has Python 3.9 but prod has Python 3.12",
            "Your database is too slow",
            "You forgot to commit your changes",
        ],
        correct=1,
        explanation="Environment drift is when dev/staging/prod diverge over time, causing bugs that only appear in certain environments.",
        hint_text="Which option describes a difference between two machines?",
    ),
    ScenarioChallenge(
        setup="You join a new team. Their app uses libpq (a C library for Postgres). It compiles on Ubuntu 20.04 but not on your macOS. You spend 2 days debugging.",
        question="In one word, what fundamental problem does this represent?",
        accepted=["environment", "dependency", "drift", "compatibility"],
        explanation="This is environment/dependency drift — the reason Docker exists.",
        hint_text="It's the same problem Docker was invented to solve.",
    ),
    FillCommand(
        prompt="What Docker command would you run to start a container from the 'nginx' image in detached mode on port 80?",
        accepted=[
            "docker run -d -p 80:80 nginx",
            "docker run -p 80:80 -d nginx",
        ],
        explanation="-d runs detached (background), -p 80:80 maps host port 80 to container port 80.",
        hint_text="You need the -d flag and -p host:container flag.",
    ),
    MultipleChoice(
        question="Docker's solution to environment inconsistency is to:",
        options=[
            "Standardize all developers' laptops",
            "Package the app AND its environment into a portable container",
            "Run everything in the cloud",
            "Use virtual machines for every app",
        ],
        correct=1,
        explanation="Docker packages the application together with its runtime, libraries, and dependencies into a single portable unit.",
    ),
]

def run(session: Session):
    return run_module("Module 1: The Problem Docker Solves", LESSON, CHALLENGES, session)
