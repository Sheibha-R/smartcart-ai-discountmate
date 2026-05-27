
let currentRecommendedProduct = null;
let cart = [];
let selectedPlan = null;
let selectedPlanId = null;
let activeUsageBonus = 0;
let appliedCouponDiscount = 0;
let currentUser = null;
let wizardStep = 1;
let wizardSteps = [1, "final"];

async function fetchJson(url, options = {}) {
    const response = await fetch(url, options);
    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.message || data.error || "Request failed");
    }

    return data;
}

function money(value) {
    return `$${Number(value || 0).toFixed(2)}`;
}

function titleCase(value) {
    return value ? value.charAt(0).toUpperCase() + value.slice(1) : "";
}

function showPopup(message, type = "success") {
    const popup = document.getElementById("popup");
    popup.textContent = message;
    popup.className = `popup show ${type}`;

    setTimeout(() => {
        popup.className = "popup";
    }, 3200);
}

function openModal(id) {
    document.getElementById(id).classList.add("modal-open");
}

function closeModal(id) {
    document.getElementById(id).classList.remove("modal-open");
}

async function openSignup() {
    ["signupName", "signupEmail", "signupPassword", "signupConfirmPassword", "signupCaptchaInput"].forEach((id) => {
        document.getElementById(id).value = "";
    });

    document.getElementById("signupMessage").textContent = "";
    await loadSignupCaptcha();
    openModal("signupModal");
}

function openLogin() {
    ["loginEmail", "loginPassword", "recoveryEmail"].forEach((id) => {
        document.getElementById(id).value = "";
    });

    document.getElementById("loginMessage").textContent = "";
    document.getElementById("forgotPasswordBox").classList.add("hidden");
    openModal("loginModal");
}

async function loadSignupCaptcha() {
    const data = await fetchJson("/captcha");
    document.getElementById("signupCaptchaDisplay").textContent = data.captcha;
    document.getElementById("signupCaptchaInput").value = "";
}

async function loadMembershipCaptcha() {
    const data = await fetchJson("/captcha");
    document.getElementById("membershipCaptchaDisplay").textContent = data.captcha;
    document.getElementById("membershipCaptchaInput").value = "";
}

async function loadSessionUser() {
    const data = await fetchJson("/session-user");
    currentUser = data.user;
    updateUserInterface();
}

function userHasLocationPlan() {
    return currentUser && currentUser.membership && ["basic", "plus"].includes(currentUser.membership.plan_id);
}

function userHasPremiumPlan() {
    return currentUser && currentUser.membership && currentUser.membership.plan_id === "premium";
}

function updateUserInterface() {
    const authButtons = document.getElementById("authButtons");
    const logoutButtons = document.getElementById("logoutButtons");
    const profileInfo = document.getElementById("profileInfo");
    const locationCard = document.getElementById("locationBenefitsCard");
    const premiumCard = document.getElementById("premiumFamilyCard");

    locationCard.classList.add("hidden");
    premiumCard.classList.add("hidden");

    if (!currentUser) {
        authButtons.classList.remove("hidden");
        logoutButtons.classList.add("hidden");

        profileInfo.innerHTML = "Not logged in.";

        locationCard.classList.add("hidden");
        premiumCard.classList.add("hidden");

        activeUsageBonus = 0;
        appliedCouponDiscount = 0;

        renderCart();
        return;
    }

    authButtons.classList.add("hidden");
    logoutButtons.classList.remove("hidden");

    const membership = currentUser.membership
        ? `${currentUser.membership.plan_name} (${currentUser.membership.discount}% discount)`
        : "No active plan";

    const locationText = {
        while_using: "Access location only while using app",
        always: "Access location always even when app not used",
        off: "Location off"
    };

    profileInfo.innerHTML = `
        <div class="profile-line"><span>Name</span><strong>${currentUser.name}</strong></div>
        <div class="profile-line"><span>Email</span><strong>${currentUser.email}</strong></div>
        <div class="profile-line"><span>Membership</span><strong>${membership}</strong></div>
        <div class="profile-line"><span>App usage count</span><strong>${currentUser.usage_count}</strong></div>
    `;

    if (userHasLocationPlan()) {
        locationCard.classList.remove("hidden");
        document.getElementById("locationPreference").value = currentUser.location_access || "off";
        profileInfo.innerHTML += `
            <div class="profile-line"><span>Location</span><strong>${locationText[currentUser.location_access] || "Location off"}</strong></div>
        `;
    }
    if (userHasPremiumPlan()) {
        premiumCard.classList.remove("hidden");

        if (currentUser.family_profile && currentUser.family_profile.length > 0) {
            profileInfo.innerHTML += `
                <h4>Family Profile</h4>
                ${currentUser.family_profile.map((person, index) => `
                    <div class="family-profile-row">
                        <span>${person.name}, ${person.age} years · ${person.routine} · ${person.lifestyle}</span>
                        <button class="remove-family-btn" onclick="removeFamilyMember(${index})">Remove</button>
                    </div>
                `).join("")}
            `;
        }
    }

    renderCart();
}

