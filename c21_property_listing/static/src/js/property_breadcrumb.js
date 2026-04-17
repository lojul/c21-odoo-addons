/** @odoo-module **/

import { reactive } from "@odoo/owl";

function getNativeBreadcrumbItems() {
    const breadcrumbRoot = document.querySelector(
        ".o_control_panel .breadcrumb, .o_control_panel .o_control_panel_breadcrumbs"
    );
    if (!breadcrumbRoot) {
        return [];
    }
    return Array.from(breadcrumbRoot.querySelectorAll(".breadcrumb-item")).filter(
        (item) => item.textContent.trim()
    );
}

function syncPropertyBreadcrumb() {
    const nativeItems = getNativeBreadcrumbItems();
    const sectionItem = nativeItems[0];

    document.querySelectorAll(".c21_breadcrumb_bar").forEach((bar) => {
        const sectionButton = bar.querySelector(".c21_breadcrumb_section_link");
        const sectionSeparator = bar.querySelector(".c21_breadcrumb_sep_section");
        const currentSeparator = bar.querySelector(".c21_breadcrumb_sep_current");
        if (!sectionButton || !sectionSeparator || !currentSeparator) {
            return;
        }

        if (!sectionItem) {
            sectionButton.style.display = "none";
            sectionSeparator.style.display = "none";
            currentSeparator.style.display = "none";
            sectionButton.onclick = null;
            return;
        }

        const sectionLabel = sectionItem.textContent.trim();
        if (!sectionLabel || sectionLabel.toLowerCase() === "properties") {
            sectionButton.style.display = "none";
            sectionSeparator.style.display = "none";
            currentSeparator.style.display = "none";
            sectionButton.onclick = null;
            return;
        }

        sectionButton.textContent = sectionLabel;
        sectionButton.style.display = "inline-flex";
        sectionSeparator.style.display = "inline";
        currentSeparator.style.display = "inline";
        sectionButton.onclick = (event) => {
            event.preventDefault();
            const nativeTarget = sectionItem.querySelector("a, button") || sectionItem;
            nativeTarget.dispatchEvent(
                new MouseEvent("click", { bubbles: true, cancelable: true })
            );
        };
    });
}

const observer = new MutationObserver(() => {
    window.requestAnimationFrame(syncPropertyBreadcrumb);
});

function startBreadcrumbSync() {
    syncPropertyBreadcrumb();
    if (document.body) {
        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ["class"],
        });
    }
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", startBreadcrumbSync, { once: true });
} else {
    startBreadcrumbSync();
}

export default {}
