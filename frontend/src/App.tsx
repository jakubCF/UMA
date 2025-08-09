import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './components/shared/Layout';
import { ProductsPage } from './pages/ProductsPage';
import { OrdersPage } from './pages/OrdersPage';
import './i18n';

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/products" element={<ProductsPage />} />
          <Route path="/orders" element={<OrdersPage />} />
          <Route path="/" element={<OrdersPage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
