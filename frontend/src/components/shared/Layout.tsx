import { Box, AppBar, Toolbar, Typography, Button } from '@mui/material';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

export const Layout = ({ children }: { children: React.ReactNode }) => {
  const { t } = useTranslation();
  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Merinozky Management
          </Typography>
          <Button color="inherit" component={Link} to="/orders">
            {t('orders_menu')}
          </Button>
          <Button color="inherit" component={Link} to="/products">
            {t('products_menu')}
          </Button>
        </Toolbar>
      </AppBar>
      <Box sx={{ p: 3 }}>
        {children}
      </Box>
    </Box>
  );
}
