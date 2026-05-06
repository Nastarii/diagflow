"""
Morph example: v1 simple architecture → v2 scaled architecture.

Demonstrates all four diff cases:
  • Persistent nodes (Client, API, Database) — move to new positions
  • Modify node     (API → API Gateway)     — label + color change
  • Added nodes     (Auth Service, Redis)   — fade in
  • Removed nodes   (none in this example)  — (add a d1-only node to test)
  • Edge rewiring between states
"""
from diagflow import Diagram, Node, Morph

# ── D1: simple 3-tier system ──────────────────────────────────────────────────
d1 = Diagram("v1: Simple Architecture")

client = Node("Client")
api    = Node("API")
db     = Node("Database")

d1.add(client, api, db)
d1.connect(client, api)
d1.connect(api,    db)

# ── D2: scaled system with gateway, auth, and cache ───────────────────────────
d2 = Diagram("v2: Scaled Architecture")

d2_client  = Node("Client")        # exact label match → persist + move
d2_gateway = Node("API Gateway")   # similar to "API"  → modify
d2_auth    = Node("Auth Service")  # new                → add
d2_cache   = Node("Redis Cache")   # new                → add
d2_db      = Node("Database")      # exact label match  → persist + move

d2.add(d2_client, d2_gateway, d2_auth, d2_cache, d2_db)
d2.connect(d2_client,  d2_gateway)
d2.connect(d2_gateway, d2_auth)
d2.connect(d2_gateway, d2_cache)
d2.connect(d2_gateway, d2_db)

# ── Morph ─────────────────────────────────────────────────────────────────────
morph = Morph(d1, d2, duration=1.8, stagger=0.10, easing="power2.inOut")
morph.export("examples/morph_output.html")

# ── Also demonstrate the shorthand API on Diagram ────────────────────────────
# d1.transition_to(d2, duration=1.8).export("examples/morph_output2.html")
