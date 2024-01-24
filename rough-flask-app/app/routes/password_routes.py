# app/routes/lease_routes.py

from flask import Blueprint
from app.controllers.password_controller import forgotPasswordRequestOTP , forgotPasswordVerifyOTP, forgotPasswordSetNewPassword

password_routes = Blueprint('otp_routes', __name__)


password_routes.route('/forgot-password/request-otp', methods=['POST'])(forgotPasswordRequestOTP)
password_routes.route('/api/forgot-password/verify-otp', methods=['POST'])(forgotPasswordVerifyOTP)
password_routes.route('/api/forgot-password-set-new-password', methods=['POST'])(forgotPasswordSetNewPassword)