function selectBestProduct(products, priority) {
    if (priority === "discount") {
        return [...products].sort((a, b) => b.discount_percentage - a.discount_percentage)[0];
    }

    if (priority === "rating") {
        return [...products].sort((a, b) => b.rating - a.rating)[0];
    }

    return [...products].sort((a, b) => a.price - b.price)[0];
}

function renderSummary(compareData, chosenBest) {
    document.getElementById("summaryCards").innerHTML = `
        <div class="summary-card"><span>Recommended Price</span><strong>${money(chosenBest.price)}</strong></div>
        <div class="summary-card"><span>Estimated Saving</span><strong>${money(compareData.estimated_saving)}</strong></div>
        <div class="summary-card"><span>Stores Checked</span><strong>${compareData.stores_checked}</strong></div>
        <div class="summary-card"><span>Rating</span><strong>${chosenBest.rating}/5</strong></div>
    `;
}

function renderComparison(compareData, priority) {
    const chosenBest = selectBestProduct(compareData.results, priority);
    currentRecommendedProduct = chosenBest;
    activeUsageBonus = compareData.usage_bonus || 0;

    const container = document.getElementById("comparisonResults");
    container.innerHTML = "";

    compareData.results.forEach((product) => {
        const isBest = product.id === chosenBest.id;
        const card = document.createElement("article");

        card.className = isBest ? "product-card best" : "product-card";

        card.innerHTML = `
            ${isBest ? "<div class='best-ribbon'>Recommended</div>" : ""}
            <div class="product-emoji">${product.image}</div>
            <h4>${product.brand}</h4>
            <p><strong>Store:</strong> ${product.store}</p>
            <p><strong>Category:</strong> ${product.category}</p>
            <p><strong>Diet:</strong> ${product.diet}</p>
            <p><strong>Weight:</strong> ${product.weight}</p>
            <p><strong>Calories:</strong> ${product.calories} kcal</p>
            <div class="price-line">
                <span class="price">${money(product.price)}</span>
                <span class="old-price">${money(product.previous_price)}</span>
            </div>
            <span class="discount-pill">${product.discount_percentage}% off</span>
            <span class="recommendation-pill">${product.recommendation}</span>
            <p><strong>Rating:</strong> ${product.rating}/5</p>
            <p><strong>Saving:</strong> ${money(product.saving)}</p>
            <button class="mini-cart-btn" onclick='addToCart(${JSON.stringify(product)})'>Add This Product</button>
        `;

        container.appendChild(card);
    });

    renderNearbyStores(compareData.nearby_store_search);
    renderUsageBonus(compareData.usage_bonus);
    renderPremiumGuidance();

    return chosenBest;
}

function renderSubstitute(data) {
    const product = data.recommended_substitute;

    document.getElementById("substituteBox").innerHTML = `
        <h3>Smart Substitute</h3>
        <p>Choose <strong>${product.brand}</strong> from <strong>${product.store}</strong> for <strong>${money(product.price)}</strong>.</p>
        <p>${data.reason}</p>
    `;
}

function renderDiscount(data) {
    const best = [...data.discount_predictions].sort((a, b) => b.discount_percentage - a.discount_percentage)[0];

    document.getElementById("discountBox").innerHTML = `
        <h3>Discount Prediction</h3>
        <p>Best discount: <strong>${best.brand}</strong> from <strong>${best.store}</strong>.</p>
        <p>Discount: <strong>${best.discount_percentage}%</strong> | Advice: <strong>${best.recommendation}</strong> | Confidence: <strong>${best.confidence}</strong></p>
    `;
}

function renderNearbyStores(nearbyData) {
    const box = document.getElementById("nearbyStoresBox");

    if (!nearbyData || !nearbyData.visible) {
        box.classList.add("hidden");
        return;
    }

    box.classList.remove("hidden");

    if (!nearbyData.enabled) {
        box.innerHTML = `<h3>Nearby Store Search</h3><p>${nearbyData.message}</p>`;
        return;
    }

    box.innerHTML = `
        <h3>Nearby Stores and Local Discounts</h3>
        <p>${nearbyData.message}</p>
        <div class="nearby-grid">
            ${nearbyData.stores.map((store) => `
                <div class="nearby-card">
                    <strong>${store.store}</strong>
                    <span>${store.brand}</span>
                    <span>${money(store.price)} · ${store.discount_percentage}% off</span>
                    <span>${store.distance} km away · ${store.eta}</span>
                </div>
            `).join("")}
        </div>
    `;
}

