"""JWT authentication flow — demonstrates mixed animations."""
from diagflow import Diagram, Node

d = Diagram("JWT Auth Flow")

browser = Node("Browser")
api     = Node("API")
jwt     = Node("JWT Service")
users   = Node("Users DB")

with d.step("Infrastructure"):
    d.add(browser, api, jwt, users)
    d.connect(browser, api)
    d.connect(api,     jwt)
    d.connect(api,     users)

with d.step("Login request"):
    d.animate(browser.send("POST /login  { user, pass }", api))

with d.step("Validate credentials"):
    d.animate(api.send("SELECT WHERE email=?", users))
    d.animate(users.highlight(at=0.9))

with d.step("Issue token"):
    d.animate(api.send("sign({ userId, exp })", jwt))
    d.animate(jwt.highlight(color="#9f7aea", at=0.85))

with d.step("Token delivered"):
    d.animate(api.send("200 { token: eyJ… }", browser))
    d.animate(browser.highlight(color="#48bb78", at=0.9))

d.export("examples/auth_flow_output.html")
