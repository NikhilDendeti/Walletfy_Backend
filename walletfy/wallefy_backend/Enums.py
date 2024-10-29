from enum import Enum


class BaseEnum(Enum):
    @classmethod
    def list_of_values(cls):
        return [(i.value, i.name) for i in
                cls]  # Correct format for Django choices


class PreferenceChoices(BaseEnum):
    RICH = 'RICH'
    MIDDLE_CLASS = 'MIDDLE CLASS'
    POOR = 'POOR'


class GenderChoices(BaseEnum):
    MALE = 'MALE'
    FEMALE = 'FEMALE'
    OTHER = 'OTHER'


class RoleChoices(BaseEnum):
    STUDENT = 'Student'
    EMPLOYEE = 'Employee'


class LocationChoices(BaseEnum):
    HYDERABAD = 'Hyderabad'


class Category(BaseEnum):
    FOOD = "Food"
    ENTERTAINMENT = "Entertainment"
    TRAVEL = "Travel"
    HEALTH = "Health"
    MISCELLANEOUS = "Miscellaneous"
    RENT = "Rent"
    SAVINGS = "Savings"
    SHOPPING = "Shopping"
    INCOME = "Income"
    EXPENSE = "Expense"


class TransactionType(BaseEnum):
    INCOME = "Income"
    EXPENSE = "Expense"  # Corrected from tuple to string


class AreaEnum(BaseEnum):
    ALWAL = "ALWAL"
    AMBERPET = "AMBERPET"
    AMEERPET = "AMEERPET"
    ATTAPUR = "ATTAPUR"
    BACHUPALLY = "BACHUPALLY"
    BANJARA_HILLS = "BANJARA HILLS"
    BEGUMPET = "BEGUMPET"
    CHARMINAR = "CHARMINAR"
    DILSUKHNAGAR = "DILSUKHNAGAR"
    ECIL = "ECIL"
    GACHIBOWLI = "GACHIBOWLI"
    HAFIZ_BABA_NAGAR = "HAFIZ BABA NAGAR"
    HAYATH_NAGAR = "HAYATH NAGAR"
    HIMAYATNAGAR = "HIMAYATNAGAR"
    JEEDIMETLA = "JEEDIMETLA"
    JNTU = "JNTU"
    KARKHANA = "KARKHANA"
    KOMPALLY = "KOMPALLY"
    KONDAPUR = "KONDAPUR"
    KUKATPALLY = "KUKATPALLY"
    LB_NAGAR = "LB NAGAR"
    MADHAPUR = "MADHAPUR"
    MALAKPET = "MALAKPET"
    MANIKONDA = "MANIKONDA"
    MASAB_TANK = "MASAB TANK"
    MEDCHAL_ROAD = "MEDCHAL ROAD"
    MIYAPUR = "MIYAPUR"
    MOKILA = "MOKILA"
    MOOSAPET = "MOOSAPET"
    NAGOLE = "NAGOLE"
    NARAYANGUDA = "NARAYANGUDA"
    NIZAMPET = "NIZAMPET"
    PATANCHERU = "PATANCHERU"
    PEERZADIGUDA = "PEERZADIGUDA"
    Q_CITY = "Q CITY"
    SAINIKPURI = "SAINIKPURI"
    SANGAREDDY = "SANGAREDDY"
    SAROOR_NAGAR = "SAROOR NAGAR"
    SERILINGAMPALLY = "SERILINGAMPALLY"
    SHAMSHABAD = "SHAMSHABAD"
    SIVARAMPALLI = "SIVARAMPALLI"
    SURARAM = "SURARAM"
    TARNAKA = "TARNAKA"
    TOLI_CHOWKI = "TOLI CHOWKI"
    UPPAL = "UPPAL"
    VANASTHALIPURAM = "VANASTHALIPURAM"

