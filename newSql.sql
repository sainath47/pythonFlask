create database dfx ;

use dfx ;

show tables ;


describe countries ;
describe lease_data ;
describe otp_data ;
describe feedbacks;

describe subscriptions;
select * from subscriptions;

describe user_details ;
select * from user_details;

SET SQL_SAFE_UPDATES = 0;
SET SQL_SAFE_UPDATES = 1;

delete from user_details where email='reddysainath47@gmail.com';

delete from user_details where email='p.v.sainathreddy@hotmail.com';



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
    
    
    INSERT INTO user_roles (role_name) VALUES
('superadmin'),
('manager'),
('department_head'),
('software_developer'),
('executive');

DELETE FROM user_roles WHERE role_name = 'software_developer';



CREATE TABLE users (
    user_id INT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    role_id INT,
    FOREIGN KEY (role_id) REFERENCES user_roles(role_id)
);

CREATE TABLE permissions (
    permission_id INT auto_increment  PRIMARY KEY,
    permission_name VARCHAR(50) NOT NULL
);

drop table permissions; 

INSERT INTO permissions (permission_name) VALUES
('read'),
('update'),
('create'),
('delete');

CREATE TABLE role_permissions (
    role_id INT,
    org_id  INT,
    permission_id INT,
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES user_roles(role_id),
    FOREIGN KEY (permission_id) REFERENCES permissions(permission_id)
);

drop table role_permissions;