function renderUsageBonus(bonus) {
    const box = document.getElementById("usageBonusBox");

    if (!currentUser || !currentUser.membership || currentUser.membership.plan_id !== "plus") {
        box.classList.add("hidden");
        return;
    }

    box.classList.remove("hidden");

    if (bonus) {
        box.innerHTML = `<h3>Usage-Based Bonus Active</h3><p>You have unlocked an extra <strong>${bonus}%</strong> Smart Plus app discount.</p>`;
    } else {
        box.innerHTML = `<h3>Usage-Based Bonus</h3><p>Smart Plus members receive extra app discounts as their usage increases.</p>`;
    }

    renderCart();
}

async function renderPremiumGuidance() {
    const box = document.getElementById("premiumGuidanceBox");

    if (!userHasPremiumPlan()) {
        box.classList.add("hidden");
        return;
    }

    box.classList.remove("hidden");

    try {
        const data = await fetchJson("/premium-guidance");

        if (!data.enabled || data.recommendations.length === 0) {
            box.innerHTML = `<h3>AI Premium Meal and Wellness Guidance</h3><p>${data.message}</p>`;
            return;
        }

        box.innerHTML = `
            <h3>AI Premium Meal and Wellness Guidance</h3>
            <p>${data.message}</p>
            <div class="premium-recommendation-grid">
                ${data.recommendations.map((item) => `
                    <div class="premium-recommendation-card">
                        <h4>${item.image} ${item.person}</h4>
                        <p><strong>Routine:</strong> ${item.routine}</p>
                        <p><strong>Lifestyle:</strong> ${item.lifestyle}</p>
                        <p><strong>Recommended food:</strong> ${item.product} (${item.diet})</p>
                        <p><strong>Food match:</strong> ${item.meal_fit}</p>
                        <p><strong>Weight:</strong> ${item.weight}</p>
                        <p><strong>Calories:</strong> ${item.calories} kcal</p>
                        <p><strong>Wellness:</strong> ${item.wellness_tip}</p>
                    </div>
                `).join("")}
            </div>
        `;
    } catch (error) {
        box.innerHTML = `<h3>AI Premium Meal and Wellness Guidance</h3><p>${error.message}</p>`;
    }
}

async function runSmartCart() {
    const item = document.getElementById("itemSelect").value;
    const priority = document.getElementById("prioritySelect").value;
    const statusBox = document.getElementById("statusBox");

    try {
        statusBox.textContent = "Analysing prices, discounts and recommended options...";

        const compareData = await fetchJson(`/compare?item=${encodeURIComponent(item)}`);
        const substituteData = await fetchJson(`/substitute?item=${encodeURIComponent(item)}`);
        const discountData = await fetchJson(`/predict-discount?item=${encodeURIComponent(item)}`);

        if (compareData.user) {
            currentUser = compareData.user;
            updateUserInterface();
        }

        document.getElementById("resultTitle").textContent = `Results for ${titleCase(item)}`;

        const chosenBest = renderComparison(compareData, priority);
        renderSummary(compareData, chosenBest);
        renderSubstitute(substituteData);
        renderDiscount(discountData);

        statusBox.textContent = `Recommendation generated successfully for ${titleCase(item)}.`;
    } catch (error) {
        statusBox.textContent = error.message;
    }
}

function addRecommendedToCart() {
    if (!currentRecommendedProduct) {
        showPopup("Please analyse a product first.", "error");
        return;
    }

    addToCart(currentRecommendedProduct);
}

function addToCart(product) {
    const existing = cart.find((item) => item.id === product.id);

    if (existing) {
        existing.quantity += 1;
    } else {
        cart.push({ ...product, quantity: 1 });
    }

    appliedCouponDiscount = 0;
    renderCart();
    showPopup(`${product.brand} added to cart.`);
}

function removeCartItem(productId) {
    cart = cart.filter((item) => item.id !== productId);
    appliedCouponDiscount = 0;
    renderCart();
}

function updateQuantity(productId, quantity) {
    const item = cart.find((cartItem) => cartItem.id === productId);

    if (!item) {
        return;
    }

    item.quantity = Number(quantity);

    if (item.quantity <= 0) {
        removeCartItem(productId);
    }

    appliedCouponDiscount = 0;
    renderCart();
}

function calculateCartTotal() {
    return cart.reduce((total, item) => total + item.price * item.quantity, 0);
}

