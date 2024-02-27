create database dfx ;


-- orgnisaiton creation 
-- logs in the backend production server

use dfx ;

show tables ;

SET SQL_SAFE_UPDATES = 0;
SET SQL_SAFE_UPDATES = 1;

describe organisation;
select * from organisation;

describe feedbacks;
select * from feedbacks;

describe countries ;
select * from countries;

describe lease_data ;
select * from lease_data;
select * from lease_data where user_id="28";

describe feedbacks;
select * from feedbacks;

describe subscriptions;
select * from subscriptions;

INSERT INTO subscriptions (user_id, subscription_id, start_date, end_date)
VALUES ('99', 'your_random_subscription_id', NOW(), MAKEDATE(YEAR(NOW()) + 1, 1) - INTERVAL 1 DAY);

DELETE FROM subscriptions where user_id=99;


describe user_details ;
select * from user_details ORDER BY created_at DESC;

describe role_permissions;
select * from role_permissions;
delete from role_permissions;

describe user_roles;
select * from user_roles;




delete from user_details where email='reddysainath47@gmail.com';
delete from user_details where email='alice.johnson@example.com';
select * from user_details where email='reddysainath47@gmail.com';
select * from user_details where org_id =1 and role_id = 3;



update user_details 
set org_id =1 , role_id =3
where email = 'reddysainath47@gmail.com';

select * from user_details where email='p.v.sainathreddy@hotmail.com';
select * from user_details where email='parth.ycmou2018@gmail.com';

select * from user_details where email= "p.v.sainathreddy@hotmail.com";
-- user_id : 99

DELETE FROM lease_data WHERE user_id = '28';

select * from lease_data ORDER BY updated_at DESC ; 
SELECT * FROM lease_data WHERE is_deleted = FALSE ORDER BY updated_at DESC;
SELECT * FROM lease_data WHERE user_id= 'deepalsaee1113@gmail.com' ORDER BY updated_at DESC;


CREATE TABLE subscriptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255),
    subscription_id VARCHAR(255) NOT NULL,
    start_date DATETIME,
    end_date DATETIME,
    UNIQUE KEY unique_subscription_id (subscription_id)
);


drop table subscriptions;


CREATE TABLE user_roles (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL
);


drop table user_roles;


ALTER TABLE user_details
ADD COLUMN role_id INT,
ADD CONSTRAINT fk_user_roles
    FOREIGN KEY (role_id)
    REFERENCES user_roles(role_id);
    
    



DELETE FROM user_roles WHERE role_name = 'software_developer';





CREATE TABLE permissions (
    permission_id INT auto_increment  PRIMARY KEY,
    permission_name VARCHAR(50) NOT NULL
);

drop table permissions; 

INSERT INTO permissions (permission_name) VALUES
('create'),
('read'),
('update'),
('delete');

CREATE TABLE role_permissions (
    role_id INT,
    org_id  INT,
    permission_id INT,
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES user_roles(role_id),
    FOREIGN KEY (permission_id) REFERENCES permissions(permission_id)
);

-- Assigning permissions to the 'superadmin' role
INSERT INTO role_permissions (role_id, org_id, permission_id) VALUES
((SELECT role_id FROM user_roles WHERE role_name = 'superadmin'), 1, 1),
((SELECT role_id FROM user_roles WHERE role_name = 'superadmin'), 1, 2),
((SELECT role_id FROM user_roles WHERE role_name = 'superadmin'), 1, 3),
((SELECT role_id FROM user_roles WHERE role_name = 'superadmin'), 1, 4);

-- Assigning permissions to the 'manager' role
INSERT INTO role_permissions (role_id, org_id, permission_id) VALUES
((SELECT role_id FROM user_roles WHERE role_name = 'manager'), 1, 1),
((SELECT role_id FROM user_roles WHERE role_name = 'manager'), 1, 2),
((SELECT role_id FROM user_roles WHERE role_name = 'manager'), 1, 3);

-- Assigning permissions to the 'department_head' role
INSERT INTO role_permissions (role_id, org_id, permission_id) VALUES
((SELECT role_id FROM user_roles WHERE role_name = 'department_head'), 1, 1),
((SELECT role_id FROM user_roles WHERE role_name = 'department_head'), 1, 2);

-- Assigning permissions to the 'executive' role
INSERT INTO role_permissions (role_id, org_id, permission_id) VALUES
((SELECT role_id FROM user_roles WHERE role_name = 'executive'), 1, 1);


drop table role_permissions;

SELECT * FROM role_permissions WHERE role_id =1 AND org_id = 1;

select * from role_permissions;

delete from role_permissions;


ALTER TABLE user_details
DROP COLUMN is_subscribed;



CREATE TABLE user_headcount (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    headcount1 INT DEFAULT 24,
    headcount2 INT DEFAULT 24,
    headcount3 INT DEFAULT 24,
    headcount4 INT DEFAULT 24,
    FOREIGN KEY (user_id) REFERENCES user_details(user_id)
);


INSERT INTO user_headcount (user_id)
VALUES (99);

