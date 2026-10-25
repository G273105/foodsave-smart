import {AppError, money, canReserve, priceInputToPence, formatDate, quantity, expiryText} from './model.js';
import {createApi} from './api.js';
import {createMockService} from './mock.js';

const $ = id => document.getElementById(id), config = window.FOODSAVE_CONFIG;
const mock = config?.MODE === 'mock';
let service, products = [], reservations = [], category = 'all', activeView = 'browse', toastTimer,
    productGeneration = 0;
const locks = new Set();
let detailGeneration = 0, confirmAction = null;
const photos = {
    'lasagna ready meal': 'lasagna',
    'veggie curry': 'curry',
    'croissant 2-pack': 'croissant',
    'sourdough loaf': 'bread',
    'apples': 'apples',
    'sandwich (single)': 'sandwich',
    'sandwich': 'sandwich',
    'bread pack': 'bread-pack',
    'yoghurt pack': 'yoghurt',
    'sandwich pack (2 sandwiches)': 'sandwich-pack',
    'sandwich pack': 'sandwich-pack',
    'mixed vegetables': 'vegetables',
    'red apples': 'apples',
    'green apples': 'green-apples',
    'mixed apples pack': 'mixed-apples',
};

function node(tag, text, cls) {
    const n = document.createElement(tag);
    if (text !== undefined) n.textContent = text;
    if (cls) n.className = cls;
    return n;
}

function button(text, fn, cls = 'secondary') {
    const b = node('button', text, cls);
    b.type = 'button';
    b.onclick = fn;
    return b;
}

function feedback(id, message, type = 'loading', retry) {
    const target = typeof id === 'string' ? $(id) : id;
    target.replaceChildren();
    if (!message) return;
    const box = node('div', message, 'feedback ' + type);
    box.setAttribute('role', type === 'error' ? 'alert' : 'status');
    if (retry) box.append(button('Try again', retry));
    target.append(box);
}

function toast(message) {
    $('toast').textContent = message;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => $('toast').textContent = '', 8000);
}

function showMode() {
    const text = mock ? 'Independent review · Sample data · Actions save on this device; no real bookings' : 'API mode · Food availability and reservations use the team service';
    $('mode-banner').textContent = text + (mock && service?.persistent === false ? ' · Storage unavailable: this session only' : '');
    $('footer-mode').textContent = mock ? 'Independent front-end review' : 'Team service mode';
    $('catalogue-note').textContent = mock ? 'Prices follow the shared product list. Reduced prices are document examples; quantities are local review data.' : 'Prices, availability and reservation decisions are provided by the team service.';
    $('staff-mode-note').textContent = mock ? 'Staff review access: try adding a batch and confirming a collection. All changes remain on this device.' : 'Staff actions require server-side permission. Collection and stock changes are confirmed by the team service.';
    $('staff-nav').hidden = !mock;
}

function productImage(p) {
    const img = node('img');
    const name = String(p.name || '').toLowerCase().trim();

    let known = photos[name];

    if (name === 'apples') {
        const applePhotos = {
            17: 'apples',
            23: 'green-apples',
            24: 'mixed-apples'
        };

        known = applePhotos[Number(p.batch_id)] || 'apples';
    }

    img.src = known
        ? `assets/${known}.jpg`
        : 'assets/placeholder.svg';

    img.alt = `${p.name} — illustrative photograph`;
    img.loading = 'lazy';
    img.width = 900;
    img.height = 620;

    img.onerror = () => {
        img.onerror = null;
        img.src = 'assets/placeholder.svg';
    };

    return img;
}

function statusLabel(p) {
    if (p.reservation_message) return p.reservation_message;
    if (['expired', 'past_sell_by'].includes(p.status) || /EXPIRED/.test(p.reservation_status || '')) return 'Expired — reservations unavailable';
    if (p.quantity_available === 0) return 'Out of stock';
    if (!canReserve(p)) return 'Unavailable — reservations disabled';
    return `${p.quantity_available} available`;
}

function countdown(p) {
    const n = node('p', expiryText(p.sell_by_at), 'muted');
    n.dataset.expiry = p.sell_by_at || '';
    return n;
}

