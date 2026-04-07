from engine import (MultipleChoice, FillCommand, ScenarioChallenge,
                     SpotTheBug, Session, run_module)

LESSON = """
  Real-world apps aren't a single container — they're a web server, a database,
  a cache, a worker, and more. Docker Compose lets you define your entire stack
  in one YAML file. Run 'docker compose up' and everything starts together.
  Services find each other by name. 'depends_on' controls startup order.
  One file, one command, full stack.
"""

CHALLENGES = [
    MultipleChoice(
        question="What is the main advantage of Docker Compose over running multiple 'docker run' commands?",
        options=[
            "It's faster to type",
            "It defines the entire stack declaratively in one file, ensuring consistency",
            "It uses less memory",
            "It automatically deploys to AWS",
        ],
        correct=1,
        explanation="Compose captures your entire multi-service architecture in a single declarative file — reproducible by anyone with one command.",
    ),
    SpotTheBug(
        code_block="""\
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgres://user:pass@db:5432/mydb

  db:
    image: postgres:16
    environment:
      - POSTGRES_PASSWORD=pass
      - POSTGRES_USER=user
      - POSTGRES_DB=mydb""",
        question="The web service crashes on startup because it can't connect to the database. What's missing?",
        accepted_keywords=["depends_on", "depends", "startup order", "order"],
        explanation="Without depends_on: [db] in the web service, both containers start simultaneously. The web app tries to connect before Postgres is ready.",
        hint_text="What controls which service starts first?",
    ),
    FillCommand(
        prompt="Start all services defined in docker-compose.yml in the background.",
        accepted=["docker compose up -d", "docker-compose up -d"],
        explanation="-d runs in detached mode (background). Without it, logs stream to your terminal.",
        hint_text="You need the 'up' subcommand and a flag for background mode.",
    ),
    ScenarioChallenge(
        setup="A new engineer joins your team. They've never worked on this project. Your stack has a web server, Postgres database, Redis cache, and a background worker.",
        question="What single file should they check out from git, and what single command starts everything?",
        accepted=["docker-compose.yml", "compose up", "docker compose up", "docker-compose up"],
        explanation="docker-compose.yml (or compose.yaml) defines the whole stack. 'docker compose up' starts all services. New engineer is productive in seconds, not days.",
        hint_text="It's a YAML file that defines the whole stack.",
    ),
    ScenarioChallenge(
        setup="You want to completely tear down your Compose stack AND delete all the database data stored in volumes (you're resetting to a clean state).",
        question="What command tears down containers AND removes volumes?",
        accepted=["docker compose down -v", "docker-compose down -v"],
        explanation="'docker compose down' stops and removes containers but keeps volumes. The -v flag also removes named volumes — deleting their data. Use with care.",
        hint_text="You need the 'down' subcommand plus a flag for volumes.",
    ),
    MultipleChoice(
        question="In a Compose file, how does the 'web' service connect to the 'db' service by hostname?",
        options=[
            "Using the container ID",
            "Using the service name 'db' as the hostname",
            "Using localhost",
            "Using the host machine's IP",
        ],
        correct=1,
        explanation="Compose automatically creates a network where each service is reachable by its service name as a DNS hostname.",
    ),
]

def run(session: Session):
    return run_module("Module 5: Docker Compose", LESSON, CHALLENGES, session)
