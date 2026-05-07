<div align="center">

# Diagflow

<img src="docs/logo.png" alt="diagflow logo" width="180" />

**Animated diagram framework for Python — declarative storytelling for technical systems.**

Describe your architecture, data flow, or algorithm in pure Python.  
Export a beautiful, self-contained animated HTML presentation in one line.

<br>

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-export-E34F26?style=flat-square&logo=html5&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-GSAP%203-F7DF1E?style=flat-square&logo=javascript&logoColor=black)
![SVG](https://img.shields.io/badge/SVG-rendering-FFB13B?style=flat-square&logo=svg&logoColor=black)
![NetworkX](https://img.shields.io/badge/NetworkX-layout-orange?style=flat-square)
![Jinja2](https://img.shields.io/badge/Jinja2-templates-B41717?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-22c55e?style=flat-square)
![Version](https://img.shields.io/badge/version-0.1.0-6366f1?style=flat-square)

</div>

---

## Why Diagflow?

| Tool | Limitation |
|---|---|
| Mermaid | Static — no animation or storytelling |
| PowerPoint | Manual, non-programmable, hard to maintain |
| Manim | Powerful but steep learning curve |
| **Diagflow** | **Declarative Python DSL → animated HTML in one call** |

---

## Features

- **Declarative DSL** — describe nodes, edges and animations in plain Python
- **Step-based slides** — present your system one step at a time, like a deck of slides
- **4 animation types** — `fade_in`, `fade_out`, `highlight`, `send_message`
- **Graph Morphing** — smooth semantic transition between two diagram states (diff, match, animate)
- **Auto layout** — topological, spring, or grid layout via NetworkX, zero configuration
- **Standalone HTML export** — single file, no server, works offline (GSAP CDN only)
- **Keyboard navigation** — `←` `→` arrow keys in all exported files
- **Dark theme** — GitHub-style dark design with glow effects, beautiful by default

---

## Installation

```bash
pip install diagflow          # from PyPI (coming soon)
# or from source:
git clone https://github.com/you/diagflow
cd diagflow
pip install -e .
```

**Requirements:** Python 3.10+, `networkx`, `jinja2`

---

## Quick Start

```python
from diagflow import Diagram, Node

d = Diagram("Hello Diagflow")

api = Node("API")
db  = Node("Database")

d.add(api, db)
edge = d.connect(api, db, label="SQL")

d.animate(
    api.fade_in(),
    db.fade_in(at=0.4),
    edge.fade_in(at=0.7),
    api.send("SELECT * FROM users", db, at=1.1),
)

d.export("output.html")   # → standalone animated HTML
```

---

## Core API

### Nodes

```python
node = Node("label")                    # create a node (auto color assigned)
node = Node("label", color="#4299e1")   # explicit color

# animations — return animation objects for d.animate()
node.fade_in(at=0.0)
node.highlight(color="#fbbf24", at=0.0, duration=1.0)
node.send("message text", to=other_node, at=0.0)
```

### Edges

```python
edge = d.connect(source, target)                        # solid edge
edge = d.connect(source, target, label="HTTP", style="dashed")
edge.fade_in(at=0.5)
```

### Diagram

```python
d = Diagram("Title")
d.add(node_a, node_b)               # register nodes
d.connect(node_a, node_b)           # create edge (registers nodes too)
d.animate(*animations)              # append animations to active step
d.show(*elements, at=0.0)           # shorthand fade_in for multiple elements
d.export("path/output.html")        # compute layout + render + write
```

---

## Step-based Slides

Use `with d.step("title"):` to group animations into navigable slides.  
Elements added inside a step **automatically fade in** on that step — no boilerplate.

```python
from diagflow import Diagram, Node

d = Diagram("API Request Flow")

client  = Node("Client")
gateway = Node("API Gateway")
auth    = Node("Auth Service")
db      = Node("PostgreSQL")

with d.step("System Overview"):
    d.add(client, gateway, auth, db)
    d.connect(client,  gateway)
    d.connect(gateway, auth)
    d.connect(gateway, db)

with d.step("Client sends request"):
    d.animate(client.send("GET /api/users", gateway))

with d.step("Token validation"):
    d.animate(gateway.send("verify(token)", auth))
    d.animate(auth.highlight(color="#48bb78", at=0.9))

with d.step("Database query"):
    d.animate(gateway.send("SELECT * FROM users", db))

d.export("api_flow.html")
```

> Navigate with **← →** arrow keys or the Prev / Next buttons.

---

## Graph Morphing

`Morph` generates a smooth **semantic transition** between two diagram states.  
It automatically diffs the graphs, matches equivalent nodes by ID or label similarity, and builds a GSAP timeline that moves, adds, removes, and rewires elements.

```python
from diagflow import Diagram, Node, Morph

# ── state 1: simple 3-tier system ─────────────────────────────
d1 = Diagram("v1: Simple Architecture")
client = Node("Client");  api = Node("API");  db = Node("Database")
d1.add(client, api, db)
d1.connect(client, api);  d1.connect(api, db)

# ── state 2: scaled system ─────────────────────────────────────
d2 = Diagram("v2: Scaled Architecture")
d2_client  = Node("Client")       # matched to d1 "Client"   → persist
d2_gateway = Node("API Gateway")  # matched to d1 "API"      → modify label
d2_auth    = Node("Auth Service") # no match                 → add
d2_cache   = Node("Redis Cache")  # no match                 → add
d2_db      = Node("Database")     # matched to d1 "Database" → persist
d2.add(d2_client, d2_gateway, d2_auth, d2_cache, d2_db)
d2.connect(d2_client, d2_gateway)
d2.connect(d2_gateway, d2_auth)
d2.connect(d2_gateway, d2_cache)
d2.connect(d2_gateway, d2_db)

# ── morph ──────────────────────────────────────────────────────
morph = Morph(d1, d2, duration=1.8, stagger=0.10)
morph.export("v1_to_v2.html")

# Shorthand via Diagram
d1.transition_to(d2, duration=1.8).export("v1_to_v2.html")
```

### Morph animation timeline

```
[0.00 → 0.30s]  Removed nodes fade out  +  all D1 edges fade out
[0.20 → 0.75s]  Persistent nodes move to D2 positions  (+ label / color morph)
[0.65 → 0.90s]  Added nodes fade in  (back.out spring easing)
[0.72 → 1.00s]  D2 edges fade in
```

### Matching strategy

| Priority | Method | Score |
|---|---|---|
| 1 | Exact ID match | 1.0 |
| 2 | Label similarity (`SequenceMatcher`) | ≤ 0.85 |
| 3 | Structural bonus (Jaccard on neighbor labels) | +0.15 |

---

## Examples

> **Note:** iframes render in VS Code Markdown Preview and local browsers.  
> On GitHub, open the `.html` files directly: [`examples/`](examples/)

<br>

### Basic — single animated scene

<details>
<summary>▶ Source: <code>examples/basic.py</code></summary>

```python
from diagflow import Diagram, Node

d = Diagram("Hello Diagflow")
api = Node("API");  db = Node("Database")
d.add(api, db)
edge = d.connect(api, db, label="SQL")
d.animate(
    api.fade_in(),
    db.fade_in(at=0.4),
    edge.fade_in(at=0.7),
    api.send("SELECT * FROM users", db, at=1.1),
)
d.export("examples/basic_output.html")
```
</details>

<iframe
  src="examples/basic_output.html"
  width="100%"
  height="340"
  style="border:1px solid #21262d; border-radius:12px; display:block;"
  title="Basic example"
></iframe>

<br>

---

### API Flow — 5-step slide deck

<details>
<summary>▶ Source: <code>examples/api_flow.py</code></summary>

```python
from diagflow import Diagram, Node

d = Diagram("API Request Flow")
client  = Node("Client");   gateway = Node("API Gateway")
auth    = Node("Auth Service");   cache = Node("Redis Cache");   db = Node("PostgreSQL")

with d.step("System Overview"):
    d.add(client, gateway, auth, cache, db)
    d.connect(client, gateway);  d.connect(gateway, auth)
    d.connect(gateway, cache);   d.connect(gateway, db)

with d.step("Client makes a request"):
    d.animate(client.send("GET /api/users", gateway))

with d.step("Token validation"):
    d.animate(gateway.send("verify(token)", auth))
    d.animate(auth.highlight(color="#48bb78", at=0.9))

with d.step("Cache lookup"):
    d.animate(gateway.send("GET users:cache", cache))

with d.step("Database query"):
    d.animate(gateway.send("SELECT * FROM users", db))
    d.animate(db.highlight(color="#4299e1", at=0.9))

d.export("examples/api_flow_output.html")
```
</details>


<br>

---

### JWT Auth Flow

<details>
<summary>▶ Source: <code>examples/auth_flow.py</code></summary>

```python
from diagflow import Diagram, Node

d = Diagram("JWT Auth Flow")
browser = Node("Browser");  api = Node("API")
jwt     = Node("JWT Service");  users = Node("Users DB")

with d.step("Infrastructure"):
    d.add(browser, api, jwt, users)
    d.connect(browser, api);  d.connect(api, jwt);  d.connect(api, users)

with d.step("Login request"):
    d.animate(browser.send("POST /login  { user, pass }", api))

with d.step("Validate credentials"):
    d.animate(api.send("SELECT WHERE email=?", users))
    d.animate(users.highlight(at=0.9))

with d.step("Issue token"):
    d.animate(api.send("sign({ userId, exp })", jwt))
    d.animate(jwt.highlight(color="#9f7aea", at=0.85))

with d.step("Token delivered"):
    d.animate(api.send("200 { token: eyJ... }", browser))
    d.animate(browser.highlight(color="#48bb78", at=0.9))

d.export("examples/auth_flow_output.html")
```
</details>

<br>

---

### Graph Morph — v1 → v2 architecture

<details>
<summary>▶ Source: <code>examples/morph_example.py</code></summary>

```python
from diagflow import Diagram, Node, Morph

d1 = Diagram("v1: Simple Architecture")
client = Node("Client");  api = Node("API");  db = Node("Database")
d1.add(client, api, db);  d1.connect(client, api);  d1.connect(api, db)

d2 = Diagram("v2: Scaled Architecture")
d2_client  = Node("Client");    d2_gateway = Node("API Gateway")
d2_auth    = Node("Auth Service");  d2_cache = Node("Redis Cache");  d2_db = Node("Database")
d2.add(d2_client, d2_gateway, d2_auth, d2_cache, d2_db)
d2.connect(d2_client, d2_gateway);   d2.connect(d2_gateway, d2_auth)
d2.connect(d2_gateway, d2_cache);    d2.connect(d2_gateway, d2_db)

Morph(d1, d2, duration=1.8, stagger=0.10).export("examples/morph_output.html")
```
</details>


---

## Architecture

```
diagflow/
├── core/
│   ├── diagram.py        ← Diagram  (orchestrator, step context manager)
│   ├── node.py           ← Node     (DSL: .fade_in() .highlight() .send())
│   └── edge.py           ← Edge     (DSL: .fade_in())
│
├── animation/
│   └── animations.py     ← FadeIn · FadeOut · Highlight · SendMessage · Step
│
├── layout/
│   └── auto_layout.py    ← topological (DAG) → spring → grid fallback
│
├── morph/
│   ├── matcher.py        ← bipartite node matching (ID / label / structural)
│   ├── diff.py           ← GraphDiff  NodeChange  EdgeChange
│   └── morph_engine.py   ← Morph class, merged-canvas strategy, timeline gen
│
├── style/
│   └── theme.py          ← Theme dataclass
│
└── export/
    ├── html_renderer.py       ← serialises diagram → JSON → Jinja2
    └── templates/
        ├── diagram.html.j2    ← step-based player (GSAP + SVG + dark theme)
        └── morph.html.j2      ← morph player (merged SVG canvas)
```

---

## Roadmap

- [ ] PDF export (frames via `reportlab` or `playwright`)
- [ ] Video export (MP4 / GIF via FFmpeg headless render)+
- [ ] Icon packs (AWS, Kubernetes, GCP node shapes)
- [ ] Code block animations (syntax-highlighted code with line highlights)
- [ ] Multi-state morph chains (`d1 → d2 → d3`)
- [ ] LLM integration — generate diagrams from natural language

---

## License

MIT © 2026 — built with Python, SVG, and GSAP.
