from enum import Enum


class BloodGroup(str, Enum):
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"


class UserRole(str, Enum):
    DONOR = "DONOR"
    REQUESTER = "REQUESTER"
    BOTH = "BOTH"
    ADMIN = "ADMIN"


class UrgencyLevel(str, Enum):
    CRITICAL = "CRITICAL"
    URGENT = "URGENT"
    SCHEDULED = "SCHEDULED"


class RequestStatus(str, Enum):
    OPEN = "OPEN"
    MATCHED = "MATCHED"
    FULFILLED = "FULFILLED"
    CANCELLED = "CANCELLED"


class MatchStatus(str, Enum):
    PENDING = "PENDING"
    NOTIFIED = "NOTIFIED"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    COMPLETED = "COMPLETED"


class AvailabilityStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    BUSY = "BUSY"
