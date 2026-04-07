from engine import MultipleChoice, ScenarioChallenge, Session, run_module

LESSON = """
  Containers didn't start with Docker. The lineage goes back to Unix chroot
  (1979), FreeBSD Jails (2000), Solaris Zones (2004), and Linux cgroups (2008,
  contributed by Google). Docker appeared in 2013, demoed at PyCon, and
  revolutionized the space — not by inventing containers, but by making them
  developer-friendly with a simple CLI and a portable image format.
"""

CHALLENGES = [
    MultipleChoice(
        question="What Linux kernel feature, contributed by Google in 2008, forms the foundation of modern containers?",
        options=[
            "Swap memory",
            "cgroups (control groups)",
            "The ext4 filesystem",
            "iptables",
        ],
        correct=1,
        explanation="cgroups allow the kernel to limit and isolate CPU, memory, disk I/O, and network for groups of processes — essential for containers.",
        hint_text="It stands for 'control groups'.",
    ),
    MultipleChoice(
        question="Docker 0.1 was famously demoed at which conference in 2013?",
        options=[
            "DockerCon",
            "AWS re:Invent",
            "PyCon",
            "Google I/O",
        ],
        correct=2,
        explanation="Solomon Hykes demoed Docker 0.1 in a 5-minute lightning talk at PyCon 2013 — it went viral.",
        hint_text="Docker is written in Go, but the conference was for a different language.",
    ),
    MultipleChoice(
        question="What was LXC (Linux Containers), and why did Docker supersede it?",
        options=[
            "A programming language — Docker is easier",
            "A cloud service — Docker is cheaper",
            "A user-space interface to cgroups — powerful but complex; Docker added developer-friendly tooling on top",
            "A virtual machine manager",
        ],
        correct=2,
        explanation="LXC provided raw container functionality via cgroups and namespaces, but Docker wrapped it with a simple CLI, image format, and registry.",
    ),
    ScenarioChallenge(
        setup="It's 1979. A Unix developer wants to run an untrusted program without it touching the rest of the filesystem.",
        question="What primitive Unix feature (introduced in 1979) gives them a restricted filesystem view?",
        accepted=["chroot", "chroot jail", "change root"],
        explanation="chroot changes the apparent root directory for a process — the earliest form of isolation and the conceptual ancestor of containers.",
        hint_text="It 'changes' the 'root' directory.",
    ),
    MultipleChoice(
        question="Today, what percentage of IT companies use containers in production (2025)?",
        options=["45%", "67%", "92%", "100%"],
        correct=2,
        explanation="Container adoption has grown rapidly — 92% of organizations now use containers in some form in production.",
    ),
]

def run(session: Session):
    return run_module("Module 2: History & Timeline", LESSON, CHALLENGES, session)
