"""Frontend pages package"""

from .welcome_page import WelcomePage
from .register_hospital_page import RegisterHospitalPage
from .register_user_page import RegisterUserPage
from .login_page import LoginPage
from .hospital_login_page import HospitalLoginPage
from .dashboard_page import DashboardPage
from .hospital_dashboard_page import HospitalDashboardPage
from .add_donation_page import AddDonationPage
from .view_inventory_page import ViewInventoryPage
from .search_blood_page import SearchBloodPage
from .transaction_history_page import TransactionHistoryPage
from .admin_dashboard_page import AdminDashboardPage
from .hospital_blood_requests_page import HospitalBloodRequestsPage
from .hospital_donations_page import HospitalDonationsPage
from .hospital_change_password_page import HospitalChangePasswordPage
from .hospital_inventory_page import HospitalInventoryPage

__all__ = [
    'WelcomePage',
    'RegisterHospitalPage',
    'RegisterUserPage',
    'LoginPage',
    'HospitalLoginPage',
    'DashboardPage',
    'HospitalDashboardPage',
    'AddDonationPage',
    'ViewInventoryPage',
    'SearchBloodPage',
    'TransactionHistoryPage',
    'AdminDashboardPage',
    'HospitalBloodRequestsPage',
    'HospitalDonationsPage',
    'HospitalChangePasswordPage',
    'HospitalInventoryPage'
]
