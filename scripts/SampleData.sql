INSERT INTO roles
    (role, label, description, active)
VALUES
    ('sysadmin', 'System Administrator', 'A user who can administer the application', true),
    ('inuser',   'Internal User',        'A user who is part of the organization',    true),
    ('exuser',   'External User',        'A user who is outside the organization',    true);

INSERT INTO users
    (username, password, firstname, lastname, active)
VALUES
    ('jquest', '$2a$10$yT/xEFvieB6dcsW/hF.fxecJPOmG6q44vnfoCRpoH1KAcLGh0fM7e', 'Johnny', 'Quest', true),
    ('gjetson', '$2a$10$6aJaWFMYghKQtsj7UAEwLujHmwqurh1km39TCQz3iBVC7Dg/B/mN', 'George', 'Jetson', true),
    ('fflintstone', '$2a$10$dHCjMLUR0Cv2bkCKWHAhv..Z/lh7dDMZbJu6edw3.xtjsBAQHAc2O', 'Fred', 'Flintstone', true);

INSERT INTO users_roles_xref
    (userid, roleid)
VALUES
    ((SELECT id FROM users WHERE username='jquest'), (SELECT id from roles WHERE role='sysadmin')),
    ((SELECT id FROM users WHERE username='jquest'), (SELECT id from roles WHERE role='inuser')),
    ((SELECT id FROM users WHERE username='gjetson'), (SELECT id from roles WHERE role='inuser')),
    ((SELECT id FROM users WHERE username='fflintstone'), (SELECT id from roles WHERE role='exuser'));

