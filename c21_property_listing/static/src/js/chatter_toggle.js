/** @odoo-module **/

// Add toggle button to control panel
function initChatterToggle() {
    const chatter = document.querySelector('.o-mail-Form-chatter, .o-mail-Chatter');
    if (!chatter) return;

    // Don't add button if it already exists
    if (document.querySelector('.c21_chatter_toggle_btn')) return;

    // Find the control panel buttons area
    const controlPanel = document.querySelector('.o_control_panel_main_buttons, .o_control_panel_actions');
    if (!controlPanel) return;

    // Create the toggle button for control panel
    const btn = document.createElement('button');
    btn.className = 'c21_chatter_toggle_btn btn btn-secondary ms-2';
    btn.innerHTML = '<i class="fa fa-comments me-1"></i><span class="d-none d-md-inline">Activity</span>';
    btn.title = 'Toggle Activity Panel / 切換活動面板';

    // Check saved state
    const isHidden = localStorage.getItem('c21_chatter_hidden') === 'true';
    if (isHidden) {
        hideChatter(chatter, btn);
    }

    btn.addEventListener('click', () => {
        const currentlyHidden = chatter.style.display === 'none';
        if (currentlyHidden) {
            showChatter(chatter, btn);
            localStorage.setItem('c21_chatter_hidden', 'false');
        } else {
            hideChatter(chatter, btn);
            localStorage.setItem('c21_chatter_hidden', 'true');
        }
    });

    controlPanel.appendChild(btn);
}

function hideChatter(chatter, btn) {
    // Hide the chatter completely
    chatter.style.display = 'none';
    btn.classList.remove('btn-secondary');
    btn.classList.add('btn-outline-secondary');

    // Expand form to full width - target the parent container
    const formSheetBg = document.querySelector('.o_form_sheet_bg');
    if (formSheetBg) {
        formSheetBg.classList.add('c21-chatter-hidden');
    }

    // Also hide the chatter container parent if exists
    const formView = document.querySelector('.o_form_view');
    if (formView) {
        formView.classList.add('c21-no-chatter');
    }
}

function showChatter(chatter, btn) {
    chatter.style.display = '';
    btn.classList.remove('btn-outline-secondary');
    btn.classList.add('btn-secondary');

    const formSheetBg = document.querySelector('.o_form_sheet_bg');
    if (formSheetBg) {
        formSheetBg.classList.remove('c21-chatter-hidden');
    }

    const formView = document.querySelector('.o_form_view');
    if (formView) {
        formView.classList.remove('c21-no-chatter');
    }
}

// Run on page changes
const observer = new MutationObserver(() => {
    setTimeout(initChatterToggle, 300);
});

if (document.body) {
    observer.observe(document.body, { childList: true, subtree: true });
}

// Initial call with delay
setTimeout(initChatterToggle, 1000);