function calculateRecommendedTotal() {
    const grouped = {};

    cart.forEach((item) => {
        if (!grouped[item.item]) {
            grouped[item.item] = [];
        }

        grouped[item.item].push(item);
    });

    let total = 0;

    Object.values(grouped).forEach((items) => {
        const cheapest = [...items].sort((a, b) => a.price - b.price)[0];
        const quantity = items.reduce((sum, item) => sum + item.quantity, 0);
        total += cheapest.price * quantity;
    });

    return total;
}

function renderCart() {
    const cartItems = document.getElementById("cartItems");
    const rawTotal = calculateCartTotal();
    const recommendedTotal = calculateRecommendedTotal();

    const memberPercent = currentUser && currentUser.membership ? currentUser.membership.discount : 0;
    const usagePercent = currentUser && currentUser.membership && currentUser.membership.plan_id === "plus" ? activeUsageBonus : 0;

    const memberDiscount = rawTotal * memberPercent / 100;
    const usageDiscount = rawTotal * usagePercent / 100;
    const finalTotal = Math.max(rawTotal - memberDiscount - usageDiscount - appliedCouponDiscount, 0);
    const potentialSaving = Math.max(rawTotal - recommendedTotal + memberDiscount + usageDiscount + appliedCouponDiscount, 0);

    if (cart.length === 0) {
        cartItems.innerHTML = `<div class="empty-cart">🛒 Your cart is empty. Add products from the dashboard.</div>`;
    } else {
        cartItems.innerHTML = cart.map((item) => `
            <div class="cart-item">
                <div class="cart-product">
                    <span>${item.image}</span>
                    <div>
                        <h4>${item.brand}</h4>
                        <p>${item.store} · ${titleCase(item.item)} · ${money(item.price)}</p>
                    </div>
                </div>
                <div class="cart-actions">
                    <input type="number" min="1" value="${item.quantity}" onchange="updateQuantity(${item.id}, this.value)">
                    <strong>${money(item.price * item.quantity)}</strong>
                    <button onclick="removeCartItem(${item.id})">Remove</button>
                </div>
            </div>
        `).join("");
    }

    document.getElementById("rawCartTotal").textContent = money(rawTotal);
    document.getElementById("cartTotal").textContent = money(finalTotal);
    document.getElementById("recommendedTotal").textContent = money(recommendedTotal);
    document.getElementById("potentialSaving").textContent = money(potentialSaving);

    const memberRow = document.getElementById("memberDiscountRow");
    const usageRow = document.getElementById("usageBonusRow");
    const couponRow = document.getElementById("couponDiscountRow");

    if (memberPercent > 0) {
        memberRow.classList.remove("hidden");
        document.getElementById("memberDiscountLabel").textContent = `${currentUser.membership.plan_name} discount (${memberPercent}%)`;
        document.getElementById("memberDiscountValue").textContent = money(memberDiscount);
    } else {
        memberRow.classList.add("hidden");
    }

    if (usagePercent > 0) {
        usageRow.classList.remove("hidden");
        document.getElementById("usageBonusValue").textContent = money(usageDiscount);
    } else {
        usageRow.classList.add("hidden");
    }

    if (appliedCouponDiscount > 0) {
        couponRow.classList.remove("hidden");
        document.getElementById("couponDiscountValue").textContent = money(appliedCouponDiscount);
    } else {
        couponRow.classList.add("hidden");
    }

    document.getElementById("heroCartCount").textContent = cart.reduce((sum, item) => sum + item.quantity, 0);
    document.getElementById("heroCartValue").textContent = money(finalTotal);
    document.getElementById("heroSaving").textContent = money(potentialSaving);

    renderSavingsReport();
}

function clearCart() {
    cart = [];
    appliedCouponDiscount = 0;
    document.getElementById("couponMessage").textContent = "";
    renderCart();
    showPopup("Cart cleared.");
}

async function applyCoupon() {
    const code = document.getElementById("couponInput").value.trim();
    const total = calculateCartTotal();

    if (cart.length === 0) {
        showPopup("Add items before applying a coupon.", "error");
        return;
    }

    if (!code) {
        showPopup("Please enter a coupon code.", "error");
        return;
    }

    try {
        const data = await fetchJson("/apply-coupon", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ code, total })
        });

        appliedCouponDiscount = data.discount;
        document.getElementById("couponMessage").textContent = `${data.code} accepted: ${data.description}. Discount applied: ${money(data.discount)}.`;

        renderCart();
        showPopup("Coupon applied successfully.");
    } catch (error) {
        document.getElementById("couponMessage").textContent = error.message;
        showPopup(error.message, "error");
    }
}

function openCheckout() {
    if (cart.length === 0) {
        showPopup("Your cart is empty.", "error");
        return;
    }

    document.getElementById("checkoutMessage").textContent = "";
    openModal("checkoutModal");
}

