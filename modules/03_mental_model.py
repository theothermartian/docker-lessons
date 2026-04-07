from engine import MultipleChoice, ScenarioChallenge, Session, run_module

LESSON = """
  Containers and VMs both provide isolation, but they do it differently.
  A VM carries a full guest OS — it's like a standalone house with its own
  plumbing and electrical. A container shares the host OS kernel — it's like
  an apartment in a building that shares infrastructure but keeps units private.
  The result: containers start in milliseconds and use megabytes, while VMs
  take minutes and consume gigabytes.
"""

CHALLENGES = [
    MultipleChoice(
        question="What does a Docker container share with the host machine that a VM does not?",
        options=[
            "The CPU brand",
            "The host OS kernel",
            "The disk filesystem",
            "The network card",
        ],
        correct=1,
        explanation="Containers share the host OS kernel. VMs run their own full guest kernel, which is why they're heavier.",
        hint_text="It's the core part of the operating system.",
    ),
    MultipleChoice(
        question="A VM boots in ~60 seconds. A Docker container starts in:",
        options=[
            "30 seconds",
            "10 seconds",
            "Milliseconds",
            "It depends on internet speed",
        ],
        correct=2,
        explanation="Since containers share the host kernel and don't boot an OS, startup is measured in milliseconds.",
    ),
    ScenarioChallenge(
        setup="Your team needs to run 50 isolated web servers on one physical machine. Budget is tight.",
        question="Should you use VMs or containers, and why? (answer: containers or vms + one reason)",
        accepted=["containers", "container", "docker"],
        explanation="Containers are far more resource-efficient — they share the host kernel and have MB-level overhead vs GB for VMs. You can run many more containers than VMs on the same hardware.",
        hint_text="Think about resource overhead — which approach is lighter?",
    ),
    MultipleChoice(
        question="Using the apartment analogy: if a container is an apartment, what is a VM?",
        options=[
            "A room in the apartment",
            "A piece of furniture",
            "A standalone house with its own plumbing and electrical",
            "A skyscraper",
        ],
        correct=2,
        explanation="A VM is fully self-contained with its own OS (plumbing, electrical). A container shares building infrastructure (the host kernel) while remaining private.",
    ),
    ScenarioChallenge(
        setup="You need to run a Windows Server application on a Linux host.",
        question="Should you use a container or a VM for this, and why?",
        accepted=["vm", "virtual machine", "virtual machines"],
        explanation="Containers share the host kernel — you can't run a Windows kernel on a Linux host using containers. You need a VM with a Windows guest OS.",
        hint_text="Containers share the host kernel. Can a Linux kernel run Windows apps?",
    ),
]

def run(session: Session):
    return run_module("Module 3: Containers vs VMs", LESSON, CHALLENGES, session)
