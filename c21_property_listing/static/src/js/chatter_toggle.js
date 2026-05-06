/** @odoo-module **/

// Track if we've already set up the observer
let observerInitialized = false;
let lastUrl = '';

function initChatterToggle() {
    // Only run on property listing form views
    const url = window.location.href;
    if (!url.includes('c21.property.listing') && !url.includes('c21_property_listing')) {
        return;
    }

    const chatter = document.querySelector('.o-mail-Form-chatter, .o-mail-Chatter');
    if (!chatter) return;

    // Check if button already exists in control panel
    if (document.querySelector('.c21_chatter_toggle_btn')) {
        // Button exists, just reapply state if needed
        reapplyState();
        return;
    }

    // Try multiple possible insertion points - prioritize control panel
    let insertTarget = null;
    let insertParent = null;

    // Option 1: Near the pager (1/1 navigation)
    insertTarget = document.querySelector('.o_cp_pager');
    insertParent = insertTarget?.parentNode;

    // Option 2: Control panel actions area
    if (!insertParent) {
        insertParent = document.querySelector('.o_control_panel_actions');
        insertTarget = insertParent?.firstChild;
    }

    // Option 3: Control panel buttons
    if (!insertParent) {
        insertParent = document.querySelector('.o_cp_buttons');
        insertTarget = insertParent?.firstChild;
    }

    // Option 4: Near the action menu (gear)
    if (!insertParent) {
        const actionMenu = document.querySelector('.o_cp_action_menus');
        if (actionMenu) {
            insertParent = actionMenu.parentNode;
            insertTarget = actionMenu;
        }
    }

    if (!insertParent) return;

    const btn = document.createElement('button');
    btn.className = 'c21_chatter_toggle_btn btn btn-link';
    btn.innerHTML = '<i class="fa fa-comments fa-lg"></i>';
    btn.title = 'Toggle Activity Panel / 切換活動面板';

    const isHidden = localStorage.getItem('c21_chatter_hidden') === 'true';
    if (isHidden) {
        applyHiddenState(chatter, btn);
    }

    btn.addEventListener('click', () => {
        const currentChatter = document.querySelector('.o-mail-Form-chatter, .o-mail-Chatter');
        if (!currentChatter) return;

        const isCurrentlyHidden = currentChatter.style.display === 'none';
        if (isCurrentlyHidden) {
            applyVisibleState(currentChatter, btn);
            localStorage.setItem('c21_chatter_hidden', 'false');
        } else {
            applyHiddenState(currentChatter, btn);
            localStorage.setItem('c21_chatter_hidden', 'true');
        }
    });

    if (insertTarget) {
        insertParent.insertBefore(btn, insertTarget);
    } else {
        insertParent.appendChild(btn);
    }
}

function applyHiddenState(chatter, btn) {
    // Hide chatter completely - set width to 0 and hide
    chatter.style.cssText = 'display: none !important; width: 0 !important; min-width: 0 !important; flex: 0 0 0 !important; overflow: hidden !important;';

    // Get the parent of chatter (should be .o_form_view)
    const formView = chatter.parentElement;
    if (formView && formView.classList.contains('o_form_view')) {
        // Override the flex/grid to single column
        formView.style.cssText = 'display: block !important;';
    }

    // Make form sheet background full width
    const formSheetBg = document.querySelector('.o_form_sheet_bg');
    if (formSheetBg) {
        formSheetBg.style.cssText = 'width: 100% !important; max-width: 100% !important; flex: 1 1 100% !important;';
    }

    // Update button
    btn.classList.add('text-muted');
    btn.innerHTML = '<i class="fa fa-comments-o fa-lg"></i>';
}

function applyVisibleState(chatter, btn) {
    // Show chatter
    chatter.style.cssText = '';

    // Reset form view
    const formView = chatter.parentElement;
    if (formView && formView.classList.contains('o_form_view')) {
        formView.style.cssText = '';
    }

    // Reset form sheet background
    const formSheetBg = document.querySelector('.o_form_sheet_bg');
    if (formSheetBg) {
        formSheetBg.style.cssText = '';
    }

    btn.classList.remove('text-muted');
    btn.innerHTML = '<i class="fa fa-comments fa-lg"></i>';
}

function reapplyState() {
    const chatter = document.querySelector('.o-mail-Form-chatter, .o-mail-Chatter');
    const btn = document.querySelector('.c21_chatter_toggle_btn');
    if (chatter && btn && localStorage.getItem('c21_chatter_hidden') === 'true') {
        applyHiddenState(chatter, btn);
    }
}

let debounceTimer = null;

function setupObserver() {
    if (observerInitialized) return;

    const observer = new MutationObserver((mutations) => {
        // Check if any mutation involves form views or chatter
        const relevantMutation = mutations.some(m => {
            const target = m.target;
            if (target.classList) {
                return target.classList.contains('o_form_view') ||
                       target.classList.contains('o-mail-Form-chatter') ||
                       target.classList.contains('o-mail-Chatter') ||
                       target.classList.contains('o_control_panel');
            }
            return false;
        });

        // Also check URL changes (navigation between records)
        const currentUrl = window.location.href;
        const urlChanged = currentUrl !== lastUrl;
        lastUrl = currentUrl;

        if (relevantMutation || urlChanged) {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                initChatterToggle();
            }, 300);
        }
    });

    if (document.body) {
        observer.observe(document.body, { childList: true, subtree: true });
        observerInitialized = true;
    }
}

// Use Odoo's whenReady to ensure DOM is ready
function onDOMReady(fn) {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', fn);
    } else {
        fn();
    }
}

onDOMReady(() => {
    setupObserver();

    // Multiple init attempts with increasing delays for reliability
    // This handles async component loading in Odoo 17+
    setTimeout(initChatterToggle, 500);
    setTimeout(initChatterToggle, 1000);
    setTimeout(initChatterToggle, 2000);
    setTimeout(initChatterToggle, 3000);
});

// Also listen for URL hash changes (SPA navigation)
window.addEventListener('hashchange', () => {
    setTimeout(initChatterToggle, 500);
});

// Listen for popstate (browser back/forward)
window.addEventListener('popstate', () => {
    setTimeout(initChatterToggle, 500);
});
