class OrderStatus:
    PROCESSING = 'processing'
    PACKED = 'packed'
    LABEL_PENDING = 'label_pending'
    LABEL_CREATED = 'label_created'
    LABEL_PRINTED = 'label_printed'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    ERROR = 'error'

    CHOICES = [
        (PROCESSING, 'Processing'),
        (PACKED, 'Packed'),
        (LABEL_PENDING, 'Label Pending'),
        (LABEL_CREATED, 'Label Created'),
        (LABEL_PRINTED, 'Label Printed'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
        (ERROR, 'Error'),
    ]

class OrderItemPickStatus:
    PICKED = 'picked'
    NOT_PICKED = 'not_picked'
    PARTIALLY_PICKED = 'partially_picked'

    CHOICES = [
        (PICKED, 'Picked'),
        (NOT_PICKED, 'Not Picked'),
        (PARTIALLY_PICKED, 'Partially Picked'),
    ]