# app/controllers/country_controller.py

from flask import request, jsonify
from app.models.lease_model import Lease
from app import db




def create_lease():
    try:
        data = request.get_json()

        # Extract data from the request JSON
        site_id = data.get('site_id')
        status = data.get('status')
        document_type = data.get('document_type')
        building = data.get('building')
        address = data.get('address')
        floor = data.get('floor')
        city = data.get('city')
        state_district_province = data.get('state_district_province')
        country_code = data.get('country_code')
        country_name = data.get('country_name')
        sub_region = data.get('sub_region')
        region = data.get('region')
        postal_code = data.get('postal_code')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        space_use = data.get('space_use')
        business_unit = data.get('business_unit')
        rentable_sf = data.get('rentable_sf')
        annualized_base_rent = data.get('annualized_base_rent')
        additional_facilities_cost = data.get('additional_facilities_cost')
        facilities_cost_fully_loaded = data.get('facilities_cost_fully_loaded')
        capacity_seats = data.get('capacity_seats')
        parking_capacity = data.get('parking_capacity')
        vacant = data.get('vacant')
        total_employee_hc = data.get('total_employee_hc')
        total_occupancy_hc = data.get('total_occupancy_hc')
        surplus_deficit_seat_capacity = data.get('surplus_deficit_seat_capacity')
        sf_employee = data.get('sf_employee')
        sf_occupant = data.get('sf_occupant')
        sf_seat = data.get('sf_seat')
        cost_sf_1 = data.get('cost_sf_1')
        cost_employee = data.get('cost_employee')
        cost_occupant = data.get('cost_occupant')
        cost_seat = data.get('cost_seat')
        cost_sf = data.get('cost_sf')
        revenues = data.get('revenues')
        sga = data.get('sga')
        opex_total_revenues = data.get('opex_total_revenues')
        opex_sga = data.get('opex_sga')
        legacy_company = data.get('legacy_company')
        verified_yn = data.get('verified_yn')
        lease_type = data.get('lease_type')
        leased_owned = data.get('leased_owned')
        client_position = data.get('client_position')
        lease_commencement_date = data.get('lease_commencement_date')
        lease_expiration_date = data.get('lease_expiration_date')
        lease_expiration_year = data.get('lease_expiration_year')
        rmo_months = data.get('rmo_months')
        critical_decision_date = data.get('critical_decision_date')
        strategy_type = data.get('strategy_type')
        strategy_real_estate_initiative = data.get('strategy_real_estate_initiative')
        strategy_optional_committed_or_na = data.get('strategy_optional_committed_or_na')
        strategy_reduction_addition_or_as_is = data.get('strategy_reduction_addition_or_as_is')
        strategy_year_of_change_yyyy = data.get('strategy_year_of_change_yyyy')
        strategy_quarter_of_change = data.get('strategy_quarter_of_change')
        strategy_head_count_adjustment_in_year_of_change = data.get('strategy_head_count_adjustment_in_year_of_change')
        strategy_seat_count_adjustment_in_year_of_change = data.get('strategy_seat_count_adjustment_in_year_of_change')
        strategy_square_foot_adjustment_in_year_of_change = data.get('strategy_square_foot_adjustment_in_year_of_change')
        strategy_occupancy_adjustment_in_year_of_change = data.get('strategy_occupancy_adjustment_in_year_of_change')
        strategy_notes = data.get('strategy_notes')
        strategy_top_opportunities = data.get('strategy_top_opportunities')
        user_id = data.get('user_id')

        # Create a new Lease instance
        new_lease = Lease(

            site_id=site_id,
            status=status,
            document_type=document_type,
            building=building,
            address=address,
            floor=floor,
            city=city,
            state_district_province=state_district_province,
            country_code=country_code,
            country_name=country_name,
            sub_region=sub_region,
            region=region,
            postal_code=postal_code,
            latitude=latitude,
            longitude=longitude,
            space_use=space_use,
            business_unit=business_unit,
            rentable_sf=rentable_sf,
            annualized_base_rent=annualized_base_rent,
            additional_facilities_cost=additional_facilities_cost,
            facilities_cost_fully_loaded=facilities_cost_fully_loaded,
            capacity_seats=capacity_seats,
            parking_capacity=parking_capacity,
            vacant=vacant,
            total_employee_hc=total_employee_hc,
            total_occupancy_hc=total_occupancy_hc,
            surplus_deficit_seat_capacity=surplus_deficit_seat_capacity,
            sf_employee=sf_employee,
            sf_occupant=sf_occupant,
            sf_seat=sf_seat,
            cost_sf_1=cost_sf_1,
            cost_employee=cost_employee,
            cost_occupant=cost_occupant,
            cost_seat=cost_seat,
            cost_sf=cost_sf,
            revenues=revenues,
            sga=sga,
            opex_total_revenues=opex_total_revenues,
            opex_sga=opex_sga,
            legacy_company=legacy_company,
            verified_yn=verified_yn,
            lease_type=lease_type,
            leased_owned=leased_owned,
            client_position=client_position,
            lease_commencement_date=lease_commencement_date,
            lease_expiration_date=lease_expiration_date,
            lease_expiration_year=lease_expiration_year,
            rmo_months=rmo_months,
            critical_decision_date=critical_decision_date,
            strategy_type=strategy_type,
            strategy_real_estate_initiative=strategy_real_estate_initiative,
            strategy_optional_committed_or_na=strategy_optional_committed_or_na,
            strategy_reduction_addition_or_as_is=strategy_reduction_addition_or_as_is,
            strategy_year_of_change_yyyy=strategy_year_of_change_yyyy,
            strategy_quarter_of_change=strategy_quarter_of_change,
            strategy_head_count_adjustment_in_year_of_change=strategy_head_count_adjustment_in_year_of_change,
            strategy_seat_count_adjustment_in_year_of_change=strategy_seat_count_adjustment_in_year_of_change,
            strategy_square_foot_adjustment_in_year_of_change=strategy_square_foot_adjustment_in_year_of_change,
            strategy_occupancy_adjustment_in_year_of_change=strategy_occupancy_adjustment_in_year_of_change,
            strategy_notes=strategy_notes,
            strategy_top_opportunities=strategy_top_opportunities,
            user_id=user_id
        )

        # Add the new lease to the database
        db.session.add(new_lease)
        db.session.commit()

        response = {
            'status': 201,
            'message': 'Lease created successfully',
            'data': new_lease.to_dict()  # Assuming you have a to_dict method in your Lease model
        }

        return jsonify(response),201

    except Exception as e:
        return jsonify({'error': str(e)}), 500



