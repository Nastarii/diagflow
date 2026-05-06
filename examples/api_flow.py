"""Step-based API flow diagram with 5 slides."""
from diagflow import Diagram, Node

d = Diagram("API Request Flow")

client  = Node("Client")
gateway = Node("API Gateway")
auth    = Node("Auth Service")
cache   = Node("Redis Cache")
db      = Node("PostgreSQL")

# ── Step 1: show the full system ───────────────────────────────────────────────
with d.step("System Overview"):
    d.add(client, gateway, auth, cache, db)
    d.connect(client,  gateway)
    d.connect(gateway, auth)
    d.connect(gateway, cache)
    d.connect(gateway, db)

# ── Step 2: client sends a request ────────────────────────────────────────────
with d.step("Client makes a request"):
    d.animate(client.send("GET /api/users", gateway))

# ── Step 3: JWT validation ─────────────────────────────────────────────────────
with d.step("Token validation"):
    d.animate(gateway.send("verify(token)", auth))
    d.animate(auth.highlight(color="#48bb78", at=0.9))

# ── Step 4: cache lookup ──────────────────────────────────────────────────────
with d.step("Cache lookup"):
    d.animate(gateway.send("GET users:cache", cache))

# ── Step 5: database query ────────────────────────────────────────────────────
with d.step("Database query"):
    d.animate(gateway.send("SELECT * FROM users", db))
    d.animate(db.highlight(color="#4299e1", at=0.9))

d.export("examples/api_flow_output.html")
