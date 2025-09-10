import { TextField, Box, Typography, IconButton, InputAdornment, CardMedia, Button, Grid, Card, CardContent, Paper } from '@mui/material';
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
      p.code.toLowerCase().endsWith(searchTerm.toLowerCase())
    );
    setSearchResults(matchedProducts);
  };

  const handleKeyPress = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

  const handleQuantityChange = (code: string, value: number) => {
    setQuantities(prev => ({
      ...prev,
      [code]: isNaN(value) ? 1 : value
    }));
  };

  const handleAdjustment = (code: string) => {
    const quantity = quantities[code] ?? 1;  // Use nullish coalescing for default value
    if (quantity === 0) {
      showSnackbar(t('quantity_cannot_be_zero'), 'error');
      return;
    }
    addStockAdjustmentCode(code, quantity);
    // Reset quantity after adjustment
    setQuantities(prev => ({ ...prev, [code]: 1 }));
    showSnackbar(t('adjustment_added') + ' code: ' + code, 'success');
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
      <Grid container spacing={2}>
        <Paper sx={{ mt: 2, ml: 2, p: 2, height: '69vh', width: '100%', overflow: 'auto' }}>
        {searchResults.map((product) => (
          <Grid item xs={12} key={product.id}>
            <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1 }}>
              {product.code} - {product.title}
            </Typography>
            {product.variants && product.variants.length > 0 ? (
              product.variants.map((variant: ProductVariant) => (
                <Card key={variant.id} sx={{ mb: 2 }}>
                  <Grid container>
                    <Grid item xs={3} sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <CardMedia
                        component="img"
                        sx={{ 
                          height: '100%',
                          maxHeight: 180, 
                          objectFit: 'contain',
                          margin: 'auto'
                        }}
                        image={variant.image_url || ''}
                        alt={product.title || ''}
                      />
                    </Grid>
                    <Grid item xs={9} sx={{ display: 'flex' }}>
                      <CardContent sx={{ flexGrow: 1, p: 2 }}>
                        <Grid container sx={{ height: '100%' }}>
                          <Grid item xs={7}>
                            <Typography variant="subtitle1">{variant.code}</Typography>
                            <Box sx={{ mt: 1 }}>
                              <Typography variant="body2">
                                {t('stock')}: {variant.stock}
                              </Typography>
                              {variant.parameters && Object.entries(variant.parameters).map(([key, value]) => (
                                <Typography key={key} variant="body2">
                                  {formatParameterString(key, value)}
                                </Typography>
                              ))}
                              <Typography variant="body2" sx={{mt:2}}>
                                EAN: {variant.ean}
                              </Typography>
                            </Box>
                          </Grid>
                          <Grid item xs={5}>
                            <Box sx={{ 
                              display: 'flex', 
                              flexDirection: 'column', 
                              alignItems: 'flex-end',
                              height: '100%',
                              gap: 2
                            }}>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <IconButton size="small" onClick={() => handleQuantityChange(variant.code, (quantities[variant.code] ?? 1) - 1)}>
                                  <RemoveIcon />
                                </IconButton>
                                <input
                                  type="number"
                                  style={{ width: 60, textAlign: 'center' }}
                                  value={quantities[variant.code] ?? 1}
                                  onChange={(e) => handleQuantityChange(variant.code, parseInt(e.target.value))}
                                />
                                <IconButton size="small" onClick={() => handleQuantityChange(variant.code, (quantities[variant.code] ?? 1) + 1)}>
                                  <AddIcon />
                                </IconButton>
                              </Box>
                              <Button
                                variant="contained"
                                size="small"
                                sx={{ minWidth: 120 }}
                                onClick={() => handleAdjustment(variant.code)}
                              >
                                {t('add')}
                              </Button>
                            </Box>
                          </Grid>
                        </Grid>
                      </CardContent>
                    </Grid>
                  </Grid>
                </Card>
              ))
            ) : (
              <Card sx={{ mb: 2 }}>
                <Grid container>
                  <Grid item xs={3} sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <CardMedia
                      component="img"
                      sx={{ 
                        height: '100%',
                        maxHeight: 180, 
                        objectFit: 'contain',
                        margin: 'auto'
                      }}
                      image={product.image_url || ''}
                      alt={product.title || ''}
                    />
                  </Grid>
                  <Grid item xs={9} sx={{ display: 'flex' }}>
                    <CardContent sx={{ flexGrow: 1, p: 2 }}>
                      <Grid container sx={{ height: '100%' }}>
                        <Grid item xs={7}>
                          <Typography variant="subtitle1">{product.code}</Typography>
                          <Box sx={{ mt: 1 }}>
                            <Typography variant="body2">
                              {t('stock')}: {product.stock}
                            </Typography>
                            {product.parameters && Object.entries(product.parameters).map(([key, value]) => (
                              <Typography key={key} variant="body2">
                                {formatParameterString(key, value)}
                              </Typography>
                            ))}
                            <Typography variant="body2" sx={{mt:2}}>
                              EAN: {product.ean}
                            </Typography>
                          </Box>
                        </Grid>
                        <Grid item xs={5}>
                          <Box sx={{ 
                            display: 'flex', 
                            flexDirection: 'column', 
                            alignItems: 'flex-end',
                            height: '100%',
                            gap: 2
                          }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <IconButton size="small" onClick={() => handleQuantityChange(product.code, (quantities[product.code] ?? 1) - 1)}>
                                <RemoveIcon />
                              </IconButton>
                              <input
                                type="number"
                                style={{ width: 60, textAlign: 'center' }}
                                value={quantities[product.code] ?? 1}
                                onChange={(e) => handleQuantityChange(product.code, parseInt(e.target.value))}
                              />
                              <IconButton size="small" onClick={() => handleQuantityChange(product.code, (quantities[product.code] ?? 1) + 1)}>
                                <AddIcon />
                              </IconButton>
                            </Box>
                            <Button
                              variant="contained"
                              size="small"
                              sx={{ minWidth: 120 }}
                              onClick={() => handleAdjustment(product.code)}
                            >
                              {t('add')}
                            </Button>
                          </Box>
                        </Grid>
                      </Grid>
                    </CardContent>
                  </Grid>
                </Grid>
              </Card>
            )}
          </Grid>
        ))}
        </Paper>
      </Grid>
    </Box>
  );
};