def read_leases_by_user_id(user_id):
    try:
        leases = Lease.query.filter_by(user_id=user_id, is_deleted=False).order_by(Lease.updated_at.desc())

        if leases:
            lease_list = [lease.to_dict() for lease in leases]

            # Fetch the latest updated_at value
         
            latest_updated_at = lease_list[0].get('updated_at')

            response = {
                'status': 200,
                'message': 'Leases retrieved successfully',
                'data': lease_list,
                'latest_updated_at': latest_updated_at
                
            }
        else:
            response = {
                'status': 404,
                'message': 'No leases found for the user'
            }

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500



def update_lease(lease_id):
    try:
        # Get the existing lease from the database
        existing_lease = Lease.query.get(lease_id)

        if not existing_lease:
            return jsonify({'status': 404, 'message': 'Lease not found'}), 404

        # Extract data from the request JSON
        data = request.get_json()

        # Update fields based on the request data
        existing_lease.site_id = data.get('site_id', existing_lease.site_id)
        existing_lease.status = data.get('status', existing_lease.status)
        existing_lease.document_type = data.get('document_type', existing_lease.document_type)
        existing_lease.building = data.get('building', existing_lease.building)
        existing_lease.address = data.get('address', existing_lease.address)
        existing_lease.floor = data.get('floor', existing_lease.floor)
        existing_lease.city = data.get('city', existing_lease.city)
        existing_lease.state_district_province = data.get('state_district_province', existing_lease.state_district_province)
        existing_lease.country_code = data.get('country_code', existing_lease.country_code)
        existing_lease.country_name = data.get('country_name', existing_lease.country_name)
        existing_lease.sub_region = data.get('sub_region', existing_lease.sub_region)
        existing_lease.region = data.get('region', existing_lease.region)
        existing_lease.postal_code = data.get('postal_code', existing_lease.postal_code)
        existing_lease.latitude = data.get('latitude', existing_lease.latitude)
        existing_lease.longitude = data.get('longitude', existing_lease.longitude)
        existing_lease.space_use = data.get('space_use', existing_lease.space_use)
        existing_lease.business_unit = data.get('business_unit', existing_lease.business_unit)
        existing_lease.rentable_sf = data.get('rentable_sf', existing_lease.rentable_sf)
        existing_lease.annualized_base_rent = data.get('annualized_base_rent', existing_lease.annualized_base_rent)
        existing_lease.additional_facilities_cost = data.get('additional_facilities_cost', existing_lease.additional_facilities_cost)
        existing_lease.facilities_cost_fully_loaded = data.get('facilities_cost_fully_loaded', existing_lease.facilities_cost_fully_loaded)
        existing_lease.capacity_seats = data.get('capacity_seats', existing_lease.capacity_seats)
        existing_lease.parking_capacity = data.get('parking_capacity', existing_lease.parking_capacity)
        existing_lease.vacant = data.get('vacant', existing_lease.vacant)
        existing_lease.total_employee_hc = data.get('total_employee_hc', existing_lease.total_employee_hc)
        existing_lease.total_occupancy_hc = data.get('total_occupancy_hc', existing_lease.total_occupancy_hc)
        existing_lease.surplus_deficit_seat_capacity = data.get('surplus_deficit_seat_capacity', existing_lease.surplus_deficit_seat_capacity)
        existing_lease.sf_employee = data.get('sf_employee', existing_lease.sf_employee)
        existing_lease.sf_occupant = data.get('sf_occupant', existing_lease.sf_occupant)
        existing_lease.sf_seat = data.get('sf_seat', existing_lease.sf_seat)
        existing_lease.cost_sf_1 = data.get('cost_sf_1', existing_lease.cost_sf_1)
        existing_lease.cost_employee = data.get('cost_employee', existing_lease.cost_employee)
        existing_lease.cost_occupant = data.get('cost_occupant', existing_lease.cost_occupant)
        existing_lease.cost_seat = data.get('cost_seat', existing_lease.cost_seat)
        existing_lease.cost_sf = data.get('cost_sf', existing_lease.cost_sf)
        existing_lease.revenues = data.get('revenues', existing_lease.revenues)
        existing_lease.sga = data.get('sga', existing_lease.sga)
        existing_lease.opex_total_revenues = data.get('opex_total_revenues', existing_lease.opex_total_revenues)
        existing_lease.opex_sga = data.get('opex_sga', existing_lease.opex_sga)
        existing_lease.legacy_company = data.get('legacy_company', existing_lease.legacy_company)
        existing_lease.verified_yn = data.get('verified_yn', existing_lease.verified_yn)
        existing_lease.lease_type = data.get('lease_type', existing_lease.lease_type)
        existing_lease.leased_owned = data.get('leased_owned', existing_lease.leased_owned)
        existing_lease.client_position = data.get('client_position', existing_lease.client_position)
        existing_lease.lease_commencement_date = data.get('lease_commencement_date', existing_lease.lease_commencement_date)
        existing_lease.lease_expiration_date = data.get('lease_expiration_date', existing_lease.lease_expiration_date)
        existing_lease.lease_expiration_year = data.get('lease_expiration_year', existing_lease.lease_expiration_year)
        existing_lease.rmo_months = data.get('rmo_months', existing_lease.rmo_months)
        existing_lease.critical_decision_date = data.get('critical_decision_date', existing_lease.critical_decision_date)
        existing_lease.strategy_type = data.get('strategy_type', existing_lease.strategy_type)
        existing_lease.strategy_real_estate_initiative = data.get('strategy_real_estate_initiative', existing_lease.strategy_real_estate_initiative)
        existing_lease.strategy_optional_committed_or_na = data.get('strategy_optional_committed_or_na', existing_lease.strategy_optional_committed_or_na)
        existing_lease.strategy_reduction_addition_or_as_is = data.get('strategy_reduction_addition_or_as_is', existing_lease.strategy_reduction_addition_or_as_is)
        existing_lease.strategy_year_of_change_yyyy = data.get('strategy_year_of_change_yyyy', existing_lease.strategy_year_of_change_yyyy)
        existing_lease.strategy_quarter_of_change = data.get('strategy_quarter_of_change', existing_lease.strategy_quarter_of_change)
        existing_lease.strategy_head_count_adjustment_in_year_of_change = data.get('strategy_head_count_adjustment_in_year_of_change', existing_lease.strategy_head_count_adjustment_in_year_of_change)
        existing_lease.strategy_seat_count_adjustment_in_year_of_change = data.get('strategy_seat_count_adjustment_in_year_of_change', existing_lease.strategy_seat_count_adjustment_in_year_of_change)
        existing_lease.strategy_square_foot_adjustment_in_year_of_change = data.get('strategy_square_foot_adjustment_in_year_of_change', existing_lease.strategy_square_foot_adjustment_in_year_of_change)
        existing_lease.strategy_occupancy_adjustment_in_year_of_change = data.get('strategy_occupancy_adjustment_in_year_of_change', existing_lease.strategy_occupancy_adjustment_in_year_of_change)
        existing_lease.strategy_notes = data.get('strategy_notes', existing_lease.strategy_notes)
        existing_lease.strategy_top_opportunities = data.get('strategy_top_opportunities', existing_lease.strategy_top_opportunities)
        existing_lease.user_id = data.get('user_id', existing_lease.user_id)

        # Commit the changes to the database
        db.session.commit()

        response = {
            'status': 200,
            'message': 'Lease updated successfully',
            'data': existing_lease.to_dict()  # Assuming you have a to_dict method in your Lease model
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500



def delete_lease(lease_id):
    try:
        # Get the existing lease from the database
        existing_lease = Lease.query.get(lease_id)

        if not existing_lease:
            return jsonify({'status': 404, 'message': 'Lease not found'}), 404

        # Set the is_deleted field to True
        existing_lease.is_deleted = True

        # Commit the changes to the database
        db.session.commit()

        response = {
            'status': 200,
            'message': 'Lease deleted successfully',
            'data': existing_lease.to_dict()  # Assuming you have a to_dict method in your Lease model
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
