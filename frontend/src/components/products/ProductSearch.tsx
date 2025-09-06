import { TextField, List, ListItem, Box, Typography, IconButton, InputAdornment, CardMedia, Button, Grid } from '@mui/material';
import { useState, KeyboardEvent } from 'react';
import { useTranslation } from 'react-i18next';
import SearchIcon from '@mui/icons-material/Search';
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';
import { useProductsStore } from '../../store/productsStore';
import { ProductVariant } from '../../types/products';

// Interface for the showSnackbar prop that this component expects
interface ProductPageProps {
  showSnackbar: (message: string, severity: 'success' | 'info' | 'error' | 'warning') => void;
}

// Helper function to format each parameter string
const formatParameterString = (key: string, value: any) => {
  if (typeof value === 'object' && value !== null) {
    return `${value.name || key}: ${value.value || JSON.stringify(value)}`;
  }
  return `${key}: ${value}`;
};

export const ProductSearch: React.FC<ProductPageProps> = ({ showSnackbar }) => {
  const { t } = useTranslation();
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const { products, addStockAdjustmentCode } = useProductsStore();
  const [quantities, setQuantities] = useState<{ [key: string]: number }>({});

  const handleSearch = () => {
    if (!searchTerm) {
      setSearchResults([]);
      return;
    }
    const matchedProducts = products.filter(p => 
      p.code.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setSearchResults(matchedProducts);
  };

  const handleKeyPress = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

  const handleQuantityChange = (variantId: number, value: number) => {
    setQuantities(prev => ({
      ...prev,
      [variantId]: Math.max(1, value)
    }));
  };

  const handleAdjustment = (variant: ProductVariant) => {
    const quantity = quantities[variant.id] || 1;
    addStockAdjustmentCode(variant.code, quantity);
    // Reset quantity after adjustment
    setQuantities(prev => ({ ...prev, [variant.id]: 1 }));
    showSnackbar( t('adjustment_added') + ' code: ' + variant.code , 'success');
  };

  return (
    <Box>
      <TextField
        fullWidth
        label={t('search_product_code')}
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        onKeyPress={handleKeyPress}
        margin="normal"
        InputProps={{
          endAdornment: (
            <InputAdornment position="end">
              <IconButton onClick={handleSearch}>
                <SearchIcon />
              </IconButton>
            </InputAdornment>
          ),
        }}
      />
      <List>
        {searchResults.map((product) => (
          <Box key={product.id} sx={{ mb: 2 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
              {product.code} - {product.title}
            </Typography>
            <List sx={{ pl: 2 }}>
              {product.variants.map((variant:ProductVariant) => (
                <ListItem key={variant.id}>
                  <Grid container spacing={2} alignItems="center">
                    <Grid item xs={4}>
                      <CardMedia
                        component="img"
                        sx={{ 
                          width: '100%',
                          maxHeight: 180, 
                          objectFit: 'contain',
                        }}
                        image={variant.image_url || ''}
                        alt={product.title || ''}
                      />
                    </Grid>
                    <Grid item xs={5}>
                      <Box>
                        <Typography variant="body1">
                          {variant.code}
                        </Typography>
                        <Box sx={{ mt: 1 }}>
                          <Typography variant="body2">
                            {t('stock')}: {variant.stock}
                          </Typography>
                          <Box sx={{ mt: 1 }}>
                            {variant.parameters && Object.entries(variant.parameters).map(([key, value]) => (
                              <Typography key={key} variant="body2">
                                {formatParameterString(key, value)}
                              </Typography>
                            ))}
                          </Box>
                          <Typography variant="body2">
                            EAN: {variant.ean}
                          </Typography>
                        </Box>
                      </Box>
                    </Grid>
                    <Grid item xs={3}>
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, alignItems: 'center' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <IconButton size="small" onClick={() => handleQuantityChange(variant.id, (quantities[variant.id] || 1) - 1)}>
                            <RemoveIcon />
                          </IconButton>
                          <input
                            type="number"
                            min="1"
                            style={{ width: 60, textAlign: 'center' }}
                            value={quantities[variant.id] || 1}
                            onChange={(e) => handleQuantityChange(variant.id, parseInt(e.target.value) || 1)}
                          />
                          <IconButton size="small" onClick={() => handleQuantityChange(variant.id, (quantities[variant.id] || 1) + 1)}>
                            <AddIcon />
                          </IconButton>
                        </Box>
                        <Button
                          variant="contained"
                          size="small"
                          fullWidth
                          onClick={() => handleAdjustment(variant)}
                        >
                          {t('add')}
                        </Button>
                      </Box>
                    </Grid>
                  </Grid>
                </ListItem>
              ))}
            </List>
          </Box>
        ))}
      </List>
    </Box>
  );
};

