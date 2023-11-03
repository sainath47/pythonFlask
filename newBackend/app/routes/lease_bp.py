# app/routes/lease.py

from flask import Blueprint, render_template

lease_bp = Blueprint('lease', __name__)

@lease_bp.route('/leases')
def list_leases():
    # Retrieve lease data from the database using your lease model
    # Replace this with actual data retrieval code
    leases = Lease.query.all()

    return render_template('lease/list.html', leases=leases)

@lease_bp.route('/leases/<int:lease_id>')
def view_lease(lease_id):
    # Retrieve lease data from the database using your lease model
    # Replace this with actual data retrieval code
    lease = Lease.query.get(lease_id)

    return render_template('lease/detail.html', lease=lease)
