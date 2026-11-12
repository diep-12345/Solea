import React, { useState } from 'react';
import {
  Activity, ArrowDownRight, ArrowRight, ArrowUpRight, Bell, Check, ChevronDown,
  ChevronLeft, ChevronRight, CircleHelp, CreditCard, Filter, LayoutDashboard,
  LogOut, Menu, Package, Plus, Search, Settings, Shirt, ShoppingBag,
  Tags, Trash2, Truck, Users, X, ChartNoAxesCombined,
  Pencil
} from 'lucide-react';
import { initialProducts, orders, money } from './data.js';
import { Navigate, Route, Routes } from 'react-router-dom';

const navGroups = [
  {
    label: 'TỔNG QUAN',
    items: [
      { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
      { id: 'analytics', label: 'Báo cáo & phân tích', icon: ChartNoAxesCombined },
    ],
  },
  {
    label: 'QUẢN LÝ CỬA HÀNG',
    items: [
      { id: 'products', label: 'Sản phẩm', icon: Package },
      { id: 'categories', label: 'Danh mục & bộ sưu tập', icon: Tags },
      { id: 'inventory', label: 'Quản lý kho', icon: Package },
      { id: 'orders', label: 'Đơn hàng', icon: Truck },
      { id: 'vouchers', label: 'Voucher & khuyến mãi', icon: ShoppingBag },
    ],
  },
  {
    label: 'KHÁCH HÀNG & CỘNG ĐỒNG',
    items: [
      { id: 'customers', label: 'Khách hàng', icon: Users },
      { id: 'blog', label: 'Blog', icon: Activity },
      { id: 'reviews', label: 'Bình luận & đánh giá', icon: Activity },
    ],
  },
  {
    label: 'NỘI DUNG WEBSITE',
    items: [
      { id: 'banners', label: 'Banner & trang chủ', icon: LayoutDashboard },
      { id: 'policies', label: 'Footer & chính sách', icon: Settings },
      { id: 'newsletter', label: 'Newsletter', icon: Users },
    ],
  },
  {
    label: 'QUẢN TRỊ HỆ THỐNG',
    items: [
      { id: 'admins', label: 'Tài khoản & phân quyền', icon: Users },
      { id: 'activity-log', label: 'Nhật ký hoạt động', icon: Activity },
      { id: 'settings', label: 'Cài đặt hệ thống', icon: Settings },
    ],
  },
];



const pageTitles = {
  // 1. Tổng quan
  dashboard: [
    'Tổng quan',
    'Chào mừng trở lại! Đây là tình hình cửa hàng hôm nay.'
  ],
  analytics: [
    'Báo cáo & phân tích',
    'Theo dõi hiệu quả hoạt động và kinh doanh của cửa hàng.'
  ],

  // 2. Quản lý cửa hàng
  products: [
    'Quản lý sản phẩm',
    'Quản lý danh mục, giá bán và tình trạng sản phẩm.'
  ],
  categories: [
    'Danh mục & bộ sưu tập',
    'Nhóm sản phẩm theo loại trang phục và bộ sưu tập.'
  ],
  inventory: [
    'Quản lý kho',
    'Theo dõi số lượng tồn kho và tình trạng hàng hóa.'
  ],
  orders: [
    'Đơn hàng',
    'Theo dõi và cập nhật trạng thái đơn hàng.'
  ],
  vouchers: [
    'Voucher & khuyến mãi',
    'Quản lý mã giảm giá và các chương trình ưu đãi.'
  ],

  // 3. Khách hàng & cộng đồng
  customers: [
    'Khách hàng',
    'Quản lý thông tin và lịch sử mua hàng của khách hàng.'
  ],
  blog: [
    'Blog',
    'Quản lý bài viết và nội dung chia sẻ trên website.'
  ],
  reviews: [
    'Bình luận & đánh giá',
    'Theo dõi và kiểm duyệt phản hồi của khách hàng.'
  ],

  // 4. Nội dung website
  banners: [
    'Banner & trang chủ',
    'Quản lý banner và nội dung hiển thị trên trang chủ.'
  ],
  policies: [
    'Footer & chính sách',
    'Quản lý thông tin chân trang và các chính sách cửa hàng.'
  ],
  newsletter: [
    'Newsletter',
    'Quản lý danh sách đăng ký nhận tin.'
  ],

  // 5. Quản trị hệ thống
  admins: [
    'Tài khoản & phân quyền',
    'Quản lý tài khoản quản trị và quyền truy cập.'
  ],
  'activity-log': [
    'Nhật ký hoạt động',
    'Theo dõi lịch sử thao tác trong hệ thống.'
  ],
  settings: [
    'Cài đặt hệ thống',
    'Cấu hình và quản lý các thiết lập của StyleFit.'
  ]
};


function Sidebar({ active, setActive, mobileOpen, setMobileOpen }) {
  return <>
    {mobileOpen && <button className="mobile-scrim" onClick={() => setMobileOpen(false)} aria-label="Đóng menu" />}
    <aside className={`sidebar ${mobileOpen ? 'sidebar-open' : ''}`}>
      <div className="brand"><span className="brand-mark"><Shirt size={19}/></span><span>Soléa<span className="brand-dot">.</span><small>FASHION STUDIO</small></span></div>
      <div className="workspace"><div className="workspace-avatar">S</div><div><strong>Soléa Store</strong><small>Không gian quản trị</small></div><ChevronDown size={15}/></div>
      <nav className="nav">
        {navGroups.map(group => <div className="nav-group" key={group.label}>
          <p className="nav-label">{group.label}</p>
          {group.items.map(item => {
            const Icon = item.icon;
            return <button key={item.id} className={`nav-item ${active === item.id ? 'active' : ''}`}
              onClick={() => { setActive(item.id); setMobileOpen(false); }}>
              <Icon size={17} strokeWidth={1.8}/><span>{item.label}</span>
              {item.id === 'orders' && <span className="nav-count">4</span>}
            </button>;
          })}
        </div>)}
      </nav>
      <div className="sidebar-bottom">
        <div className="help-card"><span className="help-icon"><CircleHelp size={17}/></span><div><strong>Cần trợ giúp?</strong><small>Xem hướng dẫn sử dụng</small></div><ArrowRight size={14}/></div>
        <div className="profile"><div className="profile-avatar">NA</div><div className="profile-text"><strong>Diệu Hương</strong><small>Quản trị viên</small></div><button title="Đăng xuất"><LogOut size={16}/></button></div>
      </div>
    </aside>
  </>;
}

function Topbar({ setMobileOpen }) {
  return <header className="topbar">
    <button className="icon-button mobile-menu" onClick={() => setMobileOpen(true)} aria-label="Mở menu"><Menu size={19}/></button>
    <div className="crumb">Không gian làm việc <span>/</span> <strong>StyleFit</strong></div>
    <div className="top-actions"><div className="top-date">Thứ Năm, 22 tháng 10</div><button className="icon-button notification" aria-label="Thông báo"><Bell size={18}/><i/></button><div className="top-avatar">NA</div></div>
  </header>;
}

function StatCard({ label, value, change, icon: Icon, tone = 'olive', caption }) {
  return <article className="stat-card">
    <div className="stat-top"><span>{label}</span><span className={`stat-icon ${tone}`}><Icon size={18}/></span></div>
    <div className="stat-value">{value}</div>
    <div className="stat-bottom"><span className="trend"><ArrowUpRight size={14}/>{change}</span><span>{caption || 'so với tháng trước'}</span></div>
  </article>;
}

function RevenueChart() {
  const values = [26, 39, 34, 48, 44, 61, 58, 74, 70, 86, 80, 94];
  const points = values.map((v, i) => `${25 + i * 31},${146 - v * 1.18}`).join(' ');
  return <div className="chart-wrap">
    <div className="chart-legend"><span><i className="legend-dot"/><span>Doanh thu</span></span><span className="muted">12 tháng gần nhất</span></div>
    <svg className="line-chart" viewBox="0 0 390 175" role="img" aria-label="Biểu đồ doanh thu minh họa">
      {[35,70,105,140].map(y => <line key={y} x1="20" y1={y} x2="375" y2={y} className="grid-line"/> )}
      <path d={`M ${points.replaceAll(' ', ' L ')} L 366 150 L 25 150 Z`} className="chart-area"/>
      <polyline points={points} className="chart-line"/>
      {values.map((v,i) => <circle key={i} cx={25+i*31} cy={146-v*1.18} r="3" className="chart-point"/>)}
      {['T1','T2','T3','T4','T5','T6','T7','T8','T9','T10','T11','T12'].map((m,i)=><text key={m} x={25+i*31} y="168" textAnchor="middle" className="axis-label">{m}</text>)}
    </svg>
  </div>;
}

function CategoryBreakdown() {
  const rows = [['Áo', 32, '#566b43'], ['Áo khoác', 24, '#8e9a79'], ['Quần dài', 18, '#c7c9b7'], ['Váy', 15, '#ddcdb9'], ['Khác', 11, '#e8e4d9']];
  return <div className="category-breakdown">
    <div className="donut" aria-label="Tỷ trọng danh mục"><div><strong>320</strong><small>Sản phẩm</small></div></div>
    <div className="category-legend">{rows.map(([name, value, color])=><div className="category-row" key={name}><i style={{background:color}}/><span>{name}</span><strong>{value}%</strong></div>)}</div>
  </div>;
}

function OrdersTable({ compact = false }) {
  return <div className={`table-wrap ${compact ? 'compact-table' : ''}`}><table>
    <thead><tr><th>Mã đơn</th><th>Khách hàng</th><th>Ngày đặt</th><th>Tổng tiền</th><th>Trạng thái</th></tr></thead>
    <tbody>{orders.slice(0, compact ? 3 : 4).map(o=><tr key={o.id}><td className="order-id">{o.id}</td><td>{o.customer}</td><td>{o.date}</td><td className="money">{money(o.total)}</td><td><span className={`status status-${o.status.replaceAll(' ','-')}`}>{o.status}</span></td></tr>)}</tbody>
  </table></div>;
}

function Dashboard({ products, setActive }) {
  return <div className="page-content">
    <div className="page-heading"><div><div className="eyebrow">THỨ NĂM · 22.10.2026</div><h1>Tổng quan<span className="heading-period">.</span></h1><p>Chào mừng trở lại! Đây là tình hình hoạt động của cửa hàng hôm nay.</p></div><button className="button button-outline"><span className="live-dot"/> Dữ liệu minh họa</button></div>
    <div className="stats-grid">
      <StatCard label="Doanh thu" value="25.680.000đ" change="+12,8%" icon={CreditCard} tone="olive"/>
      <StatCard label="Đơn hàng" value="128" change="+8,2%" icon={ShoppingBag} tone="peach"/>
      <StatCard label="Sản phẩm" value={String(products.length).padStart(2,'0')} change="+5,4%" icon={Package} tone="sage" caption="trong danh mục mẫu"/>
      <StatCard label="Khách hàng" value="286" change="+11,2%" icon={Users} tone="lavender"/>
    </div>
    <div className="dashboard-grid">
      <section className="panel revenue-panel"><div className="panel-heading"><div><h2>Doanh thu cửa hàng</h2><p>Hiệu quả kinh doanh theo tháng</p></div><button className="select-button">12 tháng <ChevronDown size={14}/></button></div><RevenueChart/></section>
      <section className="panel category-panel"><div className="panel-heading"><div><h2>Danh mục nổi bật</h2><p>Cơ cấu sản phẩm hiện tại</p></div><button className="subtle-icon" title="Xem chi tiết" onClick={()=>setActive('categories')}><ArrowRight size={16}/></button></div><CategoryBreakdown/><button className="text-link" onClick={()=>setActive('categories')}>Quản lý danh mục <ArrowRight size={14}/></button></section>
      <section className="panel orders-panel"><div className="panel-heading"><div><h2>Đơn hàng gần đây</h2><p>Các đơn cần theo dõi</p></div><button className="text-link" onClick={()=>setActive('orders')}>Xem tất cả <ArrowRight size={14}/></button></div><OrdersTable compact/></section>
      <section className="panel stock-panel"><div className="panel-heading"><div><h2>Tình trạng tồn kho</h2><p>Kiểm tra sản phẩm sắp hết</p></div><span className="stock-count">{products.filter(p=>p.stock > 0 && p.stock <= 10).length} cảnh báo</span></div>
        {products.filter(p=>p.stock <= 10).slice(0,3).map(p=><div className="stock-row" key={p.id}><img src={p.image} alt={p.name}/><div className="stock-name"><strong>{p.name}</strong><small>{p.id}</small></div><div className="stock-qty"><strong>{p.stock}</strong><small>sản phẩm</small></div></div>)}
        <button className="text-link" onClick={()=>setActive('products')}>Xem kho hàng <ArrowRight size={14}/></button>
      </section>
    </div>
  </div>;
}

function ProductsPage({ products, setProducts }) {
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('Tất cả');
  const [stock, setStock] = useState('Tất cả');
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ name:'', category:'Áo', price:'', stock:'', color:'Trắng' });
  const filtered = products.filter(p => (p.name.toLowerCase().includes(query.toLowerCase()) || p.id.toLowerCase().includes(query.toLowerCase())) && (category==='Tất cả'||p.category===category) && (stock==='Tất cả'||p.status===stock));
  const openAdd = () => { setEditing(null); setForm({name:'',category:'Áo',price:'',stock:'',color:'Trắng'}); setModalOpen(true); };
  const openEdit = p => { setEditing(p.id); setForm({name:p.name,category:p.category,price:String(p.price),stock:String(p.stock),color:p.color}); setModalOpen(true); };
  const save = e => {
    e.preventDefault();
    const count = Number(form.stock) || 0;
    const item = { id: editing || `SF${String(Date.now()).slice(-5)}`, name:form.name, category:form.category, price:Number(form.price)||0, stock:count, color:form.color, size:['S','M','L'], status:count===0?'Hết hàng':count<=10?'Sắp hết':'Còn hàng', image: editing ? products.find(p=>p.id===editing)?.image : 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=700&q=85', tone:'ivory', type:'Top' };
    setProducts(old => editing ? old.map(p=>p.id===editing?item:p) : [item,...old]);
    setModalOpen(false);
  };
  const remove = id => { if (window.confirm('Bạn có chắc muốn xóa sản phẩm này?')) setProducts(old=>old.filter(p=>p.id!==id)); };
  return <div className="page-content">
    <div className="page-heading"><div><div className="eyebrow">CỬA HÀNG / KHO HÀNG</div><h1>Quản lý sản phẩm<span className="heading-period">.</span></h1><p>Quản lý danh mục, giá bán và tình trạng tồn kho.</p></div><button className="button button-dark" onClick={openAdd}><Plus size={17}/> Thêm sản phẩm</button></div>
    <div className="product-summary"><div><span className="summary-label">Tổng sản phẩm</span><strong>{products.length}</strong></div><div><span className="summary-label">Đang còn hàng</span><strong>{products.filter(p=>p.stock>10).length}</strong></div><div><span className="summary-label">Sắp hết hàng</span><strong className="warning-number">{products.filter(p=>p.stock>0&&p.stock<=10).length}</strong></div><div><span className="summary-label">Hết hàng</span><strong>{products.filter(p=>p.stock===0).length}</strong></div></div>
    <section className="panel product-panel">
      <div className="product-toolbar"><div className="search-field"><Search size={16}/><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Tìm theo tên hoặc mã sản phẩm..."/></div><div className="toolbar-filters"><label><Filter size={15}/><select value={category} onChange={e=>setCategory(e.target.value)}><option>Tất cả</option>{[...new Set(products.map(p=>p.category))].map(c=><option key={c}>{c}</option>)}</select></label><label><select value={stock} onChange={e=>setStock(e.target.value)}><option>Tất cả</option><option>Còn hàng</option><option>Sắp hết</option><option>Hết hàng</option></select></label></div></div>
      <div className="table-wrap product-table-wrap"><table className="products-table"><thead><tr><th>Sản phẩm</th><th>Danh mục</th><th>Giá bán</th><th>Tồn kho</th><th>Trạng thái</th><th>Thao tác</th></tr></thead><tbody>
        {filtered.map(p=><tr key={p.id}><td><div className="product-cell"><img src={p.image} alt={p.name}/><div><strong>{p.name}</strong><small>{p.id}</small></div></div></td><td>{p.category}</td><td className="money">{money(p.price)}</td><td><span className={p.stock<=10?'stock-low':''}>{p.stock}</span></td><td><span className={`status ${p.status==='Còn hàng'?'status-Đã-giao':p.status==='Sắp hết'?'status-Đang-xử-lý':'status-Hết-hàng'}`}>{p.status}</span></td><td><div className="row-actions"><button className="icon-button" title="Sửa" onClick={()=>openEdit(p)}><Pencil size={15}/></button><button className="icon-button danger-icon" title="Xóa" onClick={()=>remove(p.id)}><Trash2 size={15}/></button></div></td></tr>)}
        {filtered.length===0&&<tr><td colSpan="6" className="empty-state">Không tìm thấy sản phẩm phù hợp.</td></tr>}
      </tbody></table></div>
      <div className="table-footer"><span>Hiển thị {filtered.length} trên {products.length} sản phẩm</span><span className="pagination"><button disabled><ChevronLeft size={15}/></button><button className="page-current">1</button><button disabled>2</button><button disabled><ChevronRight size={15}/></button></span></div>
    </section>
    {modalOpen&&<div className="modal-backdrop" onClick={()=>setModalOpen(false)}><form className="modal" onSubmit={save} onClick={e=>e.stopPropagation()}><div className="modal-heading"><div><span className="eyebrow">DANH MỤC / SẢN PHẨM</span><h2>{editing?'Chỉnh sửa sản phẩm':'Thêm sản phẩm mới'}</h2></div><button type="button" className="icon-button" onClick={()=>setModalOpen(false)}><X size={18}/></button></div><label className="form-field">Tên sản phẩm<input required value={form.name} onChange={e=>setForm({...form,name:e.target.value})} placeholder="Ví dụ: Áo thun basic"/></label><div className="form-row"><label className="form-field">Danh mục<select value={form.category} onChange={e=>setForm({...form,category:e.target.value})}>{['Áo','Áo sơ mi','Áo khoác','Quần dài','Váy'].map(c=><option key={c}>{c}</option>)}</select></label><label className="form-field">Màu sắc<select value={form.color} onChange={e=>setForm({...form,color:e.target.value})}>{['Trắng','Đen','Be','Xanh','Hồng'].map(c=><option key={c}>{c}</option>)}</select></label></div><div className="form-row"><label className="form-field">Giá bán (VND)<input type="number" min="0" required value={form.price} onChange={e=>setForm({...form,price:e.target.value})} placeholder="350000"/></label><label className="form-field">Số lượng tồn<input type="number" min="0" required value={form.stock} onChange={e=>setForm({...form,stock:e.target.value})} placeholder="50"/></label></div><div className="modal-actions"><button type="button" className="button button-outline" onClick={()=>setModalOpen(false)}>Hủy</button><button className="button button-dark" type="submit"><Check size={16}/> Lưu sản phẩm</button></div></form></div>}
  </div>;
}