function completeCheckout() {
    const method = document.getElementById("checkoutPaymentMethod").value;
    const name = document.getElementById("checkoutName").value.trim();
    const number = document.getElementById("checkoutNumber").value.trim();

    const checkoutMessage = document.getElementById("checkoutMessage");

    // Empty validation
    if (!name || !number) {
        checkoutMessage.textContent =
            "Please enter all payment details.";
        showPopup("Please enter all payment details.", "error");
        return;
    }

    // Card ending 0000 validation
    if (number.endsWith("0000")) {
        checkoutMessage.textContent =
            "Payment rejected. Card or account number cannot end with 0000.";
        showPopup(
            "Payment rejected. Card or account number cannot end with 0000.",
            "error"
        );
        return;
    }

    // Minimum length validation
    if (number.length < 8) {
        checkoutMessage.textContent =
            "Payment rejected. Please enter a valid card/account number.";
        showPopup(
            "Payment rejected. Please enter a valid card/account number.",
            "error"
        );
        return;
    }

    // Success
    checkoutMessage.textContent =
        `Payment successful using ${method}.`;

    showPopup("Payment successful.");

    setTimeout(() => {
        closeModal("checkoutModal");
    }, 1200);
}

async function loadOffers() {
    const data = await fetchJson("/api/offers");
    const grid = document.getElementById("offersGrid");

    grid.innerHTML = data.offers.map((offer) => `
        <article class="offer-card">
            <div class="offer-icon">🏷️</div>
            <h3>${offer.title}</h3>
            <p>${offer.description}</p>
            <span>Valid until: ${offer.valid_until}</span>
        </article>
    `).join("");

    if (data.usage_bonus) {
        grid.innerHTML += `
            <article class="offer-card">
                <div class="offer-icon">⭐</div>
                <h3>Smart Plus Usage Reward</h3>
                <p>You unlocked an extra ${data.usage_bonus}% app discount because of frequent usage.</p>
                <span>Active now</span>
            </article>
        `;
    }
}

async function loadPlans() {
    const data = await fetchJson("/api/membership-plans");
    const grid = document.getElementById("plansGrid");

    grid.innerHTML = data.plans.map((plan) => `
        <article class="plan-card">
            <h3>${plan.name}</h3>
            <div class="plan-price">${money(plan.price)}<span>/month</span></div>
            <p><strong>${plan.discount}% member discount</strong></p>
            <ul>${plan.features.map((feature) => `<li>${feature}</li>`).join("")}</ul>
            <button onclick='selectPlan(${JSON.stringify(plan)})'>Choose Plan</button>
        </article>
    `).join("");
}

function selectPlan(plan) {
    selectedPlan = plan;
    selectedPlanId = plan.id;
    wizardStep = 1;
    wizardSteps = [1];

    if (plan.requires_location) {
        wizardSteps.push(2);
    }

    if (plan.requires_family) {
        wizardSteps.push(3);
    }

    wizardSteps.push("final");

    document.getElementById("selectedPlanText").textContent = `Selected plan: ${plan.name} (${money(plan.price)} per month)`;

    ["membershipPassword", "cardName", "cardNumber", "demoBalance", "membershipCaptchaInput"].forEach((id) => {
        document.getElementById(id).value = "";
    });

    document.getElementById("paymentEmail").value = currentUser ? currentUser.email : "";
    document.getElementById("paymentMessage").textContent = "";
    document.getElementById("wizardFamilyCount").value = 0;

    buildWizardFamilyFields();
    showWizardStep();
    openModal("membershipWizardModal");
}

function renderWizardProgress(current) {
    const progress = document.getElementById("wizardProgress");

    progress.innerHTML = wizardSteps.map((step, index) => `
        <div class="wizard-step-dot ${step === current ? "active" : ""}">${step === "final" ? "✓" : index + 1}</div>
        ${index < wizardSteps.length - 1 ? "<div class='wizard-line'></div>" : ""}
    `).join("");
}

function showWizardStep() {
    const current = wizardSteps[wizardStep - 1];

    renderWizardProgress(current);

    document.getElementById("wizardStep1").classList.toggle("hidden", current !== 1);
    document.getElementById("wizardStep2").classList.toggle("hidden", current !== 2);
    document.getElementById("wizardStep3").classList.toggle("hidden", current !== 3);
    document.getElementById("wizardFinal").classList.toggle("hidden", current !== "final");

    document.getElementById("wizardBackBtn").classList.toggle("hidden", wizardStep === 1);
    document.getElementById("wizardNextBtn").classList.toggle("hidden", current === "final");
    document.getElementById("wizardSubmitBtn").classList.toggle("hidden", current !== "final");

    if (current === "final") {
        loadMembershipCaptcha();
    }
}

