# app/routes/lease_routes.py

from flask import Blueprint
from app.controllers.lease_controller import  create_lease, read_leases_by_user_id, update_lease,delete_lease

lease_routes = Blueprint('lease_routes', __name__)


lease_routes.route('/', methods=['POST'])(create_lease)



lease_routes.route('/<user_id>', methods=['GET'])(read_leases_by_user_id)

lease_routes.route('/<lease_id>', methods=['PUT'])(update_lease)

lease_routes.route('/<lease_id>', methods=['DELETE'])(delete_lease)