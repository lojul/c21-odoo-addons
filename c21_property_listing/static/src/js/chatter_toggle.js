/** @odoo-module **/

function initChatterToggle() {
    const chatter = document.querySelector('.o-mail-Form-chatter, .o-mail-Chatter');
    if (!chatter) return;

    if (document.querySelector('.c21_chatter_toggle_btn')) return;

    const pagerArea = document.querySelector('.o_cp_pager');
    if (!pagerArea) return;

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

    pagerArea.parentNode.insertBefore(btn, pagerArea);
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

const observer = new MutationObserver(() => {
    setTimeout(() => {
        initChatterToggle();
        reapplyState();
    }, 300);
});

if (document.body) {
    observer.observe(document.body, { childList: true, subtree: true });
}

setTimeout(initChatterToggle, 1000);
