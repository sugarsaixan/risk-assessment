"""Database enum types for the risk assessment system."""

import enum


class ScoringMethod(str, enum.Enum):
    """Method used to calculate scores for a questionnaire type."""

    SUM = "SUM"


class RespondentKind(str, enum.Enum):
    """Type of respondent taking an assessment."""

    ORG = "ORG"
    PERSON = "PERSON"


class OptionType(str, enum.Enum):
    """Type of answer option for a question."""

    YES = "YES"
    NO = "NO"


class AssessmentStatus(str, enum.Enum):
    """Status of an assessment."""

    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    EXPIRED = "EXPIRED"


class RiskRating(str, enum.Enum):
    """Risk rating based on assessment score."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
