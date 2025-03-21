const categories = [...new Set(products.map(p => p.category))];

window.onload = function() {
  // Add category buttons
  const nav = document.getElementById('categoryButtons');
  categories.forEach(cat => {
    let btn = document.createElement('button');
    btn.className = "btn btn-outline-primary";
    btn.innerText = cat;
    btn.onclick = () => filterCategory(cat);
    nav.appendChild(btn);
  });

  // Load all products initially
  loadProducts('All');

  // Search functionality
  document.getElementById('searchBar').addEventListener('input', function() {
    const searchValue = this.value.toLowerCase();
    loadProducts('All', searchValue);
  });

  // Load Blogs
  fetch('blogs.json')
    .then(response => response.json())
    .then(blogs => {
      const blogList = document.getElementById('blogList');
      blogs.forEach(blog => {
        blogList.innerHTML += `<li><a href="${blog.link}" target="_blank">${blog.title}</a></li>`;
      });
    })
    .catch(err => console.log("Blog load failed", err));
};

function loadProducts(category, searchTerm = "") {
  const container = document.getElementById('productContainer');
  container.innerHTML = "";
  products
    .filter(p => (category === 'All' || p.category === category) && p.title.toLowerCase().includes(searchTerm))
    .forEach(prod => {
      container.innerHTML += `
      <div class="col-md-3">
        <div class="product-card">
          <img src="${prod.image}" alt="${prod.title}">
          <h5>${prod.title}</h5>
          <p><span class="price">${prod.price}</span> <span class="old-price">${prod.old_price}</span></p>
          <p>Category: ${prod.category}</p>
          <div class="mb-2">
            <span class="star">&#9733;&#9733;&#9733;&#9733;&#9734;</span>
          </div>
          <a href="${prod.link}" target="_blank" class="btn btn-sm btn-buy">Buy Now</a>
        </div>
      </div>`;
    });
}

function filterCategory(category) {
  loadProducts(category);
}
