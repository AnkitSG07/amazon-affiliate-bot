window.onload = function() {
  // Create category cards dynamically
  const categories = [...new Set(products.map(p => p.category))];
  const nav = document.getElementById('categoryCards');

  categories.forEach(cat => {
    let card = document.createElement('div');
    card.className = "category-card text-center";
    card.innerHTML = `
      <img src="https://i.imgur.com/yW2W9SC.png" alt="${cat} Icon">
      <div class="category-name fw-bold">${cat}</div>
    `;
    card.onclick = () => loadCategoryProducts(cat);
    nav.appendChild(card);
  });

  // Load all category products initially
  loadCategoryProducts("All");

  // Hook up search
  const searchBar = document.getElementById('searchBar');
  searchBar.addEventListener('input', function() {
    const searchTerm = this.value.toLowerCase();
    loadCategoryProducts("All", searchTerm);
  });

  // Load blogs dynamically
  fetch('blogs.json')
    .then(res => res.json())
    .then(blogData => {
      const blogList = document.getElementById('blogList');
      blogData.forEach(blog => {
        let li = document.createElement('li');
        li.innerHTML = `<a href="${blog.link}" target="_blank">${blog.title}</a>`;
        blogList.appendChild(li);
      });
    })
    .catch(err => console.error("Blogs load error:", err));
};

// Load specific category products into respective containers
function loadCategoryProducts(category, searchTerm = "") {
  const categoriesToLoad = ["Bestsellers", "Price Drops", "Best Deals"];
  categoriesToLoad.forEach(cat => {
    const container = document.getElementById(`productContainer${cat.replace(/\s/g, '')}`);
    if (container) {
      container.innerHTML = "";
      products
        .filter(p => (category === "All" || p.category === cat) && p.title.toLowerCase().includes(searchTerm))
        .forEach(prod => {
          let col = document.createElement('div');
          col.className = "col-md-3 mb-4";
          col.innerHTML = `
            <div class="product-card text-center position-relative">
              <span class="category-badge">${prod.category}</span>
              <span class="discount-badge">${prod.discount}</span>
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
        });
    }
  });
}