function prices(p) {
    const box = node('div', undefined, 'price');
    box.append(node('span', money(p.discounted_price_pence)));
    box.prepend(node('del', money(p.original_price_pence)));
    if (Number.isFinite(p.discount_percent)) box.append(node('small', p.discount_percent + '% off'));
    box.append(node('small', p.portion || 'per item'));
    return box;
}

function renderFilters() {
    const labels = [...new Set(products.map(p => p.category))];
    if (category !== 'all' && !labels.includes(category)) category = 'all';
    const box = $('filters');
    box.replaceChildren();
    for (const name of ['all', ...labels]) {
        const b = button(name === 'all' ? 'All food' : name, () => {
            category = name;
            renderFilters();
            renderProducts();
        }, 'filter' + (name === category ? ' selected' : ''));
        b.setAttribute('aria-pressed', String(name === category));
        box.append(b);
    }
}

function renderProducts() {
    const q = $('search').value.toLowerCase().trim();
    const shown = products.filter(p => (category === 'all' || p.category === category) && p.name.toLowerCase().includes(q));
    if ($('sort').value === 'price') shown.sort((a, b) => a.discounted_price_pence - b.discounted_price_pence);
    if ($('sort').value === 'quantity') shown.sort((a, b) => b.quantity_available - a.quantity_available);
    $('result-count').textContent = `${shown.length} ${shown.length === 1 ? 'item' : 'items'}${mock ? ' · Review selection' : ''}`;
    $('products').replaceChildren();
    renderStock();
    if (!shown.length) {
        $('products').append(node('p', products.length ? 'No matching food. Try a different search or category.' : 'No products to display.', 'empty'));
        return;
    }
    for (const p of shown) {
        const card = node('article', undefined, 'card'), photo = node('div', undefined, 'photo');
        photo.append(productImage(p), node('span', statusLabel(p), 'badge'));
        const body = node('div', undefined, 'card-body'), title = node('h3'),
            link = button(p.name, () => openDetails(p.batch_id), 'product-link');
        link.setAttribute('aria-label', 'View details for ' + p.name);
        title.append(link);
        body.append(node('span', p.category, 'category'), title, node('p', p.portion || 'See product details and allergen information.'));
        body.append(countdown(p));
        const bottom = node('div', undefined, 'card-bottom'),
            reserve = button(canReserve(p) ? 'Reserve ↗' : 'Unavailable', () => openDetails(p.batch_id), 'primary');
        reserve.disabled = !canReserve(p);
        reserve.setAttribute('aria-label', (canReserve(p) ? 'Reserve ' : 'View details for ') + p.name);
        bottom.append(prices(p), reserve);
        body.append(bottom);
        card.append(photo, body);
        $('products').append(card);
    }
    renderStock();
}

async function loadProducts() {
    const generation = ++productGeneration;
    feedback('catalogue-feedback', 'Loading the food selection…');
    $('products').setAttribute('aria-busy', 'true');
    try {
        const data = await service.products();
        if (generation !== productGeneration) return;
        products = data;
        renderFilters();
        renderProducts();
        feedback('catalogue-feedback', '');
    } catch (error) {
        if (generation !== productGeneration) return;
        products = [];
        renderFilters();
        renderProducts();
        feedback('catalogue-feedback', error.message, 'error', loadProducts);
        throw error;
    } finally {
        if (generation === productGeneration) $('products').setAttribute('aria-busy', 'false');
    }
}

function safe(fn) {
    return () => Promise.resolve().then(fn).catch(() => {
    });
}

function confirm(title, text, action) {
    $('confirm-title').textContent = title;
    $('confirm-copy').textContent = text;
    confirmAction = action;
    $('confirm-yes').disabled = false;
    $('confirm-dialog').showModal();
}