async function nextWizardStep() {
    const current = wizardSteps[wizardStep - 1];

    if (current === 1) {
        const ok = await validatePaymentStep();

        if (!ok) {
            return;
        }
    }

    if (wizardStep < wizardSteps.length) {
        wizardStep += 1;
        showWizardStep();
    }
}

function previousWizardStep() {
    if (wizardStep > 1) {
        wizardStep -= 1;
        showWizardStep();
    }
}

async function validatePaymentStep() {
    try {
        const data = await fetchJson("/validate-payment-step", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                plan_id: selectedPlanId,
                email: document.getElementById("paymentEmail").value,
                password: document.getElementById("membershipPassword").value,
                card_name: document.getElementById("cardName").value,
                card_number: document.getElementById("cardNumber").value,
                payment_method: document.getElementById("paymentMethod").value,
                demo_balance: document.getElementById("demoBalance").value
            })
        });

        document.getElementById("paymentMessage").textContent = data.message;
        return true;
    } catch (error) {
        document.getElementById("paymentMessage").textContent = error.message;
        showPopup(error.message, "error");
        return false;
    }
}

function getSelectedLocationAccess() {
    const selected = document.querySelector("input[name='locationAccess']:checked");
    return selected ? selected.value : "off";
}

function familyFieldHtml(prefix, index) {
    return `
        <div class="family-member-form">
            <h4>Person ${index + 1}</h4>
            <input placeholder="Name" class="${prefix}-name">
            <input type="number" placeholder="Age" class="${prefix}-age">
            <select class="${prefix}-routine">
                <option>School</option>
                <option>Work</option>
                <option>Business</option>
                <option>Retired</option>
                <option>Not regular</option>
            </select>
            <select class="${prefix}-lifestyle">
                <option>Gym and fitness</option>
                <option>Yoga</option>
                <option>Meditation</option>
                <option>Play time</option>
                <option>Lazy</option>
                <option>Not so active</option>
            </select>
        </div>
    `;
}

function buildWizardFamilyFields() {
    const count = Number(document.getElementById("wizardFamilyCount").value || 0);
    const container = document.getElementById("wizardFamilyFields");

    container.innerHTML = "";

    for (let index = 0; index < count; index += 1) {
        container.innerHTML += familyFieldHtml("wizard-family", index);
    }
}

function buildFamilyFields() {
    const count = Number(document.getElementById("familyCount").value || 0);
    const container = document.getElementById("familyFields");

    container.innerHTML = "";

    for (let index = 0; index < count; index += 1) {
        container.innerHTML += familyFieldHtml("family", index);
    }
}

function collectFamilyProfile(prefix) {
    const names = document.querySelectorAll(`.${prefix}-name`);
    const ages = document.querySelectorAll(`.${prefix}-age`);
    const routines = document.querySelectorAll(`.${prefix}-routine`);
    const lifestyles = document.querySelectorAll(`.${prefix}-lifestyle`);
    const profile = [];

    names.forEach((nameField, index) => {
        profile.push({
            name: nameField.value,
            age: ages[index].value,
            routine: routines[index].value,
            lifestyle: lifestyles[index].value
        });
    });

    return profile;
}

async function submitMembershipActivation() {
    try {
        const data = await fetchJson("/activate-membership", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                email: document.getElementById("paymentEmail").value,
                password: document.getElementById("membershipPassword").value,
                plan_id: selectedPlanId,
                card_name: document.getElementById("cardName").value,
                card_number: document.getElementById("cardNumber").value,
                payment_method: document.getElementById("paymentMethod").value,
                demo_balance: document.getElementById("demoBalance").value,
                captcha: document.getElementById("membershipCaptchaInput").value,
                location_access: selectedPlan && selectedPlan.requires_location ? getSelectedLocationAccess() : "off",
                family_profile: selectedPlan && selectedPlan.requires_family ? collectFamilyProfile("wizard-family") : []
            })
        });

        currentUser = data.user;
        document.getElementById("paymentMessage").textContent = data.message;
        updateUserInterface();

        await runSmartCart();
        await loadOffers();

        showPopup(data.message);

        setTimeout(() => {
            closeModal("membershipWizardModal");
        }, 1200);
    } catch (error) {
        document.getElementById("paymentMessage").textContent = error.message;
        showPopup(error.message, "error");
        await loadMembershipCaptcha();
    }
}

