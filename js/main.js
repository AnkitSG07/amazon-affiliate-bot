window.onload = function () {
  // Create category cards dynamically
  const categories = [...new Set(products.map((p) => p.category))];
  const nav = document.getElementById("categoryCards");

  categories.forEach((cat) => {
    let card = document.createElement("div");
    card.className = "category-card text-center";
    card.innerHTML = `
      <img src="https://i.imgur.com/yW2W9SC.png" alt="${cat} Icon">
      <div class="category-name fw-bold">${cat}</div>
    `;
    card.onclick = () => loadProducts(cat);
    nav.appendChild(card);
  });

  // Load gallery sections dynamically
  loadSection("Bestseller", "productContainerBestsellers");
  loadSection("Price Drop", "productContainerPriceDrops");
  loadSection("Best Deal", "productContainerBestDeals");

  // Hook up search
  const searchBar = document.getElementById("searchBar");
  searchBar.addEventListener("input", function () {
    const searchTerm = this.value.toLowerCase();
    loadProducts("All", searchTerm);
  });

  // Load blogs dynamically from blogs.json
  fetch("blogs.json")
    .then((res) => res.json())
    .then((blogData) => {
      const blogList = document.getElementById("blogList");
      blogData.forEach((blog) => {
        let li = document.createElement("li");
        li.innerHTML = `<a href="${blog.link}" target="_blank">${blog.title}</a>`;
        blogList.appendChild(li);
      });
    })
    .catch((err) => console.error("Blogs load error:", err));
};

// ✅ Load products by category or search term
function loadProducts(category, searchTerm = "") {
  const containers = {
    Bestseller: document.getElementById("productContainerBestsellers"),
    "Price Drop": document.getElementById("productContainerPriceDrops"),
    "Best Deal": document.getElementById("productContainerBestDeals"),
  };

  // Clear all sections
  Object.values(containers).forEach((container) => (container.innerHTML = ""));

  // Filter and load products into respective sections
  products
    .filter(
      (p) =>
        (category === "All" || p.category === category) &&
        p.title.toLowerCase().includes(searchTerm)
    )
    .forEach((prod) => {
      if (containers[prod.type]) {
        addProductCard(prod, containers[prod.type]);
      }
    });
}

// ✅ Load section by type (Bestseller, Price Drop, Best Deal)
function loadSection(type, containerId) {
  const container = document.getElementById(containerId);

  // Check if the container exists
  if (!container) {
    console.error(`Error: Container with ID "${containerId}" not found.`);
    return;
  }

  container.innerHTML = "";
  products
    .filter((p) => p.type === type)
    .forEach((prod) => addProductCard(prod, container));
}

// ✅ Add product card to the correct section
function addProductCard(prod, container) {
  let col = document.createElement("div");
  col.className = "col-md-3 mb-4";
  col.innerHTML = `
    <div class="product-card text-center position-relative">
      <span class="category-badge">${prod.category}</span>
      <span class="discount-badge">${prod.type}</span>
      <img src="${prod.image}" alt="${prod.title}">
      <div class="product-title mt-2">${prod.title}</div>
      <div class="star-rating">⭐️⭐️⭐️⭐️⭐️</div>
      <div class="mt-2">
        <span class="product-price">${prod.price}</span>
        <span class="old-price">${prod.old_price}</span>
      </div>
      <a href="${prod.link}" target="_blank" class="btn btn-primary mt-2">Buy Now</a>
    </div>`;
  container.appendChild(col);
}
