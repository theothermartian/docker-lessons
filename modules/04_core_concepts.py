from engine import (MultipleChoice, FillCommand, ScenarioChallenge,
                     SpotTheBug, LiveExecution, Session, run_module)

LESSON = """
  An image is a read-only blueprint — think of it as a class in OOP. A container
  is a running instance — an object created from that class. Images are built from
  layers: each instruction in a Dockerfile creates an immutable filesystem diff
  stacked on top of the previous one. Volumes persist data beyond the container's
  lifetime. Networks let containers discover and talk to each other by name.
"""

CHALLENGES = [
    MultipleChoice(
        question="In OOP terms, a Docker image is to a container as a ___ is to an object.",
        options=["Module", "Function", "Class", "Variable"],
        correct=2,
        explanation="An image is a blueprint (class); a container is a running instance (object). You can create many containers from one image.",
        hint_text="Think about blueprints and instances.",
    ),
    SpotTheBug(
        code_block="""\
FROM python:3.12-slim
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["python", "app.py"]""",
        question="What is wrong with the layer order in this Dockerfile, and what is the performance consequence?",
        accepted_keywords=["copy", "requirements", "cache", "layer", "order", "pip"],
        explanation="COPY . . copies ALL source code before installing dependencies. Every source change invalidates the pip install cache layer. Fix: COPY requirements.txt first, RUN pip install, THEN COPY the rest.",
        hint_text="Which line should come before which? Think about what changes more often.",
    ),
    ScenarioChallenge(
        setup="You run a Postgres database container for your app. After a week, you stop and remove the container. All your data is gone.",
        question="What Docker feature should you have used to persist the database data?",
        accepted=["volume", "volumes", "-v", "named volume", "bind mount"],
        explanation="Containers are ephemeral — data written inside them disappears when removed. Volumes mount a persistent directory: docker run -v pgdata:/var/lib/postgresql/data postgres:16",
        hint_text="Data inside a container is ephemeral. What feature makes it persistent?",
    ),
    FillCommand(
        prompt="Your 'web' container needs to communicate with a 'db' container. Create a Docker network called 'app-net'.",
        accepted=["docker network create app-net"],
        explanation="Containers are network-isolated by default. Creating a shared network lets them reach each other by container name as hostname.",
        hint_text="The command starts with 'docker network'.",
    ),
    ScenarioChallenge(
        setup="You're developing a Python app in a container. You want to edit code on your laptop and see changes reflected instantly inside the container without rebuilding the image.",
        question="What type of volume should you use, and roughly what does the command look like?",
        accepted=["bind mount", "bind", "-v /path:/app", "mount"],
        explanation="A bind mount maps a host directory directly into the container: docker run -v /your/code:/app myapp. Changes on the host appear instantly inside the container.",
        hint_text="It maps a host directory directly into the container filesystem.",
    ),
    LiveExecution(
        prompt="Run the hello-world container to verify your Docker install works.",
        command_to_run="docker run hello-world",
        success_substring="Hello from Docker",
        explanation="The hello-world image prints a confirmation message if Docker is installed and working correctly.",
    ),
]

def run(session: Session):
    return run_module("Module 4: Core Concepts", LESSON, CHALLENGES, session)
