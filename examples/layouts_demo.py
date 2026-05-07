"""Demo showcasing all 4 layouts, subtitles, icons, and expand/collapse."""
from diagflow import Diagram, Node

d = Diagram("Diagflow — Layout Showcase")

# ── Step 1: Glassmorphism — click nodes to expand ─────────────────────────
with d.step("Glassmorphism  (click a node to expand)"):
    api = Node(
        "API Gateway",
        subtitle="rate-limited · TLS",
        icon="🔌",
        layout="glass",
        description="Handles all inbound HTTP/gRPC traffic. Enforces rate limits, TLS termination, and request tracing via OpenTelemetry.",
    )
    auth = Node(
        "Auth Service",
        subtitle="JWT · OAuth2",
        icon="🔐",
        layout="glass",
        description="Issues and validates JWT tokens. Supports OAuth2 flows and integrates with external IdPs via OIDC.",
    )
    db = Node(
        "PostgreSQL",
        subtitle="primary · replica",
        icon="🗄️",
        layout="glass",
        description="Primary + read replica setup. Automatic failover via Patroni. Backups every 6 hours to S3.",
    )
    d.add(api, auth, db)
    d.connect(api, auth)
    d.connect(api, db)
    d.animate(api.scale_in(at=0), auth.scale_in(at=0.15), db.scale_in(at=0.3))

# ── Step 2: Minimal Flat ───────────────────────────────────────────────────
with d.step("Minimal Flat"):
    client  = Node("Client",  layout="minimal", description="Web or mobile client. Communicates via REST over HTTPS.")
    gateway = Node("Gateway", layout="minimal", description="Routes requests and applies middleware like auth, logging, and tracing.")
    cache   = Node("Cache",   layout="minimal", description="Redis in-memory store. TTL 5 min. Reduces DB load by up to 80%.")
    d.add(client, gateway, cache)
    d.connect(client, gateway)
    d.connect(gateway, cache)

# ── Step 3: Material Design ────────────────────────────────────────────────
with d.step("Material Design"):
    svc_a = Node("Service A", subtitle="v2.1.0", layout="material", description="Owns the user domain. Exposes REST API and async events via Kafka.")
    svc_b = Node("Service B", subtitle="v1.9.4", layout="material", description="Processes payment workflows. PCI-DSS compliant. Circuit breaker enabled.")
    queue = Node("Message Queue", subtitle="RabbitMQ", layout="material", description="Durable AMQP queue. Dead-letter exchange for failed messages. 3-node cluster.")
    d.add(svc_a, svc_b, queue)
    d.connect(svc_a, queue)
    d.connect(queue, svc_b)

# ── Step 4: Modern Gradient ────────────────────────────────────────────────
with d.step("Modern Gradient"):
    ml    = Node("ML Model",      subtitle="inference · GPU",  icon="🧠", layout="gradient", description="PyTorch model served via TorchServe. P99 latency < 30 ms. A/B tested weekly.")
    pipe  = Node("Pipeline",      subtitle="Apache Spark",     icon="⚡", layout="gradient", description="Spark streaming pipeline. Processes 50K events/s. Auto-scales on EMR.")
    store = Node("Feature Store", subtitle="Redis · Feast",    icon="📦", layout="gradient", description="Online feature store with sub-5 ms reads. Feast for offline training data sync.")
    d.add(ml, pipe, store)
    d.connect(pipe, ml)
    d.connect(pipe, store)
    d.animate(ml.scale_in(at=0.1), pipe.scale_in(at=0.25), store.scale_in(at=0.4))

# ── Step 5: Pulse + send ──────────────────────────────────────────────────
with d.step("Live inference"):
    d.animate(
        pipe.pulse(at=0.0),
        pipe.send("predict(X)", ml, at=0.3),
        ml.highlight(color="#a78bfa", at=1.2),
    )

d.export("examples/layouts_demo_output.html")
