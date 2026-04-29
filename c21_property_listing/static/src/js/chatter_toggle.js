/** @odoo-module **/

function initChatterToggle() {
    const chatter = document.querySelector('.o-mail-Form-chatter, .o-mail-Chatter');
    if (!chatter) return;

    // Don't add button if it already exists
    if (document.querySelector('.c21_chatter_toggle_btn')) return;

    // Find the top right area - near the pager or control panel right side
    const targetArea = document.querySelector('.o_control_panel_main .o_cp_pager') ||
                       document.querySelector('.o_control_panel_breadcrumbs') ||
                       document.querySelector('.o_control_panel');
    if (!targetArea) return;

    // Create icon-only toggle button
    const btn = document.createElement('button');
    btn.className = 'c21_chatter_toggle_btn btn btn-link';
    btn.innerHTML = '<i class="fa fa-comments fa-lg"></i>';
    btn.title = 'Toggle Activity Panel / 切換活動面板';

    // Check saved state
    const isHidden = localStorage.getItem('c21_chatter_hidden') === 'true';
    if (isHidden) {
        applyHiddenState(btn);
    }

    btn.addEventListener('click', () => {
        const isCurrentlyHidden = document.body.classList.contains('c21-chatter-hidden');
        if (isCurrentlyHidden) {
            applyVisibleState(btn);
            localStorage.setItem('c21_chatter_hidden', 'false');
        } else {
            applyHiddenState(btn);
            localStorage.setItem('c21_chatter_hidden', 'true');
        }
    });

    // Insert button - try to place it on the right side
    const pager = document.querySelector('.o_cp_pager');
    if (pager) {
        pager.parentNode.insertBefore(btn, pager);
    } else {
        targetArea.appendChild(btn);
    }
}

function applyHiddenState(btn) {
    document.body.classList.add('c21-chatter-hidden');
    btn.classList.add('text-muted');
    btn.innerHTML = '<i class="fa fa-comments-o fa-lg"></i>';
}

function applyVisibleState(btn) {
    document.body.classList.remove('c21-chatter-hidden');
    btn.classList.remove('text-muted');
    btn.innerHTML = '<i class="fa fa-comments fa-lg"></i>';
}

// Observe for page changes
const observer = new MutationObserver(() => {
    setTimeout(initChatterToggle, 300);
});

if (document.body) {
    observer.observe(document.body, { childList: true, subtree: true });
}

setTimeout(initChatterToggle, 1000);