async function openDetails(id) {
    const generation = ++detailGeneration;
    const content = $('detail-content');
    content.replaceChildren(node('div', 'Loading product details…', 'detail-body'));
    $('details').showModal();
    try {
        const p = await service.product(id);
        if (generation !== detailGeneration || !$('details').open) return;
        content.replaceChildren();
        const image = productImage(p), body = node('div', undefined, 'detail-body'), title = node('h2', p.name);
        title.id = 'dialog-title';
        body.append(node('p', p.category, 'eyebrow'), title, prices(p), countdown(p), node('p', statusLabel(p)), node('p', 'Sell-by: ' + formatDate(p.sell_by_at)), node('p', 'Allergens: ' + (p.allergens_supplied ? (p.allergens.length ? p.allergens.join(', ') : 'None supplied in the record; check the original label.') : 'Not supplied. Ask collection staff and check the original label.')), node('p', 'Check the original product label for complete ingredients and allergen information.'), node('p', 'Collection location and time: confirm with campus collection staff.'), node('p', 'Illustrative photography. Actual packaging and portions may differ.', 'muted'));
        if (p.temperature_c !== undefined && p.temperature_c !== null) {
            body.append(node('p', `Recorded temperature: ${p.temperature_c}°C${p.temperature_source ? ' · ' + p.temperature_source : ''}. This is not a food-safety assessment.`));
        }
        const localFeedback = node('div');
        if (canReserve(p)) {
            const form = node('form'), row = node('div', undefined, 'quantity-row'), label = node('label', 'Quantity'),
                input = node('input');
            input.id = 'reserve-quantity';
            input.type = 'number';
            input.min = '1';
            input.max = String(p.quantity_available);
            input.step = '1';
            input.value = '1';
            input.required = true;
            label.htmlFor = input.id;
            row.append(label, input);
            const submit = node('button', 'Confirm reservation', 'primary');
            submit.type = 'submit';
            form.append(row, submit);
            form.onsubmit = async event => {
                event.preventDefault();
                if (locks.has('reserve')) return;
                if (!mock && !service.user) {
                    openAuth();
                    return;
                }
                try {
                    const count = quantity(Number(input.value));
                    if (count > p.quantity_available) throw new AppError('Choose a quantity within the displayed availability.', 'VALIDATION');
                    locks.add('reserve');
                    submit.disabled = true;
                    feedback(localFeedback, 'Saving reservation…');
                    await service.reserve(p.batch_id, count);
                    $('details').close();
                    toast(mock ? 'Review reservation saved on this device. No real food has been booked.' : 'Reservation confirmed by the team service.');
                    await Promise.allSettled([loadProducts(), loadReservations()]);
                    showMode();
                } catch (error) {
                    if (error.status === 401) renderAccount();
                    if (error.status === 409) {
                        loadProducts().catch(() => {
                        });
                        submit.disabled = true;
                        submit.textContent = 'Refresh product details';
                    }
                    feedback(localFeedback, error.message, 'error');
                    if (['NETWORK', 'TIMEOUT', 'INVALID_JSON', 'CONTRACT'].includes(error.code)) {
                        submit.textContent = 'Refresh details before retrying';
                    } else if (error.status !== 409) submit.disabled = false;
                } finally {
                    locks.delete('reserve');
                }
            };
            body.append(form);
        } else body.append(node('p', statusLabel(p), 'notice'));
        body.append(localFeedback);
        content.append(image, body);
    } catch (error) {
        if (generation !== detailGeneration || !$('details').open) return;
        content.replaceChildren();
        const b = node('div', undefined, 'detail-body');
        b.append(node('h2', 'Product details unavailable'));
        feedback(b, error.message, 'error', () => {
            $('details').close();
            openDetails(id);
        });
        content.append(b);
    }
}

function renderReservations() {
    const view = $('reservation-filter').value;
    const filtered = reservations.filter(r => view === 'all' || r.status.toLowerCase() === view || (view === 'reserved' && r.status.toLowerCase() === 'pending'));
    $('reservation-list').replaceChildren();
    $('reservation-count').textContent = reservations.filter(r => ['reserved', 'pending'].includes(String(r.status).toLowerCase())).length;
    if (!filtered.length) {
        const box = node('div', undefined, 'empty');
        box.append(node('h2', reservations.length ? 'No reservations in this view.' : 'Your next good find is waiting.'), node('p', !mock ? 'Your reservation history is retrieved securely from the FoodSave Smart service.' : 'Browse the selection and reserve food you would like to collect.'), button('Browse food', () => switchView('browse'), 'primary'));
        $('reservation-list').append(box);
        return;
    }
    for (const r of filtered) {
        const p = products.find(p => p.batch_id === r.batch_id);
        const status = String(r.status).toLowerCase(), box = node('article', undefined, 'info reservation'),
            info = node('div');
        info.append(node('span', status, 'badge ' + status), node('h2', r.name || p?.name || `Product ${r.batch_id}`), node('p', `Reference ${r.reservation_id} · Quantity ${r.quantity ?? 'not supplied'}`));
        if (Number.isInteger(r.price_pence)) info.append(node('p', money(r.price_pence) + ' per item at reservation'));
        if (r.created_at) info.append(node('p', 'Reserved ' + formatDate(r.created_at), 'muted'));
        if (['reserved', 'pending'].includes(status)) {
    info.append(node('p', 'Confirm collection location and opening times with campus staff.'));

    const cancel = button(
        'Cancel reservation',
        () => confirm(
            'Cancel this reservation?',
            `Release reservation ${r.reservation_id} for ${r.name || p?.name || 'this product'}?`,
            () => cancelReservation(r.reservation_id)
        )
    );

    cancel.setAttribute('aria-label', 'Cancel reservation ' + r.reservation_id);
    box.append(info, cancel);
} else {
    box.append(info);
}
        $('reservation-list').append(box);
    }
}

