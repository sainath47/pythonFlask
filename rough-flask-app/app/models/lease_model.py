# app/models/lease_model.py
from app import db
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import func


class Lease(db.Model):
    __tablename__ = 'leases'

    lease_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    site_id = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(255), nullable=True)
    document_type = db.Column(db.String(255), nullable=True)
    building = db.Column(db.String(255), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    floor = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(255), nullable=True)
    state_district_province = db.Column(db.String(255), nullable=True)
    country_code = db.Column(db.String(10), nullable=True)
    country_name = db.Column(db.String(255), nullable=True)
    sub_region = db.Column(db.String(255), nullable=True)
    region = db.Column(db.String(255), nullable=True)
    postal_code = db.Column(db.String(20), nullable=True)
    latitude = db.Column(db.String(20), nullable=True)
    longitude = db.Column(db.String(20), nullable=True)
    space_use = db.Column(db.String(255), nullable=True)
    business_unit = db.Column(db.String(255), nullable=True)
    rentable_sf = db.Column(db.String(20), nullable=True)
    annualized_base_rent = db.Column(db.String(20), nullable=True)
    additional_facilities_cost = db.Column(db.String(20), nullable=True)
    facilities_cost_fully_loaded = db.Column(db.String(20), nullable=True)
    capacity_seats = db.Column(db.String(20), nullable=True)
    parking_capacity = db.Column(db.String(20), nullable=True)
    vacant = db.Column(db.String(3), nullable=True)
    total_employee_hc = db.Column(db.String(20), nullable=True)
    total_occupancy_hc = db.Column(db.String(20), nullable=True)
    surplus_deficit_seat_capacity = db.Column(db.String(20), nullable=True)
    sf_employee = db.Column(db.String(20), nullable=True)
    sf_occupant = db.Column(db.String(20), nullable=True)
    sf_seat = db.Column(db.String(20), nullable=True)
    cost_sf_1 = db.Column(db.String(20), nullable=True)
    cost_employee = db.Column(db.String(20), nullable=True)
    cost_occupant = db.Column(db.String(20), nullable=True)
    cost_seat = db.Column(db.String(20), nullable=True)
    cost_sf = db.Column(db.String(20), nullable=True)
    revenues = db.Column(db.String(20), nullable=True)
    sga = db.Column(db.String(20), nullable=True)
    opex_total_revenues = db.Column(db.String(20), nullable=True)
    opex_sga = db.Column(db.String(20), nullable=True)
    legacy_company = db.Column(db.String(255), nullable=True)
    verified_yn = db.Column(db.String(3), nullable=True)
    lease_type = db.Column(db.String(255), nullable=True)
    leased_owned = db.Column(db.String(255), nullable=True)
    client_position = db.Column(db.String(255), nullable=True)
    lease_commencement_date = db.Column(db.String(20), nullable=True)
    lease_expiration_date = db.Column(db.String(20), nullable=True)
    lease_expiration_year = db.Column(db.String(10), nullable=True)
    rmo_months = db.Column(db.String(20), nullable=True)
    critical_decision_date = db.Column(db.String(20), nullable=True)
    strategy_type = db.Column(db.String(255), nullable=True)
    strategy_real_estate_initiative = db.Column(db.String(255), nullable=True)
    strategy_optional_committed_or_na = db.Column(db.String(255), nullable=True)
    strategy_reduction_addition_or_as_is = db.Column(db.String(255), nullable=True)
    strategy_year_of_change_yyyy = db.Column(db.String(10), nullable=True)
    strategy_quarter_of_change = db.Column(db.String(5), nullable=True)
    strategy_head_count_adjustment_in_year_of_change = db.Column(db.String(20), nullable=True)
    strategy_seat_count_adjustment_in_year_of_change = db.Column(db.String(20), nullable=True)
    strategy_square_foot_adjustment_in_year_of_change = db.Column(db.String(20), nullable=True)
    strategy_occupancy_adjustment_in_year_of_change = db.Column(db.String(20), nullable=True)
    strategy_notes = db.Column(db.String(255), nullable=True)
    strategy_top_opportunities = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.TIMESTAMP, nullable=True, default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, nullable=True, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    is_deleted = db.Column(db.Boolean, nullable=True, default=False)

    
    def to_dict(self):
        """
        Convert the Lease model instance to a dictionary.

        Returns:
            dict: A dictionary representation of the Lease model.
        """
        return {
            'lease_id': self.lease_id,
            'site_id': self.site_id,
            'status': self.status,
            'document_type': self.document_type,
            'building': self.building,
            'address': self.address,
            'floor': self.floor,
            'city': self.city,
            'state_district_province': self.state_district_province,
            'country_code': self.country_code,
            'country_name': self.country_name,
            'sub_region': self.sub_region,
            'region': self.region,
            'postal_code': self.postal_code,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'space_use': self.space_use,
            'business_unit': self.business_unit,
            'rentable_sf': self.rentable_sf,
            'annualized_base_rent': self.annualized_base_rent,
            'additional_facilities_cost': self.additional_facilities_cost,
            'facilities_cost_fully_loaded': self.facilities_cost_fully_loaded,
            'capacity_seats': self.capacity_seats,
            'parking_capacity': self.parking_capacity,
            'vacant': self.vacant,
            'total_employee_hc': self.total_employee_hc,
            'total_occupancy_hc': self.total_occupancy_hc,
            'surplus_deficit_seat_capacity': self.surplus_deficit_seat_capacity,
            'sf_employee': self.sf_employee,
            'sf_occupant': self.sf_occupant,
            'sf_seat': self.sf_seat,
            'cost_sf_1': self.cost_sf_1,
            'cost_employee': self.cost_employee,
            'cost_occupant': self.cost_occupant,
            'cost_seat': self.cost_seat,
            'cost_sf': self.cost_sf,
            'revenues': self.revenues,
            'sga': self.sga,
            'opex_total_revenues': self.opex_total_revenues,
            'opex_sga': self.opex_sga,
            'legacy_company': self.legacy_company,
            'verified_yn': self.verified_yn,
            'lease_type': self.lease_type,
            'leased_owned': self.leased_owned,
            'client_position': self.client_position,
            'lease_commencement_date': self.lease_commencement_date,
            'lease_expiration_date': self.lease_expiration_date,
            'lease_expiration_year': self.lease_expiration_year,
            'rmo_months': self.rmo_months,
            'critical_decision_date': self.critical_decision_date,
            'strategy_type': self.strategy_type,
            'strategy_real_estate_initiative': self.strategy_real_estate_initiative,
            'strategy_optional_committed_or_na': self.strategy_optional_committed_or_na,
            'strategy_reduction_addition_or_as_is': self.strategy_reduction_addition_or_as_is,
            'strategy_year_of_change_yyyy': self.strategy_year_of_change_yyyy,
            'strategy_quarter_of_change': self.strategy_quarter_of_change,
            'strategy_head_count_adjustment_in_year_of_change': self.strategy_head_count_adjustment_in_year_of_change,
            'strategy_seat_count_adjustment_in_year_of_change': self.strategy_seat_count_adjustment_in_year_of_change,
            'strategy_square_foot_adjustment_in_year_of_change': self.strategy_square_foot_adjustment_in_year_of_change,
            'strategy_occupancy_adjustment_in_year_of_change': self.strategy_occupancy_adjustment_in_year_of_change,
            'strategy_notes': self.strategy_notes,
            'strategy_top_opportunities': self.strategy_top_opportunities,
            'user_id': self.user_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_deleted': self.is_deleted
        }

    def __init__(self, site_id, status, document_type, building, address, floor, city, state_district_province,
                 country_code, country_name, sub_region, region, postal_code, latitude, longitude, space_use, business_unit,
                 rentable_sf, annualized_base_rent, additional_facilities_cost, facilities_cost_fully_loaded, capacity_seats,
                 parking_capacity, vacant, total_employee_hc, total_occupancy_hc, surplus_deficit_seat_capacity, sf_employee,
                 sf_occupant, sf_seat, cost_sf_1, cost_employee, cost_occupant, cost_seat, cost_sf, revenues, sga, opex_total_revenues,
                 opex_sga, legacy_company, verified_yn, lease_type, leased_owned, client_position, lease_commencement_date,
                 lease_expiration_date, lease_expiration_year, rmo_months, critical_decision_date, strategy_type,
                 strategy_real_estate_initiative, strategy_optional_committed_or_na, strategy_reduction_addition_or_as_is,
                 strategy_year_of_change_yyyy, strategy_quarter_of_change, strategy_head_count_adjustment_in_year_of_change,
                 strategy_seat_count_adjustment_in_year_of_change, strategy_square_foot_adjustment_in_year_of_change,
                 strategy_occupancy_adjustment_in_year_of_change, strategy_notes, strategy_top_opportunities, user_id):

        self.site_id = site_id
        self.status = status
        self.document_type = document_type
        self.building = building
        self.address = address
        self.floor = floor
        self.city = city
        self.state_district_province = state_district_province
        self.country_code = country_code
        self.country_name = country_name
        self.sub_region = sub_region
        self.region = region
        self.postal_code = postal_code
        self.latitude = latitude
        self.longitude = longitude
        self.space_use = space_use
        self.business_unit = business_unit
        self.rentable_sf = rentable_sf
        self.annualized_base_rent = annualized_base_rent
        self.additional_facilities_cost = additional_facilities_cost
        self.facilities_cost_fully_loaded = facilities_cost_fully_loaded
        self.capacity_seats = capacity_seats
        self.parking_capacity = parking_capacity
        self.vacant = vacant
        self.total_employee_hc = total_employee_hc
        self.total_occupancy_hc = total_occupancy_hc
        self.surplus_deficit_seat_capacity = surplus_deficit_seat_capacity
        self.sf_employee = sf_employee
        self.sf_occupant = sf_occupant
        self.sf_seat = sf_seat
        self.cost_sf_1 = cost_sf_1
        self.cost_employee = cost_employee
        self.cost_occupant = cost_occupant
        self.cost_seat = cost_seat
        self.cost_sf = cost_sf
        self.revenues = revenues
        self.sga = sga
        self.opex_total_revenues = opex_total_revenues
        self.opex_sga = opex_sga
        self.legacy_company = legacy_company
        self.verified_yn = verified_yn
        self.lease_type = lease_type
        self.leased_owned = leased_owned
        self.client_position = client_position
        self.lease_commencement_date = lease_commencement_date
        self.lease_expiration_date = lease_expiration_date
        self.lease_expiration_year = lease_expiration_year
        self.rmo_months = rmo_months
        self.critical_decision_date = critical_decision_date
        self.strategy_type = strategy_type
        self.strategy_real_estate_initiative = strategy_real_estate_initiative
        self.strategy_optional_committed_or_na = strategy_optional_committed_or_na
        self.strategy_reduction_addition_or_as_is = strategy_reduction_addition_or_as_is
        self.strategy_year_of_change_yyyy = strategy_year_of_change_yyyy
        self.strategy_quarter_of_change = strategy_quarter_of_change
        self.strategy_head_count_adjustment_in_year_of_change = strategy_head_count_adjustment_in_year_of_change
        self.strategy_seat_count_adjustment_in_year_of_change = strategy_seat_count_adjustment_in_year_of_change
        self.strategy_square_foot_adjustment_in_year_of_change = strategy_square_foot_adjustment_in_year_of_change
        self.strategy_occupancy_adjustment_in_year_of_change = strategy_occupancy_adjustment_in_year_of_change
        self.strategy_notes = strategy_notes
        self.strategy_top_opportunities = strategy_top_opportunities
        self.user_id = user_id
