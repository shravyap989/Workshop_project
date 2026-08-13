const API_URL = "http://localhost:5000/api";

let menu = [];
let cart = {};

async function loadMenu() {
  const response = await fetch(`${API_URL}/menu`);
  menu = await response.json();

  document.getElementById("menu").innerHTML = menu.map(item => `
    <article class="card">
      <h3>${item.name}</h3>
      <p>${item.description || ""}</p>
      <strong>₹${Number(item.price).toFixed(2)}</strong>
      <button onclick="addToCart(${item.id})">Add to Cart</button>
    </article>
  `).join("");
}

function addToCart(id) {
  cart[id] = (cart[id] || 0) + 1;
  renderCart();
}

function changeQty(id, amount) {
  cart[id] = (cart[id] || 0) + amount;
  if (cart[id] <= 0) delete cart[id];
  renderCart();
}

function renderCart() {
  let total = 0;

  const html = Object.entries(cart).map(([id, quantity]) => {
    const item = menu.find(x => x.id == id);
    const lineTotal = Number(item.price) * quantity;
    total += lineTotal;

    return `
      <div class="cart-row">
        <span>${item.name} × ${quantity}</span>
        <span>₹${lineTotal.toFixed(2)}</span>
        <button onclick="changeQty(${id}, -1)">−</button>
        <button onclick="changeQty(${id}, 1)">+</button>
      </div>
    `;
  }).join("");

  document.getElementById("cart").innerHTML =
    html || "<p>Your cart is empty.</p>";
  document.getElementById("total").textContent = total.toFixed(2);
}

async function placeOrder() {
  const items = Object.entries(cart).map(([id, quantity]) => ({
    menu_item_id: Number(id),
    quantity
  }));

  if (!items.length) {
    document.getElementById("message").textContent =
      "Please add at least one item.";
    return;
  }

  const response = await fetch(`${API_URL}/orders`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({items})
  });

  const data = await response.json();

  document.getElementById("message").textContent =
    response.ok
      ? `Order #${data.order_id} placed successfully!`
      : data.error;

  if (response.ok) {
    cart = {};
    renderCart();
    loadOrders();
  }
}

async function updateStatus(id, status) {
  await fetch(`${API_URL}/orders/${id}/status`, {
    method: "PATCH",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({status})
  });

  loadOrders();
}

async function loadOrders() {
  const response = await fetch(`${API_URL}/orders`);
  const orders = await response.json();

  document.getElementById("orders").innerHTML =
    orders.length
      ? orders.map(order => `
        <article class="order">
          <strong>Order #${order.id}</strong>
          <span class="badge">${order.status}</span>
          <p>${order.items.map(
            item => `${item.name} × ${item.quantity}`
          ).join(", ")}</p>
          <strong>Total: ₹${Number(order.total).toFixed(2)}</strong>

          <label>
            Update status:
            <select onchange="updateStatus(${order.id}, this.value)">
              ${["PLACED","PREPARING","READY","COMPLETED","CANCELLED"]
                .map(status =>
                  `<option ${status === order.status ? "selected" : ""}>
                    ${status}
                  </option>`
                ).join("")}
            </select>
          </label>
        </article>
      `).join("")
      : "<p>No orders yet.</p>";
}

loadMenu();
renderCart();
loadOrders();
