import { Box, Typography, Grid, Card, CardContent, CardMedia, TextField, IconButton, Snackbar, Alert, Button, Dialog, DialogTitle, DialogContent, DialogActions } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';
import React, { useState, useEffect, useCallback } from 'react';
import { useOrdersStore } from '../../store/ordersStore';
import { PickStatus} from '../../types/orders';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { green } from '@mui/material/colors';
import { useTranslation } from 'react-i18next';


// Helper function to format each parameter string
const formatParameterString = (key: string, value: any) => {
  if (typeof value === 'object' && value !== null) {
    return `${value.name || key}: ${value.value || JSON.stringify(value)}`;
  }
  return `${key}: ${value}`;
};

const OrderItems = () => {
  const { t } = useTranslation();
  const { selectedOrderId, updateOrderStatus, pickedQuantities, setPickedQuantity } = useOrdersStore();
  const selectedOrderObj = useOrdersStore(state => state.selectedOrder());
  const [ItemStatus, setItemStatus] = useState<Record<number, PickStatus>>({});

  // State for Snackbar messages
  const [isSnackbarOpen, setIsSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState<'success' | 'info' | 'error' | 'warning'>('info');

  // State for the Order Fulfilled Dialog
  const [isOrderFulfilledDialogOpen, setIsOrderFulfilledDialogOpen] = useState(false);

  // State for barcode scanner input buffer
  const [scanBuffer, setScanBuffer] = useState<string>('');
  const SCAN_DEBOUNCE_MS = 100; // Small debounce for scanner input

  // Initialize pickedQuantities when selectedOrder changes
  useEffect(() => {
    // if (selectedOrderObj) {
    //   console.log('Selected Order:', selectedOrderObj);
    //   const initialQuantities: Record<number, number> = {};
    //   selectedOrderObj!.items.forEach(item => {
    //     // Initialize from actual picked quantity if available, otherwise 0
    //     // Or if 'uma_picked' status implies a full quantity, use that.
    //     // Assuming you track actual picked count somewhere, or it's implicitly 0 unless 'picked'
    //     if (item.uma_picked === 'picked') {
    //       console.log(`Item ${item.id} is picked, setting initial quantity to full: ${item.quantity}`);
    //       initialQuantities[item.id] = Number(item.quantity); // Full quantity if picked
    //     } 
    //     // else {
    //     //   initialQuantities[item.id] = 0; // Default to 0 if not picked
    //     // }
    //   });
    //    setPickedQuantities(initialQuantities);
    //  } 
    // else {
    //   setPickedQuantities({}); // Clear quantities if no order selected
    // }
    setScanBuffer(''); // Clear scan buffer when order changes
  }, [selectedOrderObj, selectedOrderId]);

  const handlePickedChange = useCallback((itemId: number, value: number) => {
    const item = selectedOrderObj?.items.find(i => i.id === itemId);
    if (!item) return;

    const newValue = Math.max(0, Math.min(value, Number(item.quantity)));
    
    // Only update if the quantity actually changes or status needs to be updated.
    // This prevents unnecessary API calls if the user tries to increment beyond max, etc.
    if (pickedQuantities[itemId] !== newValue) {
      setPickedQuantity(itemId, newValue); // Update local state
      
      //updateItemPicked(selectedOrderObj!.id, itemId, newValue);

      // Show success message only on successful increment from interaction
      if (newValue > (pickedQuantities[itemId] || 0)) {
        setSnackbarMessage(t('item_scanned_success', { itemTitle: item.code, currentQty: newValue, totalQty: item.quantity }));
        setSnackbarSeverity('success');
        setIsSnackbarOpen(true);
      }
      if (Number(item.quantity) === newValue) {
        console.log(`Item ${itemId} fully picked, updating status to 'picked'`);
        setItemStatus(prev => ({ ...prev, [itemId]: 'picked' }));
      }
      else if (newValue === 0) {
        console.log(`Item ${itemId} not picked, updating status to 'not_picked'`);
        setItemStatus(prev => ({ ...prev, [itemId]: 'not_picked' }));
      }
      else if (newValue < Number(item.quantity) && newValue > 0) {
        console.log(`Item ${itemId} partially picked, updating status to 'partially_picked'`);
        setItemStatus(prev => ({ ...prev, [itemId]: 'partially_picked' }));
      }
      // Check if all items are fully picked (after this change)
      const tempPickedQuantities = { ...pickedQuantities, [itemId]: newValue };
      
      const allPicked = selectedOrderObj!.items.every(i => { // Use selectedOrderObj!.items
        const pickedQty = (i.id === itemId) ? newValue : (tempPickedQuantities[i.id] || 0); // Use tempPickedQuantities
        return pickedQty >= Number(i.quantity);
      });

      // If all items are picked, open the fulfillment dialog
      if (allPicked) {
        setIsOrderFulfilledDialogOpen(true);
      }
    }
  }, [selectedOrderObj, pickedQuantities, setPickedQuantity, t]);

  const processScannedEAN = useCallback((ean: string) => {
    const order = selectedOrderObj;
    if (!order) {
      setSnackbarMessage(t('no_order_selected_scan_error'));
      setSnackbarSeverity('warning');
      setIsSnackbarOpen(true);
      return;
    }

    const itemToUpdate = order.items.find(item => item.ean === ean);

    if (itemToUpdate) {
      const currentPicked = pickedQuantities[itemToUpdate.id] || 0;
      const maxQuantity = Number(itemToUpdate.quantity);

      if (currentPicked < maxQuantity) {
        // Increment quantity by 1
        handlePickedChange(itemToUpdate.id, currentPicked + 1);
        // Success message handled by handlePickedChange
      } else {
        setSnackbarMessage(t('quantity_exceeded_error', { itemTitle: itemToUpdate.code, currentQty: currentPicked, totalQty: maxQuantity }));
        setSnackbarSeverity('warning');
        setIsSnackbarOpen(true);
      }
    } else {
      setSnackbarMessage(t('ean_not_found_error', { ean: ean }));
      setSnackbarSeverity('error');
      setIsSnackbarOpen(true);
    }
  }, [selectedOrderObj, pickedQuantities, handlePickedChange, t]);

  // Barcode Scanner Logic
  useEffect(() => {
    let timeout: NodeJS.Timeout;

    const handleKeyDown = (event: KeyboardEvent) => {
      // Ignore modifier keys and ensure an order is selected
      if ((event.key.length > 1 && event.key !== 'Enter') || !selectedOrderObj) {
        return;
      }

      clearTimeout(timeout); // Clear any existing debounce timeout

      if (event.key === 'Enter') {
        event.preventDefault(); // Prevent newline in text fields/other default behavior
        processScannedEAN(scanBuffer);
        setScanBuffer(''); // Clear buffer after processing
      } else {
        setScanBuffer(prev => prev + event.key); // Accumulate keystrokes
      }

      // Set a timeout to clear the buffer if no new key is pressed within SCAN_DEBOUNCE_MS
      timeout = setTimeout(() => {
        setScanBuffer('');
      }, SCAN_DEBOUNCE_MS);
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      clearTimeout(timeout); // Clean up timeout on unmount
    };
  }, [scanBuffer, selectedOrderObj, handlePickedChange, processScannedEAN, t]); // Add t as a dependency


  const handleSnackbarClose = (event?: React.SyntheticEvent | Event, reason?: string) => {
    if (reason === 'clickaway') {
      return;
    }
    setIsSnackbarOpen(false);
  };

  const handleMarkOrderPacked = async () => {
    if (!selectedOrderObj) return;

    // Prepare items data to send to backend
    const itemsToUpdate = selectedOrderObj.items.map(item => {
      const finalPickedQty = pickedQuantities[item.id] || 0;
      const totalQuantity = Number(item.quantity);

      // Determine the final status based on picked quantity
      let finalUmaPickedStatus: 'not_picked' | 'partially_picked' | 'picked';
      if (finalPickedQty >= totalQuantity) {
        finalUmaPickedStatus = 'picked';
      } else if (finalPickedQty > 0) {
        finalUmaPickedStatus = 'partially_picked';
      } else {
        finalUmaPickedStatus = 'not_picked';
      }

      return {
        id: item.id,
        uma_picked: finalUmaPickedStatus,
      };
    });

    try {
      // Call the store action to update the order status and all item statuses/quantities
      // Assuming updateOrderCompleted can now accept an array of item updates
      await updateOrderStatus(selectedOrderObj.id, 'completed', itemsToUpdate); // Pass itemsToUpdate
      setIsOrderFulfilledDialogOpen(false); // Close the dialog
      // You might want to show a success Snackbar after marking order as picked if desired
      setSnackbarMessage(t('order_marked_as_picked_success'));
      setSnackbarSeverity('success');
      setIsSnackbarOpen(true);
    } catch (error) {
      console.error('Failed to mark order as picked:', error);
      setSnackbarMessage(t('order_marked_as_picked_error'));
      setSnackbarSeverity('error');
      setIsSnackbarOpen(true);
    }
  };

  const handleCloseOrderFulfilledDialog = () => {
    setIsOrderFulfilledDialogOpen(false);
  };

  if (!selectedOrderObj) {
    return <Typography>{t('select_order_items')}</Typography>;
  }

  const sortedItems = [...selectedOrderObj.items].sort((a, b) => {
    // Regex to extract digits from the string (e.g., "P00170-5" -> "00170", "5")
    const extractNumbers = (code: string) => {
      // Find all sequences of digits
      const matches = code.match(/\d+/g); 
      // Join them and convert to a number for comparison. 
      // If no numbers, treat as 0 or handle as string later.
      return matches ? parseInt(matches.join('').padEnd(10,"0"), 10) : 0; 
    };

    const numA = extractNumbers(a.code);
    const numB = extractNumbers(b.code);

    if (numA !== numB) {
      return numA - numB; // Sort by the extracted number
    } else {
      // If numeric parts are identical, sort by the full string code
      return a.code.localeCompare(b.code);
    }
  });

  return (
    // set box to max-height to display and enable scrolling
    <Box>
      <Typography variant="h6" gutterBottom>{t('order_items')}</Typography>
      <Grid container spacing={2}>
        {sortedItems.map((item) => (
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
                        <Typography variant="subtitle1">{t('code')} {item.code}</Typography>
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
                            {ItemStatus[item.id] === 'picked' && (
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
                              <Typography variant="body2" fontSize={"14pt"}>{t('picked')}</Typography>
                              <IconButton 
                                size="small"
                                onClick={() => handlePickedChange(item.id, (pickedQuantities[item.id] || 0) - 1)}
                              >
                                <RemoveIcon />
                              </IconButton>
                              <TextField
                                id={`picked-quantity-${item.id}`}
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
                            <Typography variant="body2">{t('status')}: {t(`status_${ItemStatus[item.id] || 'not_picked'}`)}</Typography>
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
        <Snackbar 
        open={isSnackbarOpen} 
        autoHideDuration={6000} 
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert 
          onClose={handleSnackbarClose} 
          severity={snackbarSeverity} 
          sx={{ 
            minWidth: 300, // Ensure a minimum width for larger appearance
            fontSize: '1.2rem', // Bigger font size
            padding: '16px 24px', // Increase padding for a larger alert box
            display: 'flex', // Ensure flex for centering content
            alignItems: 'center', // Center content vertically
            justifyContent: 'center', // Center content horizontally
            textAlign: 'center' // Ensure text aligns centrally
          }} 
        >
          {snackbarMessage}
        </Alert>
      </Snackbar>
      </Grid>
      {/* Order Fulfilled Dialog */}
      <Dialog open={isOrderFulfilledDialogOpen} onClose={handleCloseOrderFulfilledDialog}>
        <DialogTitle>{t('order_fulfilled_title')}</DialogTitle>
        <DialogContent>
          <Typography>{t('order_fulfilled_message')}</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseOrderFulfilledDialog} color="primary" variant="contained">
            {t('continue_picking')}
          </Button>
          <Button onClick={handleMarkOrderPacked} color="success" variant="contained">
            {t('mark_order_picked')}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default OrderItems;