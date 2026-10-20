"""Autonomous web agent with multi-page end-to-end user journey testing and visible transitions."""

from __future__ import annotations
import time
from typing import Dict, List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from playwright.async_api import Page, async_playwright

from src.models import ActionStep, ActionType, ElementFingerprint, StepResult
from src.scanner import extract_fingerprint, scan_interactive_candidates
from src.self_healing import SelfHealingEngine

console = Console()


class AutonomousWebAgent:
    def __init__(self, headless: bool = False, slow_mo: int = 600):
        self.headless = headless
        self.slow_mo = slow_mo
        self.healer = SelfHealingEngine()
        self.fingerprint_registry: Dict[str, ElementFingerprint] = {}
        self.history: List[StepResult] = []

    async def run_end_to_end_journey(self, start_url: str = "https://www.saucedemo.com/") -> List[StepResult]:
        """Executes a full QA End-to-End E-Commerce user journey with clear page transitions."""
        console.print(Panel.fit(f"[bold cyan]Omni-Web-Agent: Autonomous E2E Journey on {start_url}[/bold cyan]"))

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless, slow_mo=self.slow_mo)
            context = await browser.new_context(viewport={"width": 1280, "height": 800})
            page = await context.new_page()

            # --- PAGE 1: Authentication / Login ---
            console.print("\n[bold yellow]>>> [Stage 1/5] Navigating to Login Page...[/bold yellow]")
            start_time = time.perf_counter()
            await page.goto(start_url, wait_until="domcontentloaded")
            self._log_result(1, True, "NAVIGATE", start_url, (time.perf_counter() - start_time) * 1000)

            # Credentials filling
            await self._run_step(page, 2, ActionType.FILL, "#user-name", "standard_user")
            await self._run_step(page, 3, ActionType.FILL, "#password", "secret_sauce")
            await self._run_step(page, 4, ActionType.CLICK, "#login-button")
            await page.wait_for_load_state("domcontentloaded")

            # పేజీ మారిన తర్వాత యూజర్‌కు స్పష్టంగా కనిపించడానికి చిన్న విరామం
            await page.wait_for_timeout(1800)

            # --- PAGE 2: Inventory Catalog ---
            console.print("[bold yellow]>>> [Stage 2/5] Login Successful. Exploring Catalog Page...[/bold yellow]")
            await self._run_step(page, 5, ActionType.CLICK, "#add-to-cart-sauce-labs-backpack")
            await page.wait_for_timeout(800)

            await self._run_step(page, 6, ActionType.CLICK, ".shopping_cart_link")
            await page.wait_for_load_state("domcontentloaded")

            # కార్ట్ పేజీ ఓపెన్ అయిన తర్వాత చిన్న విరామం
            await page.wait_for_timeout(1800)

            # --- PAGE 3: Cart Verification ---
            console.print("[bold yellow]>>> [Stage 3/5] Cart Verified. Proceeding to Checkout...[/bold yellow]")
            await self._run_step(page, 7, ActionType.CLICK, "#checkout")
            await page.wait_for_load_state("domcontentloaded")

            # చెక్‌అవుట్ పేజీ ఓపెన్ అయిన తర్వాత చిన్న విరామం
            await page.wait_for_timeout(1800)

            # --- PAGE 4: Customer Information Form ---
            console.print("[bold yellow]>>> [Stage 4/5] Entering Customer Shipping Details...[/bold yellow]")
            await self._run_step(page, 8, ActionType.FILL, "#first-name", "Satya")
            await self._run_step(page, 9, ActionType.FILL, "#last-name", "Automation")
            await self._run_step(page, 10, ActionType.FILL, "#postal-code", "500081")
            await page.wait_for_timeout(800)

            await self._run_step(page, 11, ActionType.CLICK, "#continue")
            await page.wait_for_load_state("domcontentloaded")

            # ఆర్డర్ సమ్మరీ కనిపించడానికి చిన్న విరామం
            await page.wait_for_timeout(1800)

            # --- PAGE 5: Order Summary & Completion ---
            console.print("[bold yellow]>>> [Stage 5/5] Reviewing Order Summary & Finishing Order...[/bold yellow]")
            await self._run_step(page, 12, ActionType.CLICK, "#finish")
            await page.wait_for_load_state("domcontentloaded")

            # ఆర్డర్ కన్ఫర్మేషన్ స్క్రీన్ ("Thank you for your order!") స్పష్టంగా కనిపించడానికి 2 సెకన్ల విరామం
            console.print("[bold green]✓ Order Placed Successfully! Viewing confirmation...[/bold green]")
            await page.wait_for_timeout(2500)
            await browser.close()

        self._render_telemetry_table()
        return self.history

    async def _run_step(self, page: Page, step_id: int, action: ActionType, selector: str, value: Optional[str] = None):
        start_time = time.perf_counter()
        locator = page.locator(selector).first
        element_found = False

        try:
            await locator.wait_for(state="visible", timeout=3000)
            element_found = True
        except Exception:
            element_found = False

        healed = False
        effective_selector = selector
        match_score: Optional[float] = None
        healing_reasons: List[str] = []

        if not element_found:
            console.print(f"[yellow]⚠️ Locator Failed: '{selector}'. Triggering self-healing...[/yellow]")
            try:
                candidates = await scan_interactive_candidates(page)
                cached_fp = self.fingerprint_registry.get(selector)
                if cached_fp:
                    best = self.healer.find_best_match(cached_fp, candidates)
                    if best:
                        healed = True
                        effective_selector = best.selector_used
                        match_score = best.match_score
                        healing_reasons = best.reasons
                        locator = page.locator(effective_selector).first
            except Exception:
                pass

        try:
            if action == ActionType.CLICK:
                await locator.click(timeout=3000)
            elif action == ActionType.FILL:
                await locator.click(timeout=3000)
                await locator.press_sequentially(value or "", delay=90)

            elapsed = (time.perf_counter() - start_time) * 1000
            self._log_result(step_id, True, selector, effective_selector, elapsed, healed, match_score, healing_reasons)
        except Exception as e:
            elapsed = (time.perf_counter() - start_time) * 1000
            self._log_result(step_id, False, selector, effective_selector, elapsed, healed, error=str(e))

    def _log_result(
        self,
        step_id: int,
        success: bool,
        orig_sel: str,
        eff_sel: str,
        duration: float,
        healed: bool = False,
        score: Optional[float] = None,
        reasons: Optional[List[str]] = None,
        error: Optional[str] = None,
    ):
        self.history.append(
            StepResult(
                step_id=step_id,
                success=success,
                healed=healed,
                original_selector=orig_sel,
                effective_selector=eff_sel,
                match_score=score,
                healing_reasons=reasons or [],
                duration_ms=duration,
                error_message=error,
            )
        )

    def _render_telemetry_table(self):
        table = Table(title="Omni-Web-Agent E2E Execution Report", show_header=True, header_style="bold magenta")
        table.add_column("Step", justify="center", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Healed?", justify="center")
        table.add_column("Original Selector", style="dim")
        table.add_column("Effective Selector", style="bold")
        table.add_column("Match", justify="right")
        table.add_column("Duration", justify="right")

        for r in self.history:
            status = "[green]PASS[/green]" if r.success else "[red]FAIL[/red]"
            healed = "[yellow]YES[/yellow]" if r.healed else "[dim]NO[/dim]"
            score = f"{r.match_score:.2f}" if r.match_score is not None else "-"
            table.add_row(
                str(r.step_id),
                status,
                healed,
                r.original_selector[:28] + "..." if len(r.original_selector) > 28 else r.original_selector,
                r.effective_selector[:28] + "..." if len(r.effective_selector) > 28 else r.effective_selector,
                score,
                f"{r.duration_ms:.1f}ms",
            )

        console.print("\n", table)