async function loadReservations() {
    if (!mock && !service.user) {
        reservations = [];
        renderReservations();
        feedback('reservations-feedback', '');
        return;
    }

    feedback('reservations-feedback', 'Loading reservations…');

    try {
        reservations = await service.reservations();
        renderReservations();
        feedback('reservations-feedback', '');
    } catch (error) {
        reservations = [];
        $('reservation-list').replaceChildren();
        $('reservation-count').textContent = '–';
        feedback('reservations-feedback', error.message, 'error', safe(loadReservations));
        throw error;
    }
}

async function cancelReservation(id) {
    if (locks.has('cancel-' + id)) return;
    locks.add('cancel-' + id);
    try {
        await service.cancel(id);
        toast(mock ? 'Review reservation cancelled.' : 'Cancellation confirmed by the team service.');
        await Promise.allSettled([loadProducts(), loadReservations()]);
    } catch (error) {
        feedback('reservations-feedback', error.message, 'error', safe(loadReservations));
    } finally {
        locks.delete('cancel-' + id);
    }
}

// The API exposes two independent streams in latest_readings. Display both;
// do not infer that the physical sensor is controlling the collection status.
function displayReadingTime(value) {
    if (typeof value !== 'string' || !value.trim()) return 'Not supplied';
    const raw = value.trim();
    // MySQL currently returns timestamps without an offset. Never guess a timezone.
    const plain = raw.match(/^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})(?::\d{2}(?:\.\d+)?)?$/);
    if (plain) return `${plain[3]}/${plain[2]}/${plain[1]} · ${plain[4]}:${plain[5]} (server time)`;
    const timestamp = Date.parse(raw);
    if (!Number.isFinite(timestamp)) return 'Timestamp unavailable';
    return new Intl.DateTimeFormat('en-GB', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        timeZoneName: 'short'
    }).format(new Date(timestamp));
}

