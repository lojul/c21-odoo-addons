/** @odoo-module **/

import { Component, useState, onMounted, onPatched } from "@odoo/owl";
import { registry } from "@web/core/registry";

// Simple DOM-based toggle that runs after page load
function initChatterToggle() {
    // Check if we're on a form view with chatter
    const chatter = document.querySelector('.o-mail-Form-chatter, .o-mail-Chatter');
    if (!chatter) return;

    // Don't add button if it already exists
    if (document.querySelector('.c21_chatter_toggle_btn')) return;

    // Create the toggle button
    const btn = document.createElement('button');
    btn.className = 'c21_chatter_toggle_btn';
    btn.innerHTML = '<i class="fa fa-comments"></i>';
    btn.title = 'Toggle Activity Panel / 切換活動面板';

    // Check saved state
    const isHidden = localStorage.getItem('c21_chatter_hidden') === 'true';
    if (isHidden) {
        chatter.style.display = 'none';
        btn.classList.add('is-hidden');
        document.querySelector('.o_form_sheet_bg')?.classList.add('c21-chatter-hidden');
    }

    btn.addEventListener('click', () => {
        const currentlyHidden = chatter.style.display === 'none';
        if (currentlyHidden) {
            chatter.style.display = '';
            btn.classList.remove('is-hidden');
            document.querySelector('.o_form_sheet_bg')?.classList.remove('c21-chatter-hidden');
            localStorage.setItem('c21_chatter_hidden', 'false');
        } else {
            chatter.style.display = 'none';
            btn.classList.add('is-hidden');
            document.querySelector('.o_form_sheet_bg')?.classList.add('c21-chatter-hidden');
            localStorage.setItem('c21_chatter_hidden', 'true');
        }
    });

    document.body.appendChild(btn);
}

// Run on page load and navigation
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(initChatterToggle, 1000);
});

// Also observe DOM changes for SPA navigation
const observer = new MutationObserver(() => {
    setTimeout(initChatterToggle, 500);
});

if (document.body) {
    observer.observe(document.body, { childList: true, subtree: true });
}

// Initial call
setTimeout(initChatterToggle, 1500);
