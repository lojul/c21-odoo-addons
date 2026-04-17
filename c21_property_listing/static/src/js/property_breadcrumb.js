/** @odoo-module **/

/**
 * Property Breadcrumb Sync
 *
 * Syncs the custom breadcrumb bar with Odoo's native breadcrumb to show
 * the navigation path (e.g., Properties > All Properties > [Property Name])
 */

function getNativeBreadcrumbItems() {
    // Odoo 19 uses .breadcrumb inside .o_control_panel
    const breadcrumbRoot = document.querySelector(
        ".o_control_panel .breadcrumb"
    );
    if (!breadcrumbRoot) {
        return [];
    }
    // Get all breadcrumb items that have actual text content
    return Array.from(breadcrumbRoot.querySelectorAll(".breadcrumb-item")).filter(
        (item) => item.textContent.trim()
    );
}

function syncPropertyBreadcrumb() {
    const customBars = document.querySelectorAll(".c21_breadcrumb_bar");
    if (customBars.length === 0) {
        return;
    }

    const nativeItems = getNativeBreadcrumbItems();
    // The first native breadcrumb item is typically the section (e.g., "All Properties", "Co-working Spaces")
    const sectionItem = nativeItems.length > 0 ? nativeItems[0] : null;

    customBars.forEach((bar) => {
        const sectionButton = bar.querySelector(".c21_breadcrumb_section_link");
        const sectionSeparator = bar.querySelector(".c21_breadcrumb_sep_section");
        const currentSeparator = bar.querySelector(".c21_breadcrumb_sep_current");

        if (!sectionButton || !sectionSeparator || !currentSeparator) {
            return;
        }

        // If no native breadcrumb or no section item, hide the section part
        if (!sectionItem) {
            sectionButton.style.display = "none";
            sectionSeparator.style.display = "none";
            currentSeparator.style.display = "none";
            sectionButton.onclick = null;
            return;
        }

        const sectionLabel = sectionItem.textContent.trim();

        // Hide section if empty or if it's just "Properties" (avoid duplication)
        if (!sectionLabel || sectionLabel.toLowerCase() === "properties") {
            sectionButton.style.display = "none";
            sectionSeparator.style.display = "none";
            currentSeparator.style.display = "none";
            sectionButton.onclick = null;
            return;
        }

        // Show the section with the label from native breadcrumb
        sectionButton.textContent = sectionLabel;
        sectionButton.style.display = "inline-flex";
        sectionSeparator.style.display = "inline";
        currentSeparator.style.display = "inline";

        // Make clicking the section button trigger the native breadcrumb navigation
        sectionButton.onclick = (event) => {
            event.preventDefault();
            const nativeTarget = sectionItem.querySelector("a, button") || sectionItem;
            if (nativeTarget) {
                nativeTarget.dispatchEvent(
                    new MouseEvent("click", { bubbles: true, cancelable: true })
                );
            }
        };
    });
}

// Use MutationObserver to detect DOM changes and re-sync
let syncTimeout = null;
const observer = new MutationObserver(() => {
    // Debounce to avoid excessive calls
    if (syncTimeout) {
        clearTimeout(syncTimeout);
    }
    syncTimeout = setTimeout(() => {
        syncPropertyBreadcrumb();
    }, 50);
});

function startBreadcrumbSync() {
    // Initial sync
    syncPropertyBreadcrumb();

    // Observe DOM changes to re-sync when views change
    if (document.body) {
        observer.observe(document.body, {
            childList: true,
            subtree: true,
        });
    }
}

// Start when DOM is ready
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", startBreadcrumbSync, { once: true });
} else {
    startBreadcrumbSync();
}
