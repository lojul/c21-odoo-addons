/** @odoo-module **/

import { registry } from "@web/core/registry";

// Add toggle button when DOM is ready
document.addEventListener('click', function(e) {
    // Delegate - check after any click if we need to add button
    setTimeout(addToggleButton, 500);
});

// Also run on initial load
setTimeout(addToggleButton, 1000);

function addToggleButton() {
    const chatter = document.querySelector('.o-mail-Form-chatter, .o-mail-Chatter');
    if (!chatter) return;

    // Check if button already exists
    if (document.querySelector('.o_chatter_toggle_btn')) return;

    // Create floating toggle button
    const btn = document.createElement('button');
    btn.className = 'o_chatter_toggle_btn btn';
    btn.innerHTML = '<i class="fa fa-comments"></i>';
    btn.title = 'Toggle Activity Panel / 切換活動面板';

    // Get saved preference
    const isHidden = localStorage.getItem('chatterHidden') === 'true';
    if (isHidden) {
        hideChatter(chatter);
    }

    btn.addEventListener('click', function() {
        toggleChatter(chatter);
    });

    document.body.appendChild(btn);
}

function toggleChatter(chatter) {
    const isCurrentlyHidden = localStorage.getItem('chatterHidden') === 'true';

    if (isCurrentlyHidden) {
        showChatter(chatter);
        localStorage.setItem('chatterHidden', 'false');
    } else {
        hideChatter(chatter);
        localStorage.setItem('chatterHidden', 'true');
    }
}

function hideChatter(chatter) {
    if (chatter) {
        chatter.style.display = 'none';
    }
    // Also adjust the form container
    const formSheetBg = document.querySelector('.o_form_sheet_bg');
    if (formSheetBg) {
        formSheetBg.classList.add('chatter-hidden');
    }
    // Update button appearance
    const btn = document.querySelector('.o_chatter_toggle_btn');
    if (btn) {
        btn.classList.add('chatter-is-hidden');
    }
}

function showChatter(chatter) {
    if (chatter) {
        chatter.style.display = '';
    }
    const formSheetBg = document.querySelector('.o_form_sheet_bg');
    if (formSheetBg) {
        formSheetBg.classList.remove('chatter-hidden');
    }
    const btn = document.querySelector('.o_chatter_toggle_btn');
    if (btn) {
        btn.classList.remove('chatter-is-hidden');
    }
}

// Re-apply state when navigating between records
const observer = new MutationObserver(function(mutations) {
    const chatter = document.querySelector('.o-mail-Form-chatter, .o-mail-Chatter');
    if (chatter && localStorage.getItem('chatterHidden') === 'true') {
        hideChatter(chatter);
    }
    addToggleButton();
});

// Start observing once DOM is ready
if (document.body) {
    observer.observe(document.body, { childList: true, subtree: true });
}
