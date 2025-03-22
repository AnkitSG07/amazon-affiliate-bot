window.onload = function() {
  // Create category cards instead of buttons
  const categories = [...new Set(products.map(p => p.category))];
  const nav = document.getElementById('categoryButtons');

  categories.forEach(cat => {
    let card = document.createElement('div');
    card.className = "category-card text-center p-3 m-2 border rounded shadow-sm";
    card.style.cursor = "pointer";
    card.innerHTML = `
      <div class="icon mb-2" style="font-size:30px;">🍀</div> 
      <div class="category-name fw-bold">${cat}</div>
    `;
    card.onclick = () => loadProducts(cat);
    nav.appendChild(card);
  });

  // Load "All" products initially
  loadProducts("All");

  // Hook up search
  const searchBar = document.getElementById('searchBar');
  searchBar.addEventListener('input', function() {
    const searchTerm = this.value.toLowerCase();
    loadProducts("All", searchTerm);
  });

  // Load blogs
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

function loadProducts(category, searchTerm = "") {
  const container = document.getElementById('productContainer');
  container.innerHTML = "";
  products
    .filter(p => (category === "All" || p.category === category) && p.title.toLowerCase().includes(searchTerm))
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
