
const categories = [...new Set(products.map(p => p.category))];

window.onload = function() {
  // Add category buttons dynamically
  const nav = document.getElementById('categoryButtons');
  categories.forEach(cat => {
    let btn = document.createElement('button');
    btn.className = "btn btn-outline-prconst container = document.getElementById('product-container');

products.forEach(product => {
  const col = document.createElement('div');
  col.className = "col-md-4";

  col.innerHTML = `
    <div class="product-card text-center">
      <img src="${product.image}" alt="${product.title}" />
      <div class="product-title">${product.title}</div>
      <div>
        <span class="product-price">${product.price}</span>
        <span class="old-price">${product.old_price}</span>
      </div>
      <a href="${product.link}" class="btn btn-primary mt-2" target="_blank">Buy Now</a>
    </div>
  `;

  container.appendChild(col);
});
imary";
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
      <div class="col-md-3 mb-4">
        <div class="card h-100 shadow-sm">
          <img src="${prod.image}" class="card-img-top" alt="${prod.title}">
          <div class="card-body">
            <h5 class="card-title">${prod.title}</h5>
            <p class="card-text">
              <strong>Price:</strong> ${prod.price} 
              <span style='text-decoration: line-through; color: grey;'>${prod.old_price}</span>
            </p>
            <p><strong>Category:</strong> ${prod.category}</p>
            <a href="${prod.link}" target="_blank" class="btn btn-warning w-100">Buy Now</a>
          </div>
        </div>
      </div>`;
    });
}

function filterCategory(category) {
  loadProducts(category);
}
