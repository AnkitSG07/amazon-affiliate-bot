// js/main.js
window.onload = function() {
  // Create category buttons
  const categories = [...new Set(products.map(p => p.category))];
  const nav = document.getElementById('categoryButtons');
  // "All" button is in index.html or you can create it here
  categories.forEach(cat => {
    let btn = document.createElement('button');
    btn.className = "btn btn-outline-primary";
    btn.innerText = cat;
    btn.onclick = () => loadProducts(cat);
    nav.appendChild(btn);
  });

  // Load "All" products initially
  loadProducts("All");

  // Hook up search
  const searchBar = document.getElementById('searchBar');
  searchBar.addEventListener('input', function() {
    const searchTerm = this.value.toLowerCase();
    loadProducts("All", searchTerm);
  });

  // Load blogs from blogs.json
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
        <div class="product-card text-center">
          <img src="${prod.image}" alt="${prod.title}">
          <div class="product-title mt-2">${prod.title}</div>
          <div class="mt-2">
            <span class="product-price">${prod.price}</span>
            <span class="old-price">${prod.old_price}</span>
          </div>
          <p class="text-muted">${prod.category}</p>
          <a href="${prod.link}" target="_blank" class="btn btn-primary mt-2">Buy Now</a>
        </div>`;
      container.appendChild(col);
    });
}
