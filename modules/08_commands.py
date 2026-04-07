from engine import (MultipleChoice, FillCommand, ScenarioChallenge,
                     Session, run_module)

LESSON = """
  Here are the commands you'll use every day. For containers: 'docker run',
  'docker ps', 'docker logs', 'docker exec', 'docker stop', 'docker rm'.
  For Compose: 'up -d', 'down', 'logs -f', 'exec'. For housekeeping:
  'docker system prune' cleans up, 'docker system df' shows disk usage.
  Master these and you can operate any Docker environment.
"""

CHALLENGES = [
    FillCommand(
        prompt="Show all running containers.",
        accepted=["docker ps"],
        explanation="docker ps lists running containers. Add -a to see stopped ones too.",
        hint_text="It's two words: docker + a command that lists processes.",
    ),
    FillCommand(
        prompt="Show all containers including stopped ones.",
        accepted=["docker ps -a", "docker ps --all"],
        explanation="The -a (or --all) flag shows all containers, including stopped ones.",
        hint_text="Same as the previous command, but with a flag for 'all'.",
    ),
    ScenarioChallenge(
        setup="A container named 'api' is running but behaving unexpectedly. You want to look inside it — open an interactive bash shell.",
        question="What command opens a shell inside the running container?",
        accepted=["docker exec -it api bash", "docker exec -it api sh"],
        explanation="docker exec -it opens an interactive terminal inside a running container. -i keeps stdin open, -t allocates a pseudo-TTY.",
        hint_text="You need 'docker exec' with flags for interactive + TTY.",
    ),
    ScenarioChallenge(
        setup="Your server has been running Docker for months. 'df -h' shows the disk is 90% full. You suspect old images and stopped containers.",
        question="What single Docker command cleans up stopped containers, unused networks, and dangling images?",
        accepted=["docker system prune", "docker system prune -f"],
        explanation="docker system prune is the housekeeping command. Add -a to also remove all unused images. Always check docker system df first.",
        hint_text="It's under 'docker system' and it cleans/removes unused resources.",
    ),
    FillCommand(
        prompt="Follow (stream) the logs of a container named 'web'.",
        accepted=["docker logs -f web", "docker logs --follow web"],
        explanation="-f streams logs in real-time, like tail -f. Essential for debugging a running service.",
        hint_text="docker logs + a flag that means 'follow'.",
    ),
    MultipleChoice(
        question="You run 'docker compose down'. What happens?",
        options=[
            "Containers are stopped and removed; volumes are kept",
            "Only containers are paused",
            "Containers, volumes, and images are all deleted",
            "Nothing — you need sudo",
        ],
        correct=0,
        explanation="'down' stops and removes containers and networks, but keeps volumes (data is safe). Use 'down -v' to also remove volumes.",
    ),
    ScenarioChallenge(
        setup="You want to check how much disk space Docker is using — images, containers, volumes, build cache.",
        question="What command shows Docker's disk usage breakdown?",
        accepted=["docker system df", "docker system df -v"],
        explanation="docker system df shows disk usage by images, containers, local volumes, and build cache. Add -v for verbose detail.",
        hint_text="It's under 'docker system' and it's similar to the Unix 'df' command.",
    ),
]

def run(session: Session):
    return run_module("Module 8: Command Reference & Debugging", LESSON, CHALLENGES, session)
