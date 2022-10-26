alter table material_run add constraint pk_material_run primary key(uid)
alter table material_spec add constraint pk_material_spec primary key(uid)
alter table material_template add constraint pk_material_template primary key(uid)
alter table process_run add constraint pk_process_run primary key(uid)
alter table process_spec add constraint pk_process_spec primary key(uid)
alter table process_template add constraint pk_process_template primary key(uid)
alter table measurement_run add constraint pk_measurement_run primary key(uid)
alter table measurement_spec add constraint pk_measurement_spec primary key(uid)
alter table measurement_template add constraint pk_measurement_template primary key(uid)


 create index ix_nodes_uid on nodes(uid)
