
-- drop table GEMDObject
  create table GEMDObject (
  uid varchar(64) not null
  , scope varchar(32) not null
  , gemd_type varchar(32) not null
)
alter table GEMDObject add constraint pk_GEMDObject primary key(uid)


-- drop table GEMDContext 
create table GEMDContext (
  uid varchar(64) not null
  , gemd_type varchar(32) not null
  , context varchar(max) not null
  )
alter table GEMDContext add constraint pk_GEMDContext primary key(uid)

select count(*) from gemdcontext
select count(*) from gemdobject

select distinct gemd_type from gemdobject
select distinct gemd_type from gemdcontext order by 1