function SimplePage({ page, setActive }) {
  const [saved, setSaved] = useState(false);
  const info = {
    categories: ['Danh mục','Quản lý các nhóm trang phục của cửa hàng.',['Áo','Áo khoác','Quần dài','Váy','Phụ kiện']],
    orders: ['Đơn hàng','Theo dõi tình trạng xử lý và giao hàng.',['Đang xử lý','Đang giao','Đã giao','Đã hủy']],
    customers: ['Khách hàng','Tổng hợp thông tin khách hàng.',['Khách hàng mới','Khách hàng thân thiết','Lịch sử mua hàng']],
    analytics: ['Thống kê','Các chỉ số mẫu phục vụ thiết kế dashboard.',['Doanh thu theo thời gian','Sản phẩm bán chạy','Tỷ lệ chuyển đổi']],
    settings: ['Cài đặt','Cấu hình cơ bản cho không gian quản trị.',['Thông tin cửa hàng','Tài khoản quản trị','Thông báo']]
  }[page] || ['Trang đang phát triển','Nội dung sẽ được bổ sung trong bước tiếp theo.',[]];
  return <div className="page-content"><div className="page-heading"><div><div className="eyebrow">STYLEFIT / QUẢN TRỊ</div><h1>{info[0]}<span className="heading-period">.</span></h1><p>{info[1]}</p></div></div><section className="panel simple-page-panel"><div className="simple-icon"><Activity size={24}/></div><h2>{info[0]}</h2><p>{info[1]}</p><div className="simple-list">{info[2].map((x,i)=><div key={x}><span className="simple-list-number">0{i+1}</span><strong>{x}</strong><ChevronRight size={16}/></div>)}</div><button className="button button-dark" onClick={()=>setSaved(!saved)}>{saved?<><Check size={16}/> Đã đánh dấu xem lại</>:<>Đánh dấu để hoàn thiện <ArrowRight size={16}/></>}</button><button className="text-link" onClick={()=>setActive('dashboard')}>Quay lại tổng quan</button></section></div>;
}


export default function App() {
  const [active, setActive] = useState('dashboard');
  const [products, setProducts] = useState(initialProducts);
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <Routes>
      <Route
        path="/"
        element={<Navigate to="/admin" replace />}
      />

      <Route
        path="/admin"
        element={
          <div className="app-shell">
            <Sidebar
              active={active}
              setActive={setActive}
              mobileOpen={mobileOpen}
              setMobileOpen={setMobileOpen}
            />

            <main className="main-area">
              <Topbar setMobileOpen={setMobileOpen} />

              {active === 'dashboard' ? (
                <Dashboard
                  products={products}
                  setActive={setActive}
                />
              ) : active === 'products' ? (
                <ProductsPage
                  products={products}
                  setProducts={setProducts}
                />
              ) : (
                <SimplePage
                  page={active}
                  setActive={setActive}
                />
              )}

              <footer className="admin-footer">
                <span>© 2026 StyleFit Studio</span>
                <span>
                  Designed with intention{' '}
                  <span className="footer-heart">♥</span>
                </span>
                <span className="build-label">
                  UI prototype · v1.0
                </span>
              </footer>
            </main>
          </div>
        }
      />

      <Route
        path="*"
        element={<Navigate to="/admin" replace />}
      />
    </Routes>
  );
}