async function signupUser() {
    try {
        const data = await fetchJson("/signup", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                name: document.getElementById("signupName").value,
                email: document.getElementById("signupEmail").value,
                password: document.getElementById("signupPassword").value,
                confirm_password: document.getElementById("signupConfirmPassword").value,
                captcha: document.getElementById("signupCaptchaInput").value
            })
        });

        currentUser = data.user;
        document.getElementById("signupMessage").textContent = data.message;
        updateUserInterface();
        showPopup(data.message);

        setTimeout(() => {
            closeModal("signupModal");
        }, 1200);
    } catch (error) {
        document.getElementById("signupMessage").textContent = error.message;
        showPopup(error.message, "error");
        await loadSignupCaptcha();
    }
}

async function loginUser() {
    try {
        const data = await fetchJson("/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                email: document.getElementById("loginEmail").value,
                password: document.getElementById("loginPassword").value
            })
        });

        currentUser = data.user;
        document.getElementById("loginMessage").textContent = data.message;
        updateUserInterface();

        await runSmartCart();
        await loadOffers();

        showPopup(data.message);

        setTimeout(() => {
            closeModal("loginModal");
        }, 1200);
    } catch (error) {
        document.getElementById("loginMessage").textContent = error.message;
        showPopup(error.message, "error");
    }
}

function showForgotPassword() {
    document.getElementById("forgotPasswordBox").classList.remove("hidden");
    document.getElementById("recoveryEmail").value = document.getElementById("loginEmail").value || "";
}

async function sendRecoveryLink() {
    try {
        const data = await fetchJson("/forgot-password", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                email: document.getElementById("recoveryEmail").value
            })
        });

        document.getElementById("loginMessage").textContent = data.message;
        showPopup(data.message);
    } catch (error) {
        document.getElementById("loginMessage").textContent = error.message;
        showPopup(error.message, "error");
    }
}

async function logoutUser() {
    const data = await fetchJson("/logout", {
        method: "POST",
        headers: { "Content-Type": "application/json" }
    });

    // Clear logged-in user
    currentUser = null;

    // Clear cart and all user/cart-related values
    cart = [];
    currentRecommendedProduct = null;
    activeUsageBonus = 0;
    appliedCouponDiscount = 0;

    // Clear coupon and messages
    document.getElementById("couponInput").value = "";
    document.getElementById("couponMessage").textContent = "";
    document.getElementById("locationMessage").textContent = "";
    document.getElementById("familyMessage").textContent = "";

    // Hide user-only benefit sections
    document.getElementById("locationBenefitsCard").classList.add("hidden");
    document.getElementById("premiumFamilyCard").classList.add("hidden");
    document.getElementById("nearbyStoresBox").classList.add("hidden");
    document.getElementById("usageBonusBox").classList.add("hidden");
    document.getElementById("premiumGuidanceBox").classList.add("hidden");

    // Refresh UI as logged-out user
    updateUserInterface();
    renderCart();

    await runSmartCart();
    await loadOffers();

    showPopup(data.message);
}

function requestLocationUpdate() {
    const selected = document.getElementById("locationPreference").value;

    if (selected === "off") {
        openModal("locationWarningModal");
        return;
    }

    saveLocationPreference(selected);
}

function keepLocationOn() {
    document.getElementById("locationPreference").value = "while_using";
    closeModal("locationWarningModal");
    saveLocationPreference("while_using");
}

function confirmLocationOff() {
    closeModal("locationWarningModal");
    saveLocationPreference("off");
}

async function saveLocationPreference(locationAccess) {
    try {
        const data = await fetchJson("/update-location", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ location_access: locationAccess })
        });

        currentUser = data.user;
        document.getElementById("locationMessage").textContent = data.message;
        updateUserInterface();

        await runSmartCart();

        showPopup(data.message);
    } catch (error) {
        document.getElementById("locationMessage").textContent = error.message;
        showPopup(error.message, "error");
    }
}

async function saveFamilyProfile() {
    try {
        const data = await fetchJson("/save-family-profile", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                family_profile: collectFamilyProfile("family")
            })
        });

        currentUser = data.user;
        document.getElementById("familyMessage").textContent = data.message;
        document.getElementById("familyCount").value = 0;
        document.getElementById("familyFields").innerHTML = "";

        updateUserInterface();

        await runSmartCart();

        showPopup(data.message);
    } catch (error) {
        document.getElementById("familyMessage").textContent = error.message;
        showPopup(error.message, "error");
    }
}

async function removeFamilyMember(index) {
    try {
        const data = await fetchJson("/remove-family-member", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ index })
        });

        currentUser = data.user;
        updateUserInterface();

        await runSmartCart();

        showPopup(data.message);
    } catch (error) {
        showPopup(error.message, "error");
    }
}

