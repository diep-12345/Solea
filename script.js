
        const productsList = [
            { id: 1, name: "Áo Sơ Mi White Linen", price: 350000, type: "Áo", season: "Hè", img: "https://png.pngtree.com/png-clipart/20230508/original/pngtree-white-t-shirt-mockup-front-view-png-image_9151240.png", rating: 4.8, theme: "CleanGirl" },
            { id: 2, name: "Quần Âu Tapered Kem", price: 420000, type: "Quần", season: "Hè", img: "https://png.pngtree.com/png-clipart/20230504/original/pngtree-pants-clothing-transparency-png-image_9138676.png", rating: 4.6, theme: "CleanGirl" },
            { id: 3, name: "Áo Blazer Đen Slimfit", price: 650000, type: "Áo khoác", season: "Đông", img: "https://png.pngtree.com/png-clipart/20230419/original/pngtree-black-suit-tie-shirt-png-image_9068015.png", rating: 4.9, theme: "Y2K" },
            { id: 4, name: "Chân Váy Xòe Vintage", price: 380000, type: "Chân váy", season: "Hè", img: "https://png.pngtree.com/png-clipart/20230504/original/pngtree-blue-skirt-transparency-png-image_9138668.png", rating: 4.7, theme: "Coquette" }
        ];

        let selectedStudio = { top: null, bottom: null };
        let cartCount = 0;
        let currentStudioTab = 'top';

        function showPage(pageId) {
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.getElementById(`page-${pageId}`).classList.add('active');
            window.scrollTo(0, 0);
        }

        let cartItems = [];

        // Hiển thị sản phẩm cửa hàng
        function renderStoreProducts(list = null) {
            const grid = document.getElementById('store-products-grid');
            if (!grid) return;
            grid.innerHTML = '';
            const itemsToRender = list || productsList;
            if (!itemsToRender.length) {
                grid.innerHTML = '<p class="col-span-full text-center text-sm text-gray-500 py-10">Không tìm thấy sản phẩm phù hợp.</p>';
                return;
            }
            itemsToRender.forEach(item => {
                grid.innerHTML += `
                    <div class="bg-white border border-pastel-200 rounded-2xl p-3.5 hover:shadow-lg hover:shadow-pastel-100 transition flex flex-col justify-between">
                        <div>
                            <img src="${item.img}" alt="${item.name}" class="h-36 w-full object-contain mb-2">
                            <span class="text-[9px] bg-pastel-50 text-pastel-500 px-2 py-0.5 rounded uppercase font-bold">${item.theme}</span>
                            <h3 class="font-bold text-gray-800 text-xs mt-2">${item.name}</h3>
                            <p class="text-[11px] text-amber-500 mt-1">★ ${item.rating.toFixed(1)} <span class="text-gray-400">/ 5</span></p>
                            <p class="text-xs font-black text-pastel-400 mt-1">${item.price.toLocaleString('vi-VN')} đ</p>
                        </div>
                        <button onclick="addToCart(${item.id})" class="mt-3 w-full bg-pastel-300 text-white py-2 rounded-xl text-xs font-bold hover:bg-pastel-400 transition shadow-sm"><i class="fa-solid fa-bag-shopping mr-1"></i> Thêm vào giỏ</button>
                    </div>`;
            });
        }

        function applyStoreFilters() {
            const query = document.getElementById('store-search-input').value.toLowerCase();
            const price = document.getElementById('price-filter').value;
            const rating = document.getElementById('rating-filter').value;
            const sort = document.getElementById('sort-filter').value;
            let filtered = productsList.filter(p => p.name.toLowerCase().includes(query) || p.theme.toLowerCase().includes(query) || p.type.toLowerCase().includes(query));
            if (price === 'under400') filtered = filtered.filter(p => p.price < 400000);
            if (price === '400to600') filtered = filtered.filter(p => p.price >= 400000 && p.price <= 600000);
            if (price === 'over600') filtered = filtered.filter(p => p.price > 600000);
            if (rating !== 'all') filtered = filtered.filter(p => p.rating >= Number(rating));
            if (sort === 'priceAsc') filtered.sort((a, b) => a.price - b.price);
            if (sort === 'priceDesc') filtered.sort((a, b) => b.price - a.price);
            if (sort === 'rating') filtered.sort((a, b) => b.rating - a.rating);
            if (sort === 'newest') filtered.sort((a, b) => b.id - a.id);
            renderStoreProducts(filtered);
        }

        function searchProducts() {
            applyStoreFilters();
        }

        function selectTheme(themeName) {
            showPage('store');
            document.getElementById('store-search-input').value = themeName;
            applyStoreFilters();
        }

        function addToCart(productId) {
            const product = productsList.find(p => p.id === productId);
            if (!product) return;
            const existing = cartItems.find(item => item.id === productId);
            if (existing) existing.quantity += 1;
            else cartItems.push({ ...product, quantity: 1 });
            updateCart();
        }

        function updateCart() {
            cartCount = cartItems.reduce((sum, item) => sum + item.quantity, 0);
            document.getElementById('cart-badge').innerText = cartCount;
            const cartList = document.getElementById('cart-items');
            const cartTotal = document.getElementById('cart-total');
            if (!cartList || !cartTotal) return;
            if (!cartItems.length) {
                cartList.innerHTML = '<p class="text-sm text-gray-400 text-center py-8">Giỏ hàng của bạn đang trống.</p>';
                cartTotal.innerText = '0 đ';
                return;
            }
            cartList.innerHTML = cartItems.map(item => `
                <div class="flex items-center gap-3 border-b border-pastel-100 py-3">
                    <img src="${item.img}" class="w-14 h-14 object-contain bg-pastel-50 rounded-xl" alt="${item.name}">
                    <div class="flex-1"><p class="text-xs font-bold">${item.name}</p><p class="text-xs text-pastel-400 mt-1">${item.price.toLocaleString('vi-VN')} đ × ${item.quantity}</p>
                    <div class="flex gap-2 mt-2"><button onclick="changeCartQuantity(${item.id}, -1)" class="px-2 rounded bg-pastel-50">−</button><button onclick="changeCartQuantity(${item.id}, 1)" class="px-2 rounded bg-pastel-50">+</button><button onclick="removeFromCart(${item.id})" class="text-rose-500 text-[11px] ml-2">Xóa</button></div></div>
                </div>`).join('');
            const total = cartItems.reduce((sum, item) => sum + item.price * item.quantity, 0);
            cartTotal.innerText = total.toLocaleString('vi-VN') + ' đ';
        }

        function changeCartQuantity(id, change) {
            const item = cartItems.find(p => p.id === id);
            if (!item) return;
            item.quantity += change;
            if (item.quantity <= 0) cartItems = cartItems.filter(p => p.id !== id);
            updateCart();
        }

        function removeFromCart(id) {
            cartItems = cartItems.filter(p => p.id !== id);
            updateCart();
        }

        function toggleCartModal() {
            document.getElementById('cart-modal').classList.toggle('hidden');
            updateCart();
        }

        // VOUCHER MODAL
        function toggleVoucherModal() {
            document.getElementById('voucher-modal').classList.toggle('hidden');
        }

        function copyCode(code) {
            alert('Đã lưu thành công mã voucher: ' + code);
            toggleVoucherModal();
        }

        // TƯƠNG TÁC BLOG (LIKE, COMMENT, BOOKMARK)
        function toggleLike(btn) {
            const icon = btn.querySelector('i');
            const count = btn.querySelector('.like-count');
            let num = parseInt(count.innerText);

            if(icon.classList.contains('fa-regular')) {
                icon.className = 'fa-solid fa-heart text-base text-rose-500';
                count.innerText = num + 1;
            } else {
                icon.className = 'fa-regular fa-heart text-base';
                count.innerText = num - 1;
            }
        }

        function toggleBookmark(btn) {
            const icon = btn.querySelector('i');
            if(icon.classList.contains('fa-regular')) {
                icon.className = 'fa-solid fa-bookmark text-base text-pastel-400';
                alert('Đã lưu bài viết vào danh sách yêu thích!');
            } else {
                icon.className = 'fa-regular fa-bookmark text-base';
            }
        }

        function toggleComments(id) {
            document.getElementById(id).classList.toggle('hidden');
        }

        function addComment(postId) {
            const input = document.getElementById(`comment-input-${postId}`);
            const list = document.getElementById(`comment-list-${postId}`);
            if(!input.value.trim()) return;

            list.innerHTML += `
                <div class="bg-pastel-50 p-2.5 rounded-2xl border border-pastel-100">
                    <span class="font-bold text-gray-900">@ban_truyencam:</span> ${input.value}
                </div>
            `;
            input.value = '';
        }
        function toggleChat() {
            document.getElementById('chat-popup').classList.toggle('hidden');
        }

        function sendChat() {
            const input = document.getElementById('chat-input');
            const box = document.getElementById('chat-box');
            if(!input.value.trim()) return;
            box.innerHTML += `<div class="bg-pastel-300 text-white p-2 rounded-xl text-right">${input.value}</div>`;
            const q = input.value;
            input.value = '';
            setTimeout(() => {
                box.innerHTML += `<div class="bg-pastel-50 p-2 rounded-xl">Với yêu cầu "${q}", tôi gợi ý bạn qua trang <b>Blog Tip Phối Đồ</b> xem bài viết mới nhất!</div>`;
                box.scrollTop = box.scrollHeight;
            }, 500);
        }

        function toggleLoginModal() {
            document.getElementById('login-modal').classList.toggle('hidden');
        }

        function filterCategory(category) {
            showPage('store');
            const input = document.getElementById('store-search-input');
            input.value = category;
            applyStoreFilters();
        }
        function filterSeason(season) {
            showPage('store');
            document.getElementById('store-search-input').value = '';
            const filtered = productsList.filter(p => p.season === season);
            renderStoreProducts(filtered);
        }
        function renderLatestProducts() {
            const track = document.getElementById('latest-products-track');
            if (!track) return;
            const newest = [...productsList].reverse();
            const cards = newest.map(p => `<article class="latest-product"><img src="${p.img}" alt="${p.name}"><div class="info"><h3>${p.name}</h3><p>${p.price.toLocaleString('vi-VN')} đ</p><button onclick="addToCart(${p.id})" class="mt-3 text-xs font-bold text-[#a96374]">Thêm vào giỏ +</button></div></article>`).join('');
            track.innerHTML = cards + cards;
        }

        renderStoreProducts();
        renderLatestProducts();
    