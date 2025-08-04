import { Box, AppBar, Toolbar, Typography, Button } from '@mui/material';
import { Link } from 'react-router-dom';

export const Layout = ({ children }: { children: React.ReactNode }) => {
  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Merinozky Management
          </Typography>
          <Button color="inherit" component={Link} to="/orders">
            Orders
          </Button>
          <Button color="inherit" component={Link} to="/products">
            Products
          </Button>
        </Toolbar>
      </AppBar>
      <Box sx={{ p: 3 }}>
        {children}
      </Box>
    </Box>
  );
}
