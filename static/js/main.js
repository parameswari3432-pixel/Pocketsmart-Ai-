/**
 * PocketSmart AI - Interactive Frontend Controller
 */

document.addEventListener('DOMContentLoaded', () => {
    initInteriorForm();
    initPartyForm();
    initJewelryForm();
    initImageDropzone();
});

/**
 * Format numeric currency
 */
function formatCurrency(amount, currency = '$') {
    return `${currency}${Number(amount || 0).toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
}

/**
 * Toggle Loading and Result Containers
 */
function setLoadingState(panelId, isLoading) {
    const emptyState = document.querySelector(`${panelId} .empty-state`);
    const loadingState = document.querySelector(`${panelId} .loading-state`);
    const contentState = document.querySelector(`${panelId} .content-state`);
    const submitBtn = document.querySelector(`button[type="submit"]`);

    if (isLoading) {
        if (emptyState) emptyState.style.display = 'none';
        if (contentState) contentState.style.display = 'none';
        if (loadingState) loadingState.style.display = 'block';
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.dataset.originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = `<span>Generating Smart Plan...</span>`;
        }
    } else {
        if (loadingState) loadingState.style.display = 'none';
        if (contentState) contentState.style.display = 'block';
        if (submitBtn) {
            submitBtn.disabled = false;
            if (submitBtn.dataset.originalText) {
                submitBtn.innerHTML = submitBtn.dataset.originalText;
            }
        }
    }
}

/**
 * 1. Home Interior Planner Controller
 */
function initInteriorForm() {
    const form = document.getElementById('interior-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const currency = document.getElementById('currency-select')?.value || '$';
        const budget = parseFloat(document.getElementById('budget')?.value) || 5000;
        const roomType = document.querySelector('input[name="room_type"]:checked')?.value || 'Living Room';
        const style = document.getElementById('style-select')?.value || 'Modern Minimalist';
        const sqft = parseFloat(document.getElementById('sqft')?.value) || 250;
        const priorities = document.getElementById('priorities')?.value || 'balanced';

        setLoadingState('#interior-results', true);

        try {
            const res = await fetch('/api/interior/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    budget: budget,
                    room_type: roomType,
                    style: style,
                    square_feet: sqft,
                    priorities: priorities,
                    currency: currency
                })
            });

            const data = await res.json();
            if (data.success && data.plan) {
                renderInteriorResults(data.plan, currency);
            } else {
                alert('Could not generate plan: ' + (data.detail || 'Unknown error'));
            }
        } catch (err) {
            console.error(err);
            alert('An error occurred while connecting to the AI service.');
        } finally {
            setLoadingState('#interior-results', false);
        }
    });
}

function renderInteriorResults(plan, currency) {
    const container = document.getElementById('interior-content');
    if (!container) return;

    let allocationsHtml = '';
    if (plan.allocations && plan.allocations.length) {
        allocationsHtml = plan.allocations.map(item => `
            <div class="allocation-item">
                <div class="allocation-info">
                    <span>${item.category}</span>
                    <span>${currency}${Number(item.amount).toLocaleString()} (${item.percentage}%)</span>
                </div>
                <div class="allocation-bar-bg">
                    <div class="allocation-bar-fill" style="width: ${item.percentage}%;"></div>
                </div>
                <div style="font-size: 0.78rem; color: var(--text-muted); margin-top: 2px;">${item.description || ''}</div>
            </div>
        `).join('');
    }

    let shoppingListHtml = '';
    if (plan.itemized_shopping_list && plan.itemized_shopping_list.length) {
        shoppingListHtml = `
            <h4 style="margin: 1.5rem 0 0.5rem; font-size: 1rem;">📦 Key Items & Shopping Recommendations</h4>
            <table class="breakdown-table">
                <thead>
                    <tr>
                        <th>Item</th>
                        <th>Category</th>
                        <th>Est. Cost</th>
                        <th>Priority</th>
                    </tr>
                </thead>
                <tbody>
                    ${plan.itemized_shopping_list.map(i => `
                        <tr>
                            <td>
                                <strong>${i.item}</strong>
                                <div style="font-size:0.75rem; color:var(--text-muted);">${i.recommendation || ''}</div>
                            </td>
                            <td><span style="font-size: 0.78rem; background: var(--bg-surface); padding: 2px 6px; border-radius: 4px;">${i.category}</span></td>
                            <td><strong>${currency}${Number(i.estimated_cost).toLocaleString()}</strong></td>
                            <td><span style="font-size: 0.78rem; font-weight:700; color: ${i.priority === 'High' ? '#EF4444' : i.priority === 'Medium' ? '#F59E0B' : '#10B981'}">${i.priority}</span></td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    let tipsHtml = '';
    if (plan.money_saving_tips && plan.money_saving_tips.length) {
        tipsHtml = `
            <h4 style="margin: 1.5rem 0 0.5rem; font-size: 1rem;">💡 Smart Savings Hacks</h4>
            ${plan.money_saving_tips.map(t => `<div class="tip-box">${t}</div>`).join('')}
        `;
    }

    let paletteHtml = '';
    if (plan.color_palette && plan.color_palette.length) {
        paletteHtml = `
            <h4 style="margin: 1.5rem 0 0.5rem; font-size: 1rem;">🎨 Curated Color Palette</h4>
            <div class="palette-container">
                ${plan.color_palette.map(p => `
                    <div class="palette-swatch" style="background-color: ${p.hex};">
                        <span style="background: rgba(255,255,255,0.85); padding: 1px 4px; border-radius: 3px;">${p.name}</span>
                    </div>
                `).join('')}
            </div>
        `;
    }

    container.innerHTML = `
        <div class="plan-header-card">
            <h3 class="plan-title">${plan.title}</h3>
            <p class="plan-summary">${plan.summary}</p>
            ${plan.style_analysis ? `<p style="font-size: 0.85rem; color: #A5B4FC; margin-top: 0.5rem;"><strong>Aesthetic Note:</strong> ${plan.style_analysis}</p>` : ''}
        </div>
        <div>
            <h4 style="margin-bottom: 0.75rem; font-size: 1rem;">📊 Recommended Budget Allocation</h4>
            ${allocationsHtml}
        </div>
        ${shoppingListHtml}
        ${tipsHtml}
        ${paletteHtml}
        <button class="btn btn-outline" style="margin-top: 1.5rem;" onclick="window.print()">🖨️ Print or Save as PDF</button>
    `;
}

/**
 * 2. Party Budget Planner Controller
 */
function initPartyForm() {
    const form = document.getElementById('party-form');
    if (!form) return;

    // Per guest calculator helper
    const budgetInput = document.getElementById('budget');
    const guestInput = document.getElementById('guest_count');
    const perGuestDisplay = document.getElementById('per-guest-indicator');

    function updatePerGuest() {
        if (!budgetInput || !guestInput || !perGuestDisplay) return;
        const b = parseFloat(budgetInput.value) || 0;
        const g = parseInt(guestInput.value) || 1;
        const curr = document.getElementById('currency-select')?.value || '$';
        perGuestDisplay.textContent = `~${curr}${(b / Math.max(g, 1)).toFixed(0)} / guest`;
    }

    budgetInput?.addEventListener('input', updatePerGuest);
    guestInput?.addEventListener('input', updatePerGuest);

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const currency = document.getElementById('currency-select')?.value || '$';
        const budget = parseFloat(budgetInput?.value) || 1500;
        const guestCount = parseInt(guestInput?.value) || 25;
        const eventType = document.getElementById('event-type')?.value || 'Birthday Party';
        const theme = document.getElementById('theme')?.value || 'Neon Glow';
        const venue = document.getElementById('venue')?.value || 'Home / Backyard';

        setLoadingState('#party-results', true);

        try {
            const res = await fetch('/api/party/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    budget: budget,
                    event_type: eventType,
                    guest_count: guestCount,
                    theme: theme,
                    venue_type: venue,
                    currency: currency
                })
            });

            const data = await res.json();
            if (data.success && data.plan) {
                renderPartyResults(data.plan, currency);
            } else {
                alert('Could not generate party plan: ' + (data.detail || 'Unknown error'));
            }
        } catch (err) {
            console.error(err);
            alert('An error occurred while connecting to AI.');
        } finally {
            setLoadingState('#party-results', false);
        }
    });
}

function renderPartyResults(plan, currency) {
    const container = document.getElementById('party-content');
    if (!container) return;

    let allocationsHtml = '';
    if (plan.allocations && plan.allocations.length) {
        allocationsHtml = plan.allocations.map(item => `
            <div class="allocation-item">
                <div class="allocation-info">
                    <span>${item.category}</span>
                    <span>${currency}${Number(item.amount).toLocaleString()} (${item.percentage}%)</span>
                </div>
                <div class="allocation-bar-bg">
                    <div class="allocation-bar-fill" style="width: ${item.percentage}%; background: var(--grad-emerald);"></div>
                </div>
                <div style="font-size: 0.78rem; color: var(--text-muted); margin-top: 2px;">${item.description || ''}</div>
            </div>
        `).join('');
    }

    let menuHtml = '';
    if (plan.menu_and_catering_ideas && plan.menu_and_catering_ideas.length) {
        menuHtml = `
            <h4 style="margin: 1.5rem 0 0.5rem; font-size: 1rem;">🍽️ Menu & Catering Blueprint</h4>
            <table class="breakdown-table">
                <thead>
                    <tr>
                        <th>Course</th>
                        <th>Recommended Item</th>
                        <th>Cost Tier</th>
                    </tr>
                </thead>
                <tbody>
                    ${plan.menu_and_catering_ideas.map(m => `
                        <tr>
                            <td><strong>${m.course}</strong></td>
                            <td>
                                <div>${m.item}</div>
                                <div style="font-size: 0.75rem; color: var(--text-muted);">${m.notes || ''}</div>
                            </td>
                            <td><span style="color: #34D399; font-weight:700;">${m.cost_tier}</span></td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    let scheduleHtml = '';
    if (plan.event_day_schedule && plan.event_day_schedule.length) {
        scheduleHtml = `
            <h4 style="margin: 1.5rem 0 0.5rem; font-size: 1rem;">⏰ Event Run of Show (Timeline)</h4>
            <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                ${plan.event_day_schedule.map(s => `
                    <div style="display: flex; gap: 1rem; font-size: 0.85rem; padding: 0.4rem 0.6rem; background: var(--bg-surface); border-radius: 6px;">
                        <strong style="color: #34D399; min-width: 90px;">${s.time}</strong>
                        <span>${s.activity}</span>
                    </div>
                `).join('')}
            </div>
        `;
    }

    let tipsHtml = '';
    if (plan.budget_saving_hacks && plan.budget_saving_hacks.length) {
        tipsHtml = `
            <h4 style="margin: 1.5rem 0 0.5rem; font-size: 1rem;">✨ Party Budget Hacks</h4>
            ${plan.budget_saving_hacks.map(t => `<div class="tip-box" style="border-color: #10B981; color: #D1FAE5;">${t}</div>`).join('')}
        `;
    }

    container.innerHTML = `
        <div class="plan-header-card" style="border-color: rgba(16, 185, 129, 0.3); background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(6, 182, 212, 0.05) 100%);">
            <h3 class="plan-title">${plan.title}</h3>
            <p class="plan-summary">${plan.tagline || ''}</p>
            <div style="margin-top: 0.5rem; font-size: 0.85rem; color: #34D399;">
                Target Cost: <strong>${currency}${plan.per_guest_budget} / guest</strong>
            </div>
        </div>
        <div>
            <h4 style="margin-bottom: 0.75rem; font-size: 1rem;">📊 Party Cost Allocation</h4>
            ${allocationsHtml}
        </div>
        ${menuHtml}
        ${scheduleHtml}
        ${tipsHtml}
        <button class="btn btn-outline" style="margin-top: 1.5rem;" onclick="window.print()">🖨️ Print Party Schedule & Budget</button>
    `;
}

/**
 * 3. Jewelry & Outfit Budget Planner Controller
 */
function initJewelryForm() {
    const form = document.getElementById('jewelry-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const currency = document.getElementById('currency-select')?.value || '$';
        const budget = parseFloat(document.getElementById('budget')?.value) || 2000;
        const occasion = document.getElementById('occasion')?.value || 'Wedding Guest';
        const style = document.getElementById('style_preference')?.value || 'Contemporary Minimalist';
        const metals = document.getElementById('metals')?.value || 'Yellow Gold / Diamonds';
        const fileInput = document.getElementById('outfit-file');

        setLoadingState('#jewelry-results', true);

        const formData = new FormData();
        formData.append('budget', budget);
        formData.append('occasion', occasion);
        formData.append('style_preference', style);
        formData.append('metals', metals);
        formData.append('currency', currency);

        if (fileInput && fileInput.files && fileInput.files[0]) {
            formData.append('outfit_image', fileInput.files[0]);
        }

        try {
            const res = await fetch('/api/jewelry/generate', {
                method: 'POST',
                body: formData
            });

            const data = await res.json();
            if (data.success && data.plan) {
                renderJewelryResults(data.plan, currency);
            } else {
                alert('Could not generate jewelry plan: ' + (data.detail || 'Unknown error'));
            }
        } catch (err) {
            console.error(err);
            alert('An error occurred while connecting to AI styling service.');
        } finally {
            setLoadingState('#jewelry-results', false);
        }
    });
}

function renderJewelryResults(plan, currency) {
    const container = document.getElementById('jewelry-content');
    if (!container) return;

    let allocationsHtml = '';
    if (plan.allocations && plan.allocations.length) {
        allocationsHtml = plan.allocations.map(item => `
            <div class="allocation-item">
                <div class="allocation-info">
                    <span>${item.category}</span>
                    <span>${currency}${Number(item.amount).toLocaleString()} (${item.percentage}%)</span>
                </div>
                <div class="allocation-bar-bg">
                    <div class="allocation-bar-fill" style="width: ${item.percentage}%; background: var(--grad-amber);"></div>
                </div>
                <div style="font-size: 0.78rem; color: var(--text-muted); margin-top: 2px;">${item.description || ''}</div>
            </div>
        `).join('');
    }

    let piecesHtml = '';
    if (plan.recommended_pieces && plan.recommended_pieces.length) {
        piecesHtml = `
            <h4 style="margin: 1.5rem 0 0.5rem; font-size: 1rem;">💎 Recommended Jewelry Pieces</h4>
            <div style="display: grid; gap: 0.85rem;">
                ${plan.recommended_pieces.map(p => `
                    <div style="background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: var(--radius-sm); padding: 0.85rem 1rem;">
                        <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.25rem;">
                            <strong style="color: #FBBF24;">${p.piece_type}</strong>
                            <span style="font-weight: 700;">${currency}${Number(p.estimated_price).toLocaleString()}</span>
                        </div>
                        <div style="font-size: 0.82rem; color: var(--text-secondary); margin-bottom: 0.4rem;">
                            <strong>Materials:</strong> ${p.material_options}
                        </div>
                        <div style="font-size: 0.78rem; color: var(--text-muted);">
                            <strong>Stylist Note:</strong> ${p.style_pairing_reason}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    let dosAndDontsHtml = '';
    if (plan.styling_dos_and_donts) {
        dosAndDontsHtml = `
            <h4 style="margin: 1.5rem 0 0.5rem; font-size: 1rem;">✨ Styling Do's & Don'ts</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
                <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: var(--radius-sm); padding: 0.75rem;">
                    <div style="font-size: 0.8rem; font-weight: 700; color: #34D399; margin-bottom: 0.4rem;">DO</div>
                    <ul style="font-size: 0.78rem; padding-left: 1rem; color: #D1FAE5;">
                        ${(plan.styling_dos_and_donts.dos || []).map(d => `<li>${d}</li>`).join('')}
                    </ul>
                </div>
                <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: var(--radius-sm); padding: 0.75rem;">
                    <div style="font-size: 0.8rem; font-weight: 700; color: #F87171; margin-bottom: 0.4rem;">DON'T</div>
                    <ul style="font-size: 0.78rem; padding-left: 1rem; color: #FEE2E2;">
                        ${(plan.styling_dos_and_donts.donts || []).map(d => `<li>${d}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;
    }

    container.innerHTML = `
        <div class="plan-header-card" style="border-color: rgba(245, 158, 11, 0.3); background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(239, 68, 68, 0.05) 100%);">
            <h3 class="plan-title">${plan.title}</h3>
            <p class="plan-summary">${plan.styling_verdict}</p>
            ${plan.outfit_match_analysis ? `<p style="font-size: 0.85rem; color: #FBBF24; margin-top: 0.5rem;"><strong>Outfit Harmony:</strong> ${plan.outfit_match_analysis}</p>` : ''}
        </div>
        <div>
            <h4 style="margin-bottom: 0.75rem; font-size: 1rem;">📊 Jewelry Investment Allocation</h4>
            ${allocationsHtml}
        </div>
        ${piecesHtml}
        ${dosAndDontsHtml}
        <button class="btn btn-outline" style="margin-top: 1.5rem;" onclick="window.print()">🖨️ Print Styling & Jewelry Plan</button>
    `;
}

/**
 * Image Dropzone & Preview Controller
 */
function initImageDropzone() {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('outfit-file');
    const previewContainer = document.getElementById('image-preview-container');
    const previewImg = document.getElementById('image-preview');
    const removeBtn = document.getElementById('remove-image-btn');

    if (!dropzone || !fileInput) return;

    dropzone.addEventListener('click', () => fileInput.click());

    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('dragover');
    });

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            fileInput.files = e.dataTransfer.files;
            showPreview(fileInput.files[0]);
        }
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files && fileInput.files[0]) {
            showPreview(fileInput.files[0]);
        }
    });

    removeBtn?.addEventListener('click', (e) => {
        e.stopPropagation();
        fileInput.value = '';
        if (previewContainer) previewContainer.style.display = 'none';
        dropzone.style.display = 'block';
    });

    function showPreview(file) {
        if (!file.type.startsWith('image/')) {
            alert('Please select an image file (JPG, PNG, WEBP).');
            return;
        }
        const reader = new FileReader();
        reader.onload = (e) => {
            if (previewImg) previewImg.src = e.target.result;
            if (previewContainer) previewContainer.style.display = 'block';
            dropzone.style.display = 'none';
        };
        reader.readAsDataURL(file);
    }
}
