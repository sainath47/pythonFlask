"""empty message

Revision ID: 7b944c0e9dd2
Revises: 
Create Date: 2023-11-15 17:27:20.541804

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7b944c0e9dd2'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('countries',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('country', sa.String(length=20), nullable=False),
    sa.Column('emoji', sa.String(length=10), nullable=False),
    sa.Column('unicode', sa.String(length=200), nullable=False),
    sa.Column('image', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('leases',
    sa.Column('lease_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('site_id', sa.String(length=255), nullable=True),
    sa.Column('status', sa.String(length=255), nullable=True),
    sa.Column('document_type', sa.String(length=255), nullable=True),
    sa.Column('building', sa.String(length=255), nullable=True),
    sa.Column('address', sa.String(length=255), nullable=True),
    sa.Column('floor', sa.String(length=255), nullable=True),
    sa.Column('city', sa.String(length=255), nullable=True),
    sa.Column('state_district_province', sa.String(length=255), nullable=True),
    sa.Column('country_code', sa.String(length=10), nullable=True),
    sa.Column('country_name', sa.String(length=255), nullable=True),
    sa.Column('sub_region', sa.String(length=255), nullable=True),
    sa.Column('region', sa.String(length=255), nullable=True),
    sa.Column('postal_code', sa.String(length=20), nullable=True),
    sa.Column('latitude', sa.String(length=20), nullable=True),
    sa.Column('longitude', sa.String(length=20), nullable=True),
    sa.Column('space_use', sa.String(length=255), nullable=True),
    sa.Column('business_unit', sa.String(length=255), nullable=True),
    sa.Column('rentable_sf', sa.String(length=20), nullable=True),
    sa.Column('annualized_base_rent', sa.String(length=20), nullable=True),
    sa.Column('additional_facilities_cost', sa.String(length=20), nullable=True),
    sa.Column('facilities_cost_fully_loaded', sa.String(length=20), nullable=True),
    sa.Column('capacity_seats', sa.String(length=20), nullable=True),
    sa.Column('parking_capacity', sa.String(length=20), nullable=True),
    sa.Column('vacant', sa.String(length=3), nullable=True),
    sa.Column('total_employee_hc', sa.String(length=20), nullable=True),
    sa.Column('total_occupancy_hc', sa.String(length=20), nullable=True),
    sa.Column('surplus_deficit_seat_capacity', sa.String(length=20), nullable=True),
    sa.Column('sf_employee', sa.String(length=20), nullable=True),
    sa.Column('sf_occupant', sa.String(length=20), nullable=True),
    sa.Column('sf_seat', sa.String(length=20), nullable=True),
    sa.Column('cost_sf_1', sa.String(length=20), nullable=True),
    sa.Column('cost_employee', sa.String(length=20), nullable=True),
    sa.Column('cost_occupant', sa.String(length=20), nullable=True),
    sa.Column('cost_seat', sa.String(length=20), nullable=True),
    sa.Column('cost_sf', sa.String(length=20), nullable=True),
    sa.Column('revenues', sa.String(length=20), nullable=True),
    sa.Column('sga', sa.String(length=20), nullable=True),
    sa.Column('opex_total_revenues', sa.String(length=20), nullable=True),
    sa.Column('opex_sga', sa.String(length=20), nullable=True),
    sa.Column('legacy_company', sa.String(length=255), nullable=True),
    sa.Column('verified_yn', sa.String(length=3), nullable=True),
    sa.Column('lease_type', sa.String(length=255), nullable=True),
    sa.Column('leased_owned', sa.String(length=255), nullable=True),
    sa.Column('client_position', sa.String(length=255), nullable=True),
    sa.Column('lease_commencement_date', sa.String(length=20), nullable=True),
    sa.Column('lease_expiration_date', sa.String(length=20), nullable=True),
    sa.Column('lease_expiration_year', sa.String(length=10), nullable=True),
    sa.Column('rmo_months', sa.String(length=20), nullable=True),
    sa.Column('critical_decision_date', sa.String(length=20), nullable=True),
    sa.Column('strategy_type', sa.String(length=255), nullable=True),
    sa.Column('strategy_real_estate_initiative', sa.String(length=255), nullable=True),
    sa.Column('strategy_optional_committed_or_na', sa.String(length=255), nullable=True),
    sa.Column('strategy_reduction_addition_or_as_is', sa.String(length=255), nullable=True),
    sa.Column('strategy_year_of_change_yyyy', sa.String(length=10), nullable=True),
    sa.Column('strategy_quarter_of_change', sa.String(length=5), nullable=True),
    sa.Column('strategy_head_count_adjustment_in_year_of_change', sa.String(length=20), nullable=True),
    sa.Column('strategy_seat_count_adjustment_in_year_of_change', sa.String(length=20), nullable=True),
    sa.Column('strategy_square_foot_adjustment_in_year_of_change', sa.String(length=20), nullable=True),
    sa.Column('strategy_occupancy_adjustment_in_year_of_change', sa.String(length=20), nullable=True),
    sa.Column('strategy_notes', sa.String(length=255), nullable=True),
    sa.Column('strategy_top_opportunities', sa.String(length=255), nullable=True),
    sa.Column('user_id', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('lease_id')
    )
    op.create_table('user',
    sa.Column('user_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('fullname', sa.String(length=500), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('mobile', sa.String(length=45), nullable=True),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('organisation', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('user_id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('otps',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('otp', sa.String(length=10), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('otps')
    op.drop_table('user')
    op.drop_table('leases')
    op.drop_table('countries')
    # ### end Alembic commands ###