function resetDemo() {
    document.getElementById("itemSelect").value = "milk";
    document.getElementById("budgetInput").value = 30;
    document.getElementById("prioritySelect").value = "price";
    cart = [];
    appliedCouponDiscount = 0;
    activeUsageBonus = 0;
    document.getElementById("couponInput").value = "";
    document.getElementById("couponMessage").textContent = "";
    runSmartCart();
    renderCart();
}

function renderSavingsReport() {
    const reportSection = document.getElementById("savingsReport");
    const reportTitle = document.getElementById("reportTitle");
    const reportSubtitle = document.getElementById("reportSubtitle");
    const reportContent = document.getElementById("reportContent");

    if (!reportSection || !reportTitle || !reportSubtitle || !reportContent) {
        return;
    }

    if (!currentUser || !currentUser.membership) {
        reportSection.classList.add("hidden");
        return;
    }

    const rawTotal = calculateCartTotal();
    const cartItemsCount = cart.reduce((sum, item) => sum + item.quantity, 0);
    const recommendedTotal = calculateRecommendedTotal();
    const cartSaving = Math.max(rawTotal - recommendedTotal, 0);

    const planId = currentUser.membership.plan_id;

    reportSection.classList.remove("hidden");

    if (planId === "basic") {
        const monthlyMultiplier = 4;
        const memberDiscount = rawTotal * 0.05;
        const monthlySaving = (cartSaving + memberDiscount + appliedCouponDiscount) * monthlyMultiplier;

        reportTitle.textContent = "Basic Saver Monthly Savings Report";
        reportSubtitle.textContent =
            "A simple monthly report showing estimated savings, best-value choices, and price alert readiness.";

        reportContent.innerHTML = `
            <div class="report-card highlight">
                <span>Estimated monthly saving</span>
                <strong>${money(monthlySaving)}</strong>
                <p>Calculated from your current cart savings and Basic Saver 5% member discount.</p>
            </div>

            <div class="report-card">
                <span>Monthly cart estimate</span>
                <strong>${money(rawTotal * monthlyMultiplier)}</strong>
                <p>Estimated monthly grocery value based on your current cart.</p>
            </div>

            <div class="report-card">
                <span>Basic member discount</span>
                <strong>5%</strong>
                <p>Applied to eligible cart items for Basic Saver users.</p>
            </div>

            <div class="report-card">
                <span>Price alerts</span>
                <strong>${cartItemsCount}</strong>
                <p>Items in your cart can be monitored for future price drops.</p>
            </div>
        `;
    }

    else if (planId === "plus") {
        const weeklyMemberDiscount = rawTotal * 0.10;
        const usageBonusDiscount = rawTotal * (activeUsageBonus || 0) / 100;
        const smartSubstituteSaving = cartSaving;
        const weeklySaving =
            weeklyMemberDiscount + usageBonusDiscount + smartSubstituteSaving + appliedCouponDiscount;

        reportTitle.textContent = "Smart Plus Weekly Savings Report";
        reportSubtitle.textContent =
            "A weekly report showing Smart Plus discounts, usage rewards, substitute savings, and coupon impact.";

        reportContent.innerHTML = `
            <div class="report-card highlight">
                <span>Estimated weekly saving</span>
                <strong>${money(weeklySaving)}</strong>
                <p>Includes Smart Plus discount, usage bonus, coupons, and smart substitute savings.</p>
            </div>

            <div class="report-card">
                <span>Smart Plus discount</span>
                <strong>10%</strong>
                <p>Applied automatically to your cart as a Smart Plus member.</p>
            </div>

            <div class="report-card">
                <span>Usage bonus</span>
                <strong>${activeUsageBonus || 0}%</strong>
                <p>Extra app discount based on how frequently the user uses SmartCart.</p>
            </div>

            <div class="report-card">
                <span>Smart substitute saving</span>
                <strong>${money(smartSubstituteSaving)}</strong>
                <p>Potential saving from choosing the lowest recommended options.</p>
            </div>
        `;
    }

    else {
        reportSection.classList.add("hidden");
    }
}

document.addEventListener("DOMContentLoaded", async () => {
    document.getElementById("analyseButton").addEventListener("click", runSmartCart);
    document.getElementById("addRecommendedButton").addEventListener("click", addRecommendedToCart);
    document.getElementById("resetButton").addEventListener("click", resetDemo);
    document.getElementById("itemSelect").addEventListener("change", runSmartCart);
    document.getElementById("prioritySelect").addEventListener("change", runSmartCart);

    document.getElementById("familyCount").value = 0;
    document.getElementById("wizardFamilyCount").value = 0;

    await loadSessionUser();
    await runSmartCart();
    renderCart();
    await loadOffers();
    await loadPlans();
});