function renderIoTReadings(data) {
    const panel = $('iot-monitor');
    if (!panel) return;
    panel.replaceChildren();
    const readings = data?.latest_readings && typeof data.latest_readings === 'object' ? data.latest_readings : {};
    const active = typeof data?.active_device_id === 'string' ? data.active_device_id : '';
    for (const device of [
        {
            id: 'esp32-01',
            title: 'Physical ESP32',
            eyebrow: 'REAL SENSOR · DHT11',
            badge: 'Physical reading',
            style: 'real',
            symbol: '◉'
        },
        {
            id: 'simulator-01',
            title: 'Temperature simulator',
            eyebrow: 'SOFTWARE · TEST DATA',
            badge: 'Simulated reading',
            style: 'sim',
            symbol: '⌁'
        }
    ]) {
        const raw = readings[device.id];
        const reading = raw && typeof raw === 'object' ? raw : null;
        const valid = reading?.sensor_status === 'ok' && typeof reading.temperature === 'number' && Number.isFinite(reading.temperature);
        const card = node('article', undefined, 'iot-reading-card iot-' + device.style);
        const top = node('div', undefined, 'iot-reading-top');
        const icon = node('span', device.symbol, 'iot-device-symbol');
        icon.setAttribute('aria-hidden', 'true');
        const heading = node('div', undefined, 'iot-device-title');
        heading.append(node('span', device.eyebrow, 'iot-device-eyebrow'), node('h3', device.title));
        top.append(icon, heading);
        const chip = node('span', device.badge, 'iot-type-chip');
        card.append(top, chip);
        const measure = node('div', undefined, 'iot-measure');
        if (valid) {
            measure.append(node('strong', reading.temperature.toFixed(1), 'iot-number'), node('span', '°C', 'iot-unit'));
        } else {
            measure.append(node('strong', '—', 'iot-number iot-empty'), node('span', '°C', 'iot-unit'));
        }
        card.append(measure);
        const condition = node('div', undefined, 'iot-reading-condition');
        const dot = node('span', undefined, 'iot-condition-dot');
        dot.setAttribute('aria-hidden', 'true');
        let status;
        if (!reading) status = 'Awaiting first reading';
        else if (reading.sensor_status === 'error') status = 'Sensor error reported';
        else if (valid) status = 'Sensor OK · Reading received';
        else status = 'Reading unavailable';
        condition.className += ' ' + (valid ? 'iot-condition-ok' : reading ? 'iot-condition-error' : 'iot-condition-idle');
        condition.append(dot, node('span', status));
        card.append(condition);
        const foot = node('div', undefined, 'iot-reading-footer');
        const timeBox = node('div', undefined, 'iot-reading-time');
        timeBox.append(node('span', 'LAST READING', 'iot-small-label'), node('span', displayReadingTime(reading?.received_at), 'iot-time-value'));
        foot.append(timeBox);
        if (active === device.id) foot.append(node('span', 'Controls collection status', 'iot-active-label'));
        card.append(foot);
        panel.append(card);
    }
}

async function loadFridge() {
    const monitor = $('iot-monitor');
    if (monitor) monitor.setAttribute('aria-busy', 'true');
    feedback('fridge-content', 'Loading fridge updates…');
    try {
        const data = await service.fridge(), box = $('fridge-content');
        renderIoTReadings(data);
        box.replaceChildren();
        const state = String(data.safety_state || '').toUpperCase();
        if (!data.connected || !['OK', 'HOLD', 'LOCKED'].includes(state)) {
            box.append(node('span', 'Status unavailable', 'badge'), node('p', data.hold_reason || 'The service has not supplied a recognised fridge status.'));
        } else {
            box.append(node('span', state === 'OK' ? 'Available for collection' : 'Collection on hold', 'badge'), node('p', state === 'OK' ? 'The connected service reports normal collection status.' : 'The connected service has blocked collection.'), node('p', data.hold_reason || 'Follow collection staff’s instructions.'));
        }
        if (data.active_device_id) {
            const source = data.active_device_id === 'simulator-01' ? 'Simulator test data' : data.active_device_id === 'esp32-01' ? 'Physical ESP32 readings' : 'Device ' + data.active_device_id;
            box.append(node('p', 'Status source: ' + source + '.', 'iot-status-source'));
        }
        if (data.updated_at) box.append(node('p', 'Last reported: ' + formatDate(data.updated_at), 'last-updated'));
    } catch (error) {
        if (monitor) {
            monitor.replaceChildren();
            const box = node('div', undefined, 'iot-unavailable');
            box.append(node('strong', 'Monitoring data unavailable'), node('p', 'Could not retrieve temperature readings from the team API. Refresh to try again.'));
            monitor.append(box);
        }
        feedback('fridge-content', error.message, 'error', loadFridge);
    } finally {
        if (monitor) monitor.setAttribute('aria-busy', 'false');
    }
}

async function loadAlerts() {
    feedback('alerts-content', 'Loading alerts…');
    try {
        const alerts = await service.alerts();
        $('alerts-content').replaceChildren();
        if (!alerts.length) {
            $('alerts-content').append(node('p', 'No alerts reported by this data source.'));
            return;
        }
        for (const alert of alerts) {
            const article = node('article', undefined, 'alert-item');
            article.append(node('strong', String(alert.type || alert.alert_type || 'Update').replaceAll('_', ' ')), node('p', typeof alert.message === 'string' ? alert.message : 'No message supplied.'));
            if (alert.batch_id) article.append(node('span', 'Product reference ' + alert.batch_id, 'muted'));
            $('alerts-content').append(article);
        }
    } catch (error) {
        feedback('alerts-content', error.message, 'error', loadAlerts);
    }
}

