from engine import (MultipleChoice, ScenarioChallenge, SpotTheBug,
                     Session, run_module)

LESSON = """
  A spare PC plus Docker equals your own personal cloud. You can run 20+
  services simultaneously, replacing paid SaaS with open-source alternatives:
  Jellyfin (your own Netflix), Vaultwarden (your own 1Password), Nextcloud
  (your own Google Drive), Pi-hole (network-wide ad blocking), Home Assistant
  (smart home control), and Portainer (a web GUI to manage it all).
"""

CHALLENGES = [
    MultipleChoice(
        question="What is the main appeal of self-hosting services with Docker at home?",
        options=[
            "It's always faster than cloud services",
            "You run open-source alternatives to SaaS on your own hardware, keeping data private and eliminating monthly fees",
            "Docker makes home internet faster",
            "You get a free server from Docker",
        ],
        correct=1,
        explanation="Self-hosting gives you privacy, control, and eliminates recurring subscription costs for services you can run yourself.",
    ),
    MultipleChoice(
        question="Which self-hosted Docker app acts as a network-wide ad and tracker blocker by intercepting DNS queries?",
        options=["Jellyfin", "Nextcloud", "Pi-hole", "Portainer"],
        correct=2,
        explanation="Pi-hole acts as a DNS sinkhole — it intercepts DNS queries and blocks known ad/tracker domains for your entire network.",
    ),
    ScenarioChallenge(
        setup="You want to run Vaultwarden (a self-hosted Bitwarden password manager). The container image is 'vaultwarden/server'. You want data to survive container restarts, stored in a named volume called 'vw_data'. The service should be on port 8888.",
        question="Write the docker run command.",
        accepted=[
            "docker run -v vw_data:/data -p 8888:80 vaultwarden/server",
            "docker run -p 8888:80 -v vw_data:/data vaultwarden/server",
            "docker run -d -v vw_data:/data -p 8888:80 vaultwarden/server",
            "docker run -d -p 8888:80 -v vw_data:/data vaultwarden/server",
        ],
        explanation="Named volumes persist beyond the container. -v vw_data:/data maps the Docker-managed volume to Vaultwarden's data directory at /data.",
        hint_text="You need -v for the volume and -p for the port mapping.",
    ),
    SpotTheBug(
        code_block="""\
services:
  portainer:
    image: portainer/portainer-ce
    ports:
      - "9000:9000"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock""",
        question="Portainer starts but loses all its settings every time you restart it. What volume is missing?",
        accepted_keywords=["portainer_data", "data", "volume", "persist", "/data"],
        explanation="Portainer stores its configuration at /data inside the container. Without a named volume mapping to /data, the config is lost on restart. Add: - portainer_data:/data",
        hint_text="Where does Portainer store its configuration inside the container?",
    ),
    MultipleChoice(
        question="You want to manage all your home server Docker containers through a web GUI. Which tool is purpose-built for this?",
        options=["Pi-hole", "Jellyfin", "Portainer", "Home Assistant"],
        correct=2,
        explanation="Portainer is a lightweight web UI for managing Docker containers, images, volumes, and networks — perfect for home servers.",
    ),
]

def run(session: Session):
    return run_module("Module 7: Home Lab & Self-Hosting", LESSON, CHALLENGES, session)
