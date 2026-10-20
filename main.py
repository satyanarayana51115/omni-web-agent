"""Zero-Code Autonomous Web Agent - Full E2E E-Commerce Workflow."""

import asyncio
from src.agent import AutonomousWebAgent


async def main():
    # Headed browser execution with balanced timing for clean visibility
    agent = AutonomousWebAgent(headless=False, slow_mo=400)

    # Executes multi-page E2E user journey: Login -> Product -> Cart -> Checkout -> Finish
    await agent.run_end_to_end_journey("https://www.saucedemo.com/")


if __name__ == "__main__":
    asyncio.run(main())