function renderStock() {
    const box = $('staff-stock');
    box.replaceChildren();
    if (!products.length) {
        box.append(node('p', 'Stock unavailable. Refresh the workspace.', 'muted'));
        return;
    }
    for (const p of products) {
        const row = node('div', undefined, 'stock-row');
        row.append(node('span', p.name), node('span', `${p.quantity_available} · ${statusLabel(p)}`));
        box.append(row);
    }
}

async function loadReports() {
    feedback('staff-reports', 'Loading collection totals…');
    try {
        const r = await service.reports();
        if (!Number.isSafeInteger(r.collected_units) || r.collected_units < 0) throw new AppError('The service did not supply valid collection totals.', 'CONTRACT');
        $('staff-reports').replaceChildren();
        for (const [label, value] of [['Units collected', String(r.collected_units)], ['Original value collected', typeof r.estimated_original_value_gbp === 'number' ? money(Math.round(r.estimated_original_value_gbp * 100)) : 'Not supplied'], ['Sales value collected', typeof r.estimated_sales_value_gbp === 'number' ? money(Math.round(r.estimated_sales_value_gbp * 100)) : 'Not supplied']]) {
            const stat = node('div', undefined, 'stat');
            stat.append(node('span', label), node('strong', value));
            $('staff-reports').append(stat);
        }
    } catch (error) {
        feedback('staff-reports', error.message, 'error', loadReports);
    }
}

function fillCategories() {
    const select = $('batch-category');
    select.replaceChildren();
    for (const cat of config.CATEGORIES || []) {
        const o = node('option', cat.name);
        o.value = String(cat.category_id);
        select.append(o);
    }
    if (!select.children.length) {
        $('save-batch').disabled = true;
        feedback('batch-feedback', 'Staff categories have not been configured.', 'error');
    }
}

async function saveBatch(event) {
    event.preventDefault();
    if (locks.has('create')) return;
    try {
        const categoryId = Number($('batch-category').value),
            cat = config.CATEGORIES.find(c => c.category_id === categoryId);
        const form = {
            name: $('batch-name').value,
            category_id: categoryId,
            category_name: cat?.name,
            original_price_pence: priceInputToPence($('batch-price').value),
            quantity_available: quantity(Number($('batch-quantity').value)),
            sell_by_at: new Date($('batch-date').value).toISOString(),
            allergens: $('batch-allergens').value.split(',').map(s => s.trim()).filter(Boolean)
        };
        locks.add('create');
        $('save-batch').disabled = true;
        $('add-batch').setAttribute('aria-busy', 'true');
        feedback('batch-feedback', 'Saving food batch…');
        const result = await service.createProduct(form);
        $('add-batch').reset();
        feedback('batch-feedback', `Batch ${result.batch_id} saved${mock ? ' in the local review' : ''}.`, 'success');
        await Promise.allSettled([loadProducts(), loadAlerts()]);
        showMode();
        $('save-batch').disabled = false;
    } catch (error) {
        feedback('batch-feedback', error.message || 'Check the entered values.', 'error');
        if (!['NETWORK', 'TIMEOUT', 'INVALID_JSON', 'CONTRACT'].includes(error.code)) $('save-batch').disabled = false;
    } finally {
        locks.delete('create');
        $('add-batch').setAttribute('aria-busy', 'false');
    }
}

function reviewCollection(event) {
    event.preventDefault();
    if (locks.has('collect')) return;
    const id = Number($('collection-id').value);
    if (!Number.isSafeInteger(id) || id < 1) {
        feedback('collection-feedback', 'Enter a valid reservation reference.', 'error');
        return;
    }
    const r = reservations.find(r => r.reservation_id === id);
    confirm('Record this collection?', `Confirm collection of reservation ${id}${r ? ' · ' + r.quantity + ' item(s) for ' + (r.name || 'product ' + r.batch_id) : ''}. The service will check whether the reservation can be collected.`, () => collect(id));
}

