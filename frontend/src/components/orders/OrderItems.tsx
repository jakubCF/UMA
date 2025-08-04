import { Box, Typography, Grid, Card, CardContent, CardMedia, TextField, IconButton } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';
import { useState } from 'react';
import { useOrdersStore } from '../../store/ordersStore';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { green } from '@mui/material/colors';


// Helper function to format each parameter string
const formatParameterString = (key: string, value: any) => {
  if (typeof value === 'object' && value !== null) {
    return `${value.name || key}: ${value.value || JSON.stringify(value)}`;
  }
  return `${key}: ${value}`;
};

const OrderItems = () => {
  const { selectedOrder, updateItemPicked } = useOrdersStore();
  const [pickedQuantities, setPickedQuantities] = useState<Record<number, number>>({});

  const handlePickedChange = (itemId: number, value: number) => {
    const item = selectedOrder()?.items.find(i => i.id === itemId);
    if (!item) return;

    const newValue = Math.max(0, Math.min(value, item.quantity));
    setPickedQuantities(prev => ({ ...prev, [itemId]: newValue }));
    updateItemPicked(selectedOrder()!.id, itemId, newValue);
  };

  if (!selectedOrder()) {
    return <Typography>Select an order to view items</Typography>;
  }

  return (
    // set box to max-height to display and enable scrolling
    <Box>
      <Typography variant="h6" gutterBottom>Order Items</Typography>
      <Grid container spacing={2}>
        {selectedOrder()!.items.map((item) => (
          <Grid item xs={12} key={item.id}>
            <Card>
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
                    image={item.image_url || ''}
                    alt={item.title || ''}
                  />
                </Grid>
                <Grid item xs={9} sx={{ display: 'flex' }}>
                  <CardContent sx={{ flexGrow: 1, p: 2 }}>
                    <Grid container sx={{ height: '100%' }}>
                      {/* Left Column: All the main item details */}
                      <Grid item xs={7}>
                        <Typography variant="subtitle1">Code: {item.code}</Typography>
                        <Typography variant="body2">{item.title}</Typography>
                        
                        {/* The new way to display parameters, each on its own line */}
                        <Box sx={{ mt: 1 }}> {/* Add some top margin for spacing */}
                          {item.parameters && Object.entries(item.parameters).map(([key, value]) => (
                            <Typography 
                              key={key}  
                              variant="body2" 
                            >
                              {formatParameterString(key, value)}
                            </Typography>
                          ))}
                        </Box>
                        <Typography variant="body2" sx={{mt:2}}>EAN: {item.ean}</Typography>
                      </Grid>

                      {/* Right Column: Quantity and selector */}
                      <Grid item xs={5}>
                        <Box 
                          sx={{ 
                            display: 'flex', 
                            flexDirection: 'column', 
                            alignItems: 'flex-end',
                            height: '100%', 
                            justifyContent: 'space-between',
                          }}
                        >
                          {/* Top-right quantity display with conditional checkmark */}
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                            {item.uma_picked === 'picked' && (
                              <CheckCircleIcon sx={{ color: green[500], fontSize: 24 }} />
                            )}
                            <Typography variant="body1" fontSize={"14pt"}>
                              {pickedQuantities[item.id] || 0} / {Number(item.quantity)}
                            </Typography>
                          </Box>

                          {/* New Box to group the two bottom elements (Second element) */}
                          <Box 
                            sx={{ 
                              display: 'flex', 
                              flexDirection: 'column', 
                              alignItems: 'flex-end', 
                              gap: 1
                            }}
                          >
                            {/* Bottom-right quantity selector */}
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Typography variant="body2" fontSize={"14pt"}>Picked:</Typography>
                              <IconButton 
                                size="small"
                                onClick={() => handlePickedChange(item.id, (pickedQuantities[item.id] || 0) - 1)}
                              >
                                <RemoveIcon />
                              </IconButton>
                              <TextField
                                id='picked-quantity'
                                size="small"
                                type="number"
                                value={pickedQuantities[item.id] || 0}
                                onChange={(e) => handlePickedChange(item.id, Number(e.target.value))}
                                sx={{ width: 60 }}
                              />
                              <IconButton 
                                size="small"
                                onClick={() => handlePickedChange(item.id, (pickedQuantities[item.id] || 0) + 1)}
                              >
                                <AddIcon />
                              </IconButton>
                            </Box>
                            
                            {/* Status Typography - This is now in the correct place */}
                            <Typography variant="body2">Status: {item.uma_picked}</Typography>
                          </Box>
                        </Box>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Grid>
              </Grid>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default OrderItems;
