# 🌐 Omni-Web-Agent: Autonomous Self-Healing Web QA Framework

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat&logo=python)
![Playwright](https://img.shields.io/badge/Playwright-Automation-green?style=flat&logo=playwright)
![Architecture](https://img.shields.io/badge/Architecture-Modular-orange?style=flat)
![Status](https://img.shields.io/badge/Status-Production--Ready-brightgreen?style=flat)

An advanced, autonomous web testing framework built with **Python**, **Playwright**, and a **weighted heuristic self-healing engine**. Omni-Web-Agent shifts modern test engineering from fragile, hardcoded selector scripts to an intelligent, zero-code autonomous user journey verification model.

---

## 🚀 Key Highlights & Architectural Strengths

- **Autonomous End-to-End User Journey**: Executes full multi-page workflows (Authentication ➔ Inventory Exploration ➔ Cart Verification ➔ Customer Information Entry ➔ Order Confirmation) without manual scripting.
- **Weighted Multi-Factor Self-Healing Engine**: Recovers from mutated or broken DOM selectors using dynamic heuristic matching:
  - Strict Test IDs & Accessibility labels (`data-testid`, `aria-label`)
  - Tag Name & Element Type compatibility
  - Semantic Content Matching (Text, Names, Placeholders)
  - CSS Hierarchy & Spatial Proximity
- **Live Visual Cadence (Human-like Interaction)**: Features deliberate typing delays and smooth transitions between multi-page stages, making live demonstrations and headless recordings easy to follow.
- **Rich Telemetry & Reporting**: Generates structured execution reports in the terminal showcasing step statuses, execution latency, and self-healing metrics.

---

## 🛠️ Project Architecture

```text
omni-web-agent/
├── src/
│   ├── __init__.py
│   ├── agent.py          # Core Autonomous Orchestrator & E2E Journey Handler
│   ├── models.py         # Pydantic schemas (ActionStep, Fingerprint, StepResult)
│   ├── scanner.py        # DOM Scanner & Dynamic Fingerprint Extractor
│   └── self_healing.py   # Multi-factor Weighted Resilience Engine
├── main.py               # Application entry point
├── requirements.txt      # Core dependencies
└── README.md             # Project documentation
```
---

## 📦 Tech Stack

- **Automation Engine**: [Playwright Python](https://playwright.dev/python/)
- **Data Validation & Schemas**: [Pydantic v2](https://docs.pydantic.dev/)
- **CLI Telemetry & Terminal UI**: [Rich](https://github.com/Textualize/rich)
- **Runtime Environment**: Python 3.10+

---

## ⚙️ Installation & Setup

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/satyanarayana51115/omni-web-agent.git
   cd omni-web-agent
   ```

2. **Create & Activate Virtual Environment:**

   ```
   python -m venv .venv
   ```

   **Windows PowerShell:**

   ```
   .venv\Scripts\activate
   ```

   **Linux/macOS:**

   ```
   source .venv/bin/activate
   ```

3. **Install Dependencies & Playwright Browsers:**

   ```
   pip install -r requirements.txt
   playwright install chromium
   ```

## 🚦Execution

4. **Run the complete autonomous E2E journey using:**

   ```
   python main.py
   ```

## 📊 Live Terminal Output Sample

```text 

Omni-Web-Agent: Autonomous E2E Journey on https://www.saucedemo.com/

>>> [Stage 1/5] Navigating to Login Page...
>>> [Stage 2/5] Login Successful. Exploring Catalog Page...
>>> [Stage 3/5] Cart Verified. Proceeding to Checkout...
>>> [Stage 4/5] Entering Customer Shipping Details...
>>> [Stage 5/5] Reviewing Order Summary & Finishing Order...
✓ Order Placed Successfully! Viewing confirmation...

StepStatusHealed?Original SelectorEffective SelectorMatchDuration
1PASSNONAVIGATEhttps://www.saucedemo.com/-1251.6ms
2PASSNO#user-name#user-name-2558.5ms
3PASSNO#password#password-2331.0ms
4PASSNO#login-button#login-button-583.4ms
5PASSNO#add-to-cart-sauce-labs-backpack#add-to-cart-sauce-labs-backpack-518.0ms
6PASSNO.shopping_cart_link.shopping_cart_link-512.8ms
7PASSNO#checkout#checkout-524.4ms
8PASSNO#first-name#first-name-1592.2ms
9PASSNO#last-name#last-name-2050.7ms
10PASSNO#postal-code#postal-code-1698.2ms
11PASSNO#continue#continue-571.0ms
12PASSNO#finish#finish-513.7ms


## 🛡️ License

​Distributed under the MIT License. See LICENSE for more information.