async function collect(id) {
    if (locks.has('collect')) return;
    locks.add('collect');
    $('collect-button').disabled = true;
    $('collect-form').setAttribute('aria-busy', 'true');
    feedback('collection-feedback', 'Recording collection…');
    try {
        await service.collect(id);
        feedback('collection-feedback', `Collection for reservation ${id} confirmed${mock ? ' in the local review' : ''}.`, 'success');
        $('collect-form').reset();
        await Promise.allSettled([loadProducts(), loadReservations(), loadReports()]);
        $('collect-button').disabled = false;
    } catch (error) {
        feedback('collection-feedback', error.message, 'error');
        if (!['NETWORK', 'TIMEOUT', 'INVALID_JSON', 'CONTRACT'].includes(error.code)) $('collect-button').disabled = false;
    } finally {
        locks.delete('collect');
        $('collect-form').setAttribute('aria-busy', 'false');
    }
}

async function switchView(view, focus = true) {
    if (!['browse', 'reservations', 'status', 'staff'].includes(view)) view = 'browse';
    if (view === 'staff' && !mock) view = 'browse';
    activeView = view;
    document.querySelectorAll('.view').forEach(v => v.hidden = v.id !== view);
    document.querySelectorAll('.nav').forEach(b => {
        b.classList.toggle('active', b.dataset.view === view);
        if (b.dataset.view === view) b.setAttribute('aria-current', 'page'); else b.removeAttribute('aria-current');
    });
    history.replaceState(null, '', '#' + view);
    window.scrollTo({top: 0, behavior: 'instant'});
    if (focus) {
        const heading = $(view).querySelector('h1');
        if (heading) {
            heading.tabIndex = -1;
            heading.focus({preventScroll: true});
        }
    }
    if (view === 'reservations') await Promise.allSettled([loadReservations()]);
    if (view === 'status') await Promise.allSettled([loadFridge(), loadAlerts()]);
    if (view === 'staff') await Promise.allSettled([loadReports(), loadProducts()]);
}

function bind() {
    document.querySelectorAll('.nav').forEach(b => b.onclick = () => switchView(b.dataset.view));
    document.querySelectorAll('.brand').forEach(a => a.onclick = e => {
        e.preventDefault();
        switchView('browse');
    });
    $('search').oninput = renderProducts;
    $('sort').onchange = renderProducts;
    $('reservation-filter').onchange = renderReservations;
    $('refresh-reservations').onclick = safe(loadReservations);
    $('refresh-status').onclick = () => Promise.allSettled([loadFridge(), loadAlerts()]);
        bindSimulator();
    $('refresh-staff').onclick = async () => {
        await Promise.allSettled([loadProducts(), loadReports(), loadReservations()]);
        $('save-batch').disabled = false;
        $('collect-button').disabled = false;
    };
    $('add-batch').onsubmit = saveBatch;
    $('collect-form').onsubmit = reviewCollection;
    document.querySelector('.close').onclick = () => {
        detailGeneration++;
        $('details').close();
    };
    $('details').addEventListener('close', () => detailGeneration++);
    $('confirm-no').onclick = () => {
        confirmAction = null;
        $('confirm-dialog').close();
    };
    $('confirm-yes').onclick = async () => {
        const action = confirmAction;
        confirmAction = null;
        $('confirm-yes').disabled = true;
        $('confirm-dialog').close();
        if (action) await action();
    };
    $('confirm-dialog').addEventListener('cancel', () => confirmAction = null);
}

function renderAccount() {
    const user = service.user;
    $('account-button').textContent = user ? 'Sign out — ' + user.display_name : 'Sign in';
    $('auth-note').textContent = user ? 'Signed in as ' + user.display_name : 'Sign in to reserve food.';
        updateSimulatorControls();
}

function openAuth() {
    if (!$('auth-dialog').open) $('auth-dialog').showModal();
}
function updateSimulatorControls() {
    const user = service.user;
    const authorised = !mock && ['ADMIN', 'STAFF'].includes(user?.role);

    $('sim-45').disabled = !authorised;
    $('sim-245').disabled = !authorised;
    $('sim-signin').hidden = authorised;

    $('sim-control-note').textContent = authorised
        ? 'Staff access confirmed. Choose a test temperature.'
        : user
            ? 'Only staff and administrators can control the simulator.'
            : 'Sign in with an authorised staff account to control demo temperatures.';
}

