from engine import MultipleChoice, ScenarioChallenge, Session, run_module

LESSON = """
  Docker isn't just a dev tool — it's infrastructure. CI/CD pipelines run tests
  inside containers for reproducibility. Netflix, Uber, and Amazon decompose apps
  into containerized microservices. ML teams ship training environments as Docker
  images. Even 'serverless' cloud functions like AWS Lambda run your code in
  containers under the hood.
"""

CHALLENGES = [
    MultipleChoice(
        question="Why do CI/CD pipelines (GitHub Actions, GitLab CI) run jobs inside Docker containers?",
        options=[
            "Because containers are required by law",
            "To ensure test environments are identical to production, eliminating 'passed tests but failed in prod'",
            "Because it's cheaper",
            "To avoid writing YAML",
        ],
        correct=1,
        explanation="Containers guarantee the CI environment matches production — same OS, same libraries, same versions. No more 'tests passed locally but failed in prod'.",
    ),
    ScenarioChallenge(
        setup="Your ML team trained a model on a machine with Python 3.10, PyTorch 2.1, and CUDA 11.8. A colleague can't reproduce the results on their machine.",
        question="What should the team have done to guarantee reproducibility?",
        accepted=["docker", "container", "dockerfile", "image"],
        explanation="Package the training environment in a Docker image — FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime. Anyone with Docker can reproduce the exact environment.",
        hint_text="Ship the environment, not just the code.",
    ),
    MultipleChoice(
        question="Companies like Netflix and Uber decomposed their apps into hundreds of small independent services. Each service runs in its own container. This architecture is called:",
        options=[
            "Monolithic architecture",
            "Serverless",
            "Microservices",
            "Peer-to-peer",
        ],
        correct=2,
        explanation="Microservices architecture = many small, independently deployable services, each running in its own container.",
    ),
    ScenarioChallenge(
        setup="Your company runs AWS Lambda functions. Under the hood, AWS executes your code in an isolated environment.",
        question="What technology does AWS Lambda actually use to isolate and run your function?",
        accepted=["container", "containers", "docker", "firecracker", "microvm"],
        explanation="AWS Lambda runs each function invocation in a container (specifically a microVM using Firecracker). Understanding Docker means understanding the cloud.",
        hint_text="Even 'serverless' isn't truly server-less — something runs your code.",
    ),
    MultipleChoice(
        question="A team ships a docker-compose.yml with their repo instead of a 20-page setup guide. A new engineer runs 'docker compose up'. What is the expected result?",
        options=[
            "An error, because setup always requires manual steps",
            "The entire dev environment is running in seconds — identical to every other developer's setup",
            "Only the database starts",
            "The code is deployed to production",
        ],
        correct=1,
        explanation="That's the power of Compose: declarative, reproducible dev environments. Onboarding goes from days to seconds.",
    ),
]

def run(session: Session):
    return run_module("Module 6: Industry Use Cases", LESSON, CHALLENGES, session)
