"""Extracts live DOM fingerprints and bounding geometries via Playwright."""

from __future__ import annotations
from typing import List, Optional
from playwright.async_api import Page, Locator
from src.models import ElementFingerprint


async def extract_fingerprint(page: Page, locator: Locator, selector: str) -> Optional[ElementFingerprint]:
    """Extract a comprehensive ElementFingerprint from an existing locator."""
    try:
        count = await locator.count()
        if count == 0:
            return None

        first = locator.first
        element_data = await first.evaluate("""el => {
            const rect = el.getBoundingClientRect();
            return {
                tag_name: el.tagName ? el.tagName.toLowerCase() : '',
                id: el.id || null,
                name: el.getAttribute('name') || null,
                classes: Array.from(el.classList || []),
                text_content: (el.innerText || el.textContent || '').trim().substring(0, 150),
                aria_label: el.getAttribute('aria-label') || null,
                role: el.getAttribute('role') || null,
                placeholder: el.getAttribute('placeholder') || null,
                element_type: el.getAttribute('type') || null,
                data_testid: el.getAttribute('data-testid') || el.getAttribute('data-test') || null,
                bounding_box: {
                    x: rect.x,
                    y: rect.y,
                    width: rect.width,
                    height: rect.height
                }
            };
        }""")

        return ElementFingerprint(
            tag_name=element_data["tag_name"],
            id=element_data["id"],
            name=element_data["name"],
            classes=element_data["classes"],
            text_content=element_data["text_content"],
            aria_label=element_data["aria_label"],
            role=element_data["role"],
            placeholder=element_data["placeholder"],
            element_type=element_data["element_type"],
            data_testid=element_data["data_testid"],
            css_selector=selector,
            bounding_box=element_data["bounding_box"],
        )
    except Exception:
        return None


async def scan_interactive_candidates(page: Page) -> List[ElementFingerprint]:
    """Scan all interactive and visible input elements across the active page context."""
    raw_candidates = await page.evaluate("""() => {
        const query = 'button, a, input, select, textarea, [role="button"], [role="link"], [data-testid]';
        const elements = Array.from(document.querySelectorAll(query));
        
        // కంటికి కనిపించే (visible) ఎలిమెంట్లను మాత్రమే ఎంచుకోవడం
        const visibleElements = elements.filter(el => {
            const rect = el.getBoundingClientRect();
            const style = window.getComputedStyle(el);
            return (
                style.display !== 'none' &&
                style.visibility !== 'hidden' &&
                style.opacity !== '0' &&
                rect.width > 0 &&
                rect.height > 0
            );
        });

        return visibleElements.map((el, index) => {
            const rect = el.getBoundingClientRect();
            const classes = Array.from(el.classList || []);
            const tagName = el.tagName.toLowerCase();
            
            // స్పష్టమైన మరియు ఖచ్చితమైన యూనిక్ సెలెక్టర్‌ను నిర్మించడం
            let adhocSelector = tagName;
            if (el.id) {
                adhocSelector += `#${CSS.escape(el.id)}`;
            } else if (el.getAttribute('data-testid')) {
                adhocSelector += `[data-testid="${CSS.escape(el.getAttribute('data-testid'))}"]`;
            } else if (el.getAttribute('name')) {
                adhocSelector += `[name="${CSS.escape(el.getAttribute('name'))}"]`;
            } else if (el.getAttribute('placeholder')) {
                adhocSelector += `[placeholder="${CSS.escape(el.getAttribute('placeholder'))}"]`;
            } else if (classes.length > 0) {
                adhocSelector += `.${classes.slice(0, 2).map(c => CSS.escape(c)).join('.')}`;
            } else {
                adhocSelector += `:nth-of-type(${index + 1})`;
            }

            return {
                tag_name: tagName,
                id: el.id || null,
                name: el.getAttribute('name') || null,
                classes: classes,
                text_content: (el.innerText || el.textContent || '').trim().substring(0, 150),
                aria_label: el.getAttribute('aria-label') || null,
                role: el.getAttribute('role') || null,
                placeholder: el.getAttribute('placeholder') || null,
                element_type: el.getAttribute('type') || null,
                data_testid: el.getAttribute('data-testid') || el.getAttribute('data-test') || null,
                css_selector: adhocSelector,
                bounding_box: {
                    x: rect.x,
                    y: rect.y,
                    width: rect.width,
                    height: rect.height
                }
            };
        });
    }""")

    return [ElementFingerprint(**c) for c in raw_candidates]