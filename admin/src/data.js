export const initialProducts = [
  { id: 'SF001', name: 'Áo thun basic', category: 'Áo', price: 350000, stock: 50, color: 'Trắng', size: ['S','M','L','XL'], status: 'Còn hàng', image: 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=700&q=85', tone: 'ivory', type: 'Top' },
  { id: 'SF002', name: 'Áo khoác denim', category: 'Áo khoác', price: 790000, stock: 30, color: 'Xanh', size: ['S','M','L'], status: 'Còn hàng', image: 'https://images.unsplash.com/photo-1543076447-215ad9ba6923?auto=format&fit=crop&w=700&q=85', tone: 'blue', type: 'Outerwear' },
  { id: 'SF003', name: 'Quần jeans ống rộng', category: 'Quần dài', price: 620000, stock: 40, color: 'Xanh', size: ['S','M','L','XL'], status: 'Còn hàng', image: 'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?auto=format&fit=crop&w=700&q=85', tone: 'blue', type: 'Bottom' },
  { id: 'SF004', name: 'Váy midi hoa', category: 'Váy', price: 680000, stock: 20, color: 'Be', size: ['S','M','L'], status: 'Còn hàng', image: 'https://images.unsplash.com/photo-1595777457583-95e059d581b8?auto=format&fit=crop&w=700&q=85', tone: 'rose', type: 'Dress' },
  { id: 'SF005', name: 'Áo sơ mi oversize', category: 'Áo sơ mi', price: 550000, stock: 5, color: 'Trắng', size: ['M','L','XL'], status: 'Sắp hết', image: 'https://images.unsplash.com/photo-1598033129183-c4f50c736f10?auto=format&fit=crop&w=700&q=85', tone: 'ivory', type: 'Top' },
  { id: 'SF006', name: 'Blazer màu be', category: 'Áo khoác', price: 950000, stock: 16, color: 'Be', size: ['S','M','L'], status: 'Còn hàng', image: 'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?auto=format&fit=crop&w=700&q=85', tone: 'sand', type: 'Outerwear' },
  { id: 'SF007', name: 'Áo len cổ tròn', category: 'Áo', price: 420000, stock: 0, color: 'Đen', size: ['S','M','L'], status: 'Hết hàng', image: 'https://images.unsplash.com/photo-1618354691373-d851c5c3a990?auto=format&fit=crop&w=700&q=85', tone: 'dark', type: 'Top' },
  { id: 'SF008', name: 'Quần âu suông', category: 'Quần dài', price: 590000, stock: 24, color: 'Đen', size: ['S','M','L','XL'], status: 'Còn hàng', image: 'https://images.unsplash.com/photo-1506629905607-d9d3c3e7a9b0?auto=format&fit=crop&w=700&q=85', tone: 'dark', type: 'Bottom' }
];

export const orders = [
  { id: '#SF00124', customer: 'Nguyễn Thị Mai', date: '22/10/2026', total: 1250000, status: 'Đang xử lý' },
  { id: '#SF00123', customer: 'Trần Văn Nam', date: '22/10/2026', total: 980000, status: 'Đã giao' },
  { id: '#SF00122', customer: 'Lê Thị Hương', date: '21/10/2026', total: 1560000, status: 'Đang giao' },
  { id: '#SF00121', customer: 'Phạm Quốc Bảo', date: '21/10/2026', total: 760000, status: 'Đã giao' }
];

export const money = (n) => new Intl.NumberFormat('vi-VN', {
  style: 'currency', currency: 'VND', maximumFractionDigits: 0
}).format(n);