select * from user_headcount; 

CREATE TABLE role_permissions (
    role_id INT,
    org_id  INT,
    permission_id INT,
    PRIMARY KEY (role_id, org_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES user_roles(role_id),
    FOREIGN KEY (permission_id) REFERENCES permissions(permission_id)
);

INSERT INTO user_headcount (user_id, headcount1, headcount2, headcount3, headcount4)
SELECT user_id, 24, 24, 24, 24
FROM user_details;


CREATE TABLE organisation (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

drop table organisation;


select * from user_details where email= 'superadmin@portfolio.io' ;

UPDATE user_details
SET is_email_verified = TRUE
WHERE email = 'superadmin@portfolio.io';

UPDATE user_details
SET is_deleted = FALSE
WHERE email = 'p.v.sainathreddy@hotmail.com';



ALTER TABLE user_details
ADD COLUMN org_id INT,
ADD COLUMN reports_to INT,
ADD CONSTRAINT fk_org_id FOREIGN KEY (org_id) REFERENCES organisation(id),
ADD CONSTRAINT fk_reports_to FOREIGN KEY (reports_to) REFERENCES user_details(user_id);


INSERT INTO user_details (fullname, email, mobile, password, organisation, is_email_verified, created_at, role_id, org_id, reports_to)
VALUES
    ('Sudhir Admin', 'sudhir@admin.i2e.com', '1234567890', 'password1', 'Admin Organization', TRUE, NOW(), 6, 1, 109 ), -- Admin
    ('Vishal Director', 'vishal@director.i2e.com', '9876543210', 'password2', 'Director Organization', TRUE, NOW(), 6, 1, 110), -- Director
    ('Akshata Project Manager', 'akshata@manager.i2e.com', '5678901234', 'password3', 'Manager Organization', TRUE, NOW(), 2, 1, 111), -- Project Manager
    ('Deepal Developer', 'deepal@developer.i2e.com', '4567890123', 'password4', 'Developer Organization', TRUE, NOW(), 4, 1, 112), -- Developer
    ('Sainath Developer', 'sainath@developer.i2e.com', '7890123456', 'password5', 'Developer Organization', TRUE, NOW(), 4, 1,112 ), -- Developer
    ('Parth Developer', 'parth@developer.i2e.com', '8901234567', 'password6', 'Developer Organization', TRUE, NOW(), 4, 1, 112), -- Developer
    ('Arun Tester', 'arun@tester.i2e.com', '6789012345', 'password7', 'Tester Organization', TRUE, NOW(), 5, 1, 112), -- Tester
    ('Rahul Manager', 'rahul@manager.i2e.com', '1231231234', 'password8', 'Manager Organization 2', TRUE, NOW(), 2, 1,111 ), -- Another Project Manager
    ('Neha Team Lead', 'neha@teamlead.i2e.com', '5675675678', 'password9', 'Team Lead Organization', TRUE, NOW(), 2, 1,117 ), -- Team Lead
    ('Manoj Senior Developer', 'manoj@seniordev.i2e.com', '9879879876', 'password10', 'Senior Developer Organization', TRUE, NOW(), 4, 1,118 ), -- Senior Developer
    ('Priya Senior Developer', 'priya@seniordev.i2e.com', '6546546543', 'password11', 'Senior Developer Organization', TRUE, NOW(), 4, 1,118 ), -- Senior Developer
    ('Sanjay Senior Tester', 'sanjay@seniortester.i2e.com', '8908908901', 'password12', 'Senior Tester Organization', TRUE, NOW(), 4, 1,118 ); -- Senior Tester
    
INSERT INTO user_details (fullname, email, mobile, password, organisation, is_email_verified, created_at, role_id, org_id, reports_to)
VALUES ('Sudhir Admin', 'sudhir@admin.i2e.com', '1234567890', 'password1', 'Admin Organization', TRUE, NOW(), 6, 1, 109);
INSERT INTO user_details (fullname, email, mobile, password, organisation, is_email_verified, created_at, role_id, org_id, reports_to)
VALUES ('Vishal Director', 'vishal@director.i2e.com', '9876543210', 'password2', 'Director Organization', TRUE, NOW(), 6, 1, 134 );
INSERT INTO user_details (fullname, email, mobile, password, organisation, is_email_verified, created_at, role_id, org_id, reports_to)
VALUES ('Akshata Project Manager', 'akshata@manager.i2e.com', '5678901234', 'password3', 'Manager Organization', TRUE, NOW(), 2, 1, 136 );
INSERT INTO user_details (fullname, email, mobile, password, organisation, is_email_verified, created_at, role_id, org_id, reports_to)
VALUES ('Deepal Developer', 'deepal@developer.i2e.com', '4567890123', 'password4', 'Developer Organization', TRUE, NOW(), 4, 1, 150 );
INSERT INTO user_details (fullname, email, mobile, password, organisation, is_email_verified, created_at, role_id, org_id, reports_to)
VALUES ('Sainath Developer', 'sainath@developer.i2e.com', '7890123456', 'password5', 'Developer Organization', TRUE, NOW(), 4, 1, 150);
INSERT INTO user_details (fullname, email, mobile, password, organisation, is_email_verified, created_at, role_id, org_id, reports_to)
VALUES ('Parth Developer', 'parth@developer.i2e.com', '8901234567', 'password6', 'Developer Organization', TRUE, NOW(), 4, 1, 150);
INSERT INTO user_details (fullname, email, mobile, password, organisation, is_email_verified, created_at, role_id, org_id, reports_to)
VALUES ('Arun Tester', 'arun@tester.i2e.com', '6789012345', 'password7', 'Tester Organization', TRUE, NOW(), 5, 1, 150);
INSERT INTO user_details (fullname, email, mobile, password, organisation, is_email_verified, created_at, role_id, org_id, reports_to)
VALUES ('Rahul Manager', 'rahul@manager.i2e.com', '1231231234', 'password8', 'Manager Organization 2', TRUE, NOW(), 2, 1, 136);
INSERT INTO user_details (fullname, email, mobile, password, organisation, is_email_verified, created_at, role_id, org_id, reports_to)
VALUES ('Neha Team Lead', 'neha@teamlead.i2e.com', '5675675678', 'password9', 'Team Lead Organization', TRUE, NOW(), 2, 1, 155 );
INSERT INTO user_details (fullname, email, mobile, password, organisation, is_email_verified, created_at, role_id, org_id, reports_to)
VALUES ('Manoj Senior Developer', 'manoj@seniordev.i2e.com', '9879879876', 'password10', 'Senior Developer Organization', TRUE, NOW(), 4, 1, 156 );
INSERT INTO user_details (fullname, email, mobile, password, organisation, is_email_verified, created_at, role_id, org_id, reports_to)
VALUES ('Priya Senior Developer', 'priya@seniordev.i2e.com', '6546546543', 'password11', 'Senior Developer Organization', TRUE, NOW(), 4, 1, 156);
INSERT INTO user_details (fullname, email, mobile, password, organisation, is_email_verified, created_at, role_id, org_id, reports_to)
VALUES ('Sanjay Senior Tester', 'sanjay@seniortester.i2e.com', '8908908901', 'password12', 'Senior Tester Organization', TRUE, NOW(), 4, 1, 156);

select * from user_details order by created_at desc;

UPDATE user_details
SET role_id = 1
WHERE user_id = 109;


ALTER TABLE user_details 
ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE;

select * from user_details where user_id=99;

ALTER TABLE user_headcount
DROP FOREIGN KEY user_headcount_ibfk_1,
ADD CONSTRAINT user_headcount_ibfk_1
FOREIGN KEY (user_id)
REFERENCES user_details(user_id)
ON DELETE CASCADE;

ALTER TABLE user_headcount
DROP FOREIGN KEY user_headcount_ibfk_1;

ALTER TABLE user_headcount
ADD CONSTRAINT user_headcount_ibfk_1
FOREIGN KEY (user_id)
REFERENCES user_details(user_id)
ON DELETE CASCADE;


DROP TABLE IF EXISTS user_roles;

ALTER TABLE user_details
DROP FOREIGN KEY fk_user_roles;

ALTER TABLE role_permissions
DROP FOREIGN KEY role_permissions_ibfk_1;

CREATE TABLE user_roles (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(255) NOT NULL,
    parent_role_id INT,
    FOREIGN KEY (parent_role_id) REFERENCES user_roles(role_id)
);

drop table roles ;

INSERT INTO roles (role_name, parent_role_id) VALUES
    ('superadmin', NULL),        -- Top-level role
    ('manager', 3),               -- Child of superadmin
    ('department_head', 2),      -- Child of superadmin
    ('software_developer', 4),   -- Child of manager
    ('executive', 4),          -- Top-level role
    ('admin', 1);                 -- Child of executive

-- Insert superadmin role
INSERT INTO user_roles (role_name, parent_role_id) VALUES ('superadmin', NULL);

-- Insert manager role
INSERT INTO user_roles (role_name, parent_role_id) VALUES ('manager', 5);

-- Insert department_head role
INSERT INTO user_roles (role_name, parent_role_id) VALUES ('department_head', 3);

-- Insert software_developer role
INSERT INTO user_roles (role_name, parent_role_id) VALUES ('software_developer', 6);

-- Insert executive role
INSERT INTO user_roles (role_name, parent_role_id) VALUES ('executive', 6);

-- Insert admin role
INSERT INTO user_roles (role_name, parent_role_id) VALUES ('admin', 1);

select * from user_roles;



-- role of sainath as admin 
-- deepal as others
-- same organisation

-- show him the role heirachy , is that a issue for him
-- also the organisaiton , there are already users in it , should i make a new organisaition
select * from user_details where email = 'deepalsaee1113@gmail.com';

UPDATE user_details
SET org_id = 7
WHERE user_id = 99;

select * from user_roles;

select * from organisation; 

INSERT INTO organisation (name) VALUES ('others', 6 );

INSERT INTO user_roles (role_name, parent_role_id) VALUES ('others', 6 );


