INSERT INTO app_role
    (role, label, description, active)
VALUES
    ('sysadmin', 'System Administrator', 'A user who can administer the application', true),
    ('provider', 'Provider', 'A user who provides services to clients', true),
    ('clinician', 'Clinician', 'A user who provides clinical therapy to clients', true),
    ('casemgr', 'Case Manager', 'A user who manages cases', true),
    ('client', 'Client', 'A user who receives services.', true);

INSERT INTO protected_element
    (element)
VALUES
    ('foo'),
    ('bar'),
    ('baz');

INSERT INTO protected_element_role_xref
    (element_id, role_id)
VALUES
    ((SELECT id FROM protected_element WHERE element='foo'), (SELECT id from app_role WHERE role='provider')),
    ((SELECT id FROM protected_element WHERE element='foo'), (SELECT id from app_role WHERE role='clinician')),
    ((SELECT id FROM protected_element WHERE element='bar'), (SELECT id from app_role WHERE role='client'));

INSERT INTO person
    (firstname, lastname, active)
VALUES
    ('Adam', 'Admin', true),
    ('Percy', 'Provider', true),
    ('Carol', 'Clinician', true),
    ('Mike', 'Manager', true),
    ('Clark', 'Client', true);

INSERT INTO app_user
    (username, password, personid, active)
VALUES
    ('adama', '$2a$10$yT/xEFvieB6dcsW/hF.fxecJPOmG6q44vnfoCRpoH1KAcLGh0fM7e', (SELECT id FROM person WHERE firstname='Adam'), true),
    ('percyp', '$2a$10$6aJaWFMYghKQtsj7UAEwLujHmwqurh1km39TCQz3iBVC7Dg/B/mN', (SELECT id FROM person WHERE firstname='Percy'), true),
    ('carolc', '$2a$10$dHCjMLUR0Cv2bkCKWHAhv..Z/lh7dDMZbJu6edw3.xtjsBAQHAc2O', (SELECT id FROM person WHERE firstname='Carol'), true),
    ('mikem', '$2a$10$OMAhgT6lzUqyYNIQOz4VKeBM7iJylAN76rtc/Y4cRi6twIOKoWYu', (SELECT id FROM person WHERE firstname='Mike'), true),
    ('clarkc', '$2a$10$DdwyIaUcfcii6P8K1FJgJuHEvXQym8kuH.K2PrEpLtzT51drXvpLm', (SELECT id FROM person WHERE firstname='Clark'), true);

INSERT INTO app_user_role_xref
    (user_id, role_id)
VALUES
    ((SELECT id FROM app_user WHERE username='adama'), (SELECT id from app_role WHERE role='sysadmin')),
    ((SELECT id FROM app_user WHERE username='percyp'), (SELECT id from app_role WHERE role='provider')),
    ((SELECT id FROM app_user WHERE username='carolc'), (SELECT id from app_role WHERE role='clinician')),
    ((SELECT id FROM app_user WHERE username='mikem'), (SELECT id from app_role WHERE role='casemgr')),
    ((SELECT id FROM app_user WHERE username='mikem'), (SELECT id from app_role WHERE role='provider')),
    ((SELECT id FROM app_user WHERE username='mikem'), (SELECT id from app_role WHERE role='clinician')),
    ((SELECT id FROM app_user WHERE username='clarkc'), (SELECT id from app_role WHERE role='client'));

INSERT INTO session
    (user_id, expires)
VALUES
    ((SELECT id FROM app_user WHERE username='mikem'), now() + interval '10' day);

