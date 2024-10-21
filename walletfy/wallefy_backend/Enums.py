from enum import Enum


class BaseEnum(Enum):
    @classmethod
    def list_of_values(cls):
        return [(i.value, i.name) for i in
                cls]  # Correct format for Django choices


class PreferenceChoices(BaseEnum):
    HIGH = 'High'
    MEDIUM = 'Medium'
    LOW = 'Low'


class GenderChoices(BaseEnum):
    MALE = 'Male'
    FEMALE = 'Female'
    OTHER = 'Other'


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


class TransactionType(BaseEnum):
    INCOME = "Income"
    EXPENSE = "Expense"  # Corrected from tuple to string


class AreaEnum(BaseEnum):
    ALWAL = "Alwal"
    AMBERPET = "Amberpet"
    AMEERPET = "Ameerpet"
    ATTAPUR = "Attapur"
    BACHUPALLY = "Bachupally"
    BANJARA_HILLS = "Banjara Hills"
    BEGUMPET = "Begumpet"
    CHARMINAR = "Charminar"
    DILSUKHNAGAR = "Dilsukhnagar"
    ECIL = "ECIL"
    GACHIBOWLI = "Gachibowli"
    HAFIZ_BABA_NAGAR = "Hafiz Baba Nagar"
    HAYATH_NAGAR = "Hayath Nagar"
    HIMAYATNAGAR = "Himayatnagar"
    JEEDIMETLA = "Jeedimetla"
    JNTU = "JNTU"
    KARKHANA = "Karkhana"
    KOMPALLY = "Kompally"
    KONDAPUR = "Kondapur"
    KUKATPALLY = "Kukatpally"
    LB_NAGAR = "LB Nagar"
    MADHAPUR = "Madhapur"
    MALAKPET = "Malakpet"
    MANIKONDA = "Manikonda"
    MASAB_TANK = "Masab Tank"
    MEDCHAL_ROAD = "Medchal Road"
    MIYAPUR = "Miyapur"
    MOKILA = "Mokila"
    MOOSAPET = "Moosapet"
    NAGOLE = "Nagole"
    NARAYANGUDA = "Narayanguda"
    NIZAMPET = "Nizampet"
    PATANCHERU = "Patancheru"
    PEERZADIGUDA = "Peerzadiguda"
    Q_CITY = "Q City"
    SAINIKPURI = "Sainikpuri"
    SANGAREDDY = "Sangareddy"
    SAROOR_NAGAR = "Saroor Nagar"
    SERILINGAMPALLY = "Serilingampally"
    SHAMSHABAD = "Shamshabad"
    SIVARAMPALLI = "Sivarampalli"
    SURARAM = "Suraram"
    TARNAKA = "Tarnaka"
    TOLI_CHOWKI = "Toli Chowki"
    UPPAL = "Uppal"
    VANASTHALIPURAM = "Vanasthalipuram"
