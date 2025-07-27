import enum

class OrderStatus(enum.Enum):
    PENDING = 0
    ACCEPTED = 1
    DECLINED = 2
    DISPATCHED = 3
    SHIPPED = 4
    ARRIVED_AT_LOCAL_DP = 5
    OUT_FOR_DELIVERY = 6
    DELIVERED = 7
    CANCELLED = 8

    def __str__(self):
        return self.name

class PaymentStatus(enum.Enum):
    PENDING = 0
    SUCCESS = 1
    FAILED = 2

    def __str__(self):
        return self.name

class AdminNotifications(enum.Enum):
    ORDER_PLACED = 0
    ORDER_CANCELLED = 1
    PAYMENT_SUCCESSFUL = 2

    def __str__(self):
        return self.name

class NotificationStatus(enum.Enum):
    ACTIVE = 0
    VIEWED = 1

    def __str__(self):
        return self.name