async function setSimulatorTemperature(temperature) {
    const safeButton = $('sim-45');
    const holdButton = $('sim-245');

    safeButton.disabled = true;
    holdButton.disabled = true;

    feedback('sim-control-feedback', 'Updating simulator temperature...');

    try {
        const result = await service.setSimulatorTemperature(temperature);

        feedback(
            'sim-control-feedback',
            `Simulator updated to ${temperature}°C. Fridge status: ${result.fridge_status}.`,
            'success'
        );

        await Promise.allSettled([loadFridge(), loadAlerts(), loadProducts()]);

        window.dispatchEvent(new Event('foodsave:simulator-updated'));
    } catch (error) {
        feedback('sim-control-feedback', error.message, 'error');
    } finally {
        updateSimulatorControls();
    }
}

function bindSimulator() {
    $('sim-signin').onclick = () => {
        if (service.user) {
            feedback(
                'sim-control-feedback',
                'Sign out and use an authorised staff account.',
                'error'
            );
        } else {
            openAuth();
        }
    };

    $('sim-45').onclick = () => setSimulatorTemperature(4.5);
    $('sim-245').onclick = () => setSimulatorTemperature(24.5);

    updateSimulatorControls();
}

function bindAuth() {
    $('account-button').hidden = mock;
    if (mock) return;
    renderAccount();
    $('account-button').onclick = () => {
        if (service.user) {
            service.logout();
            renderAccount();
            loadReservations().catch(() => {
            });
            toast('Signed out.');
        } else openAuth();
    };
    $('auth-close').onclick = () => $('auth-dialog').close();
    $('auth-form').onsubmit = async event => {
        event.preventDefault();
        const submit = $('auth-submit');
        submit.disabled = true;
        feedback('auth-feedback', 'Signing in…');
        try {
            await service.login($('auth-email').value.trim(), $('auth-password').value);
            $('auth-password').value = '';
            renderAccount();
            await loadReservations();
            $('auth-dialog').close();
            toast('Signed in. You can now confirm your reservation.');
        } catch (error) {
            feedback('auth-feedback', error.message, 'error');
        } finally {
            submit.disabled = false;
        }
    };
    $('register-form').onsubmit = async event => {
        event.preventDefault();
        const submit = $('register-submit');
        submit.disabled = true;
        feedback('register-feedback', 'Creating account…');
        try {
            await service.register($('register-name').value.trim(), $('register-email').value.trim(), $('register-password').value);
            $('register-password').value = '';
            feedback('register-feedback', 'Account created. Sign in above to continue.', 'success');
        } catch (error) {
            feedback('register-feedback', error.message, 'error');
        } finally {
            submit.disabled = false;
        }
    };
    $('auth-dialog').addEventListener('close', () => {
        $('auth-password').value = '';
        $('register-password').value = '';
    });
}

async function init() {
    try {
        if (!config || !['mock', 'api'].includes(config.MODE)) throw new AppError('The website data source has not been configured.', 'CONFIG');
        if (mock) {
            let seed = window.FOODSAVE_SEED;
            if (!seed) {
                const response = await fetch('mocks/products.json');
                if (!response.ok) throw new AppError('The review product file could not be loaded.', 'CONFIG');
                seed = await response.json();
            }
            let storage;
            try {
                storage = window.localStorage;
            } catch {
            }
            service = createMockService(seed.products, {storage});
        } else service = createApi(config);
        showMode();
        fillCategories();
        bind();
        bindAuth();
if (!mock) {
    $('reservation-scope').hidden = false;
    $('reservation-scope').textContent =
        'Your reservation history is retrieved securely from the FoodSave Smart service. You can cancel pending reservations below.';

    setInterval(() => {
        document.querySelectorAll('[data-expiry]').forEach(n => {
            n.textContent = expiryText(n.dataset.expiry);
        });
    }, 30000);

    setInterval(() => {
        if (activeView === 'status') {
            loadFridge().catch(() => {});
        }
    }, 30000);
}
        await Promise.allSettled([loadProducts(), loadReservations()]);
        await switchView(location.hash.slice(1) || 'browse', false);
    } catch (error) {
        $('mode-banner').textContent = 'FoodSave Smart · Connection setup required';
        feedback('catalogue-feedback', error.message, 'error', () => location.reload());
    }
}

export const ready = init();
