/*
Microsoft SQL Server has some support for Graphs in the database. 
See https://docs.microsoft.com/en-us/sql/relational-databases/graphs/sql-graph-architecture?view=sql-server-ver15
We create two tables here that use that architecture, Nodes and Edges.
We present a few queries using this design, for example querying for shortest paths between nodes.

We also implement support for graph-like queries using more standard SQL.
We add a GEMDEdge table that stores all edges from GEMDContext to itself.
Querying for paths there requires recursive common-table expressions (CTEs).
Those turn out to be much faster and may also have support in other database types.
See e.g. for postgres https://www.postgresql.org/docs/current/queries-with.html#QUERIES-WITH-RECURSIVE
*/
use gemd

-- DROP TABLE Nodes
CREATE TABLE Nodes
( uid varchar(40) not null, gemd_type varchar(32) not null, name varchar(128), context nvarchar(max)) AS NODE

-- drop table Edges
CREATE TABLE Edges 
(gemd_name varchar(32) not null) AS EDGE

--  fill the nodess table
insert into nodes 
select uid,gemd_type,json_value(context,'$.name'),context from GEMDContext

--  fill the edges table
insert into edges 
select n1.$node_id,n2.$node_id, 'material_run:spec'
from nodes n1
join material_run mr on mr.uid=n1.uid
join nodes n2 on n2.uid=mr.spec_uid

insert into edges 
select n1.$node_id,n2.$node_id, 'material_run:process_run'
from nodes n1
join material_run mr on mr.uid=n1.uid
join nodes n2 on n2.uid=mr.process_run_uid

insert into edges 
select n1.$node_id,n2.$node_id, 'material_spec:template'
from nodes n1
join material_spec mr on mr.uid=n1.uid
join nodes n2 on n2.uid=mr.template_uid

insert into edges 
select n1.$node_id,n2.$node_id, 'process_run:spec'
from nodes n1
join process_run mr on mr.uid=n1.uid
join nodes n2 on n2.uid=mr.spec_uid

insert into edges 
select n1.$node_id,n2.$node_id, 'process_spec:template'
from nodes n1
join process_spec mr on mr.uid=n1.uid
join nodes n2 on n2.uid=mr.template_uid

insert into edges 
select n1.$node_id,n2.$node_id, 'measurement_run:spec'
from nodes n1
join measurement_run mr on mr.uid=n1.uid
join nodes n2 on n2.uid=mr.spec_uid

insert into edges 
select n1.$node_id,n2.$node_id, 'measurement_spec:template'
from nodes n1
join measurement_spec mr on mr.uid=n1.uid
join nodes n2 on n2.uid=mr.template_uid

--=========================
-- example query to find shortest paths
-- see https://docs.microsoft.com/en-us/sql/relational-databases/graphs/sql-graph-shortest-path?view=sql-server-ver15
;
with pt as (
select top 1 * 
  from material_run
 order by newid()
), b as (
SELECT n1.uid,STRING_AGG(n2.gemd_type+':'+n2.name, '->') WITHIN GROUP (GRAPH PATH) AS paths
  FROM pt
  ,    nodes n1
  ,    edges FOR PATH AS e
  ,	   nodes FOR PATH AS n2
WHERE n1.uid=pt.uid
  AND MATCH(SHORTEST_PATH(n1(-(e)->n2)+))
) select * from b


--===============================================================================================================
-- building graph using GEMDContext as node and GEMDEdge as edge but relying on recursive CFTs to follow paths
CREATE TABLE GEMDEdge(
  id bigint IDENTITY(1,1)  not null
, from_uid varchar(64) not null
, to_uid varchar(64) not null
, gemd_ref varchar(64) not null
)
--===============================================================================================================
-- building graph using GEMDContext as node and GEMDEdge as edge but relying on recursive CFTs to follow paths
-- drop table gemdedge
CREATE TABLE GEMDEdge(
  id bigint IDENTITY(1,1)  not null
, from_uid varchar(64) not null
, to_uid varchar(64) not null
, gemd_ref varchar(64) not null
)

-- delete from GEMDEdge
-- material_run
insert into GEMDEdge (from_uid,to_uid,gemd_ref)
select uid,spec_uid, 'material_run:spec'
from material_run 
where spec_uid is not null

insert into GEMDEdge 
select uid, process_run_uid, 'material_run:process_run'
from material_run 
where process_run_uid is not null

-- material_spec
insert into GEMDEdge 
select uid,template_uid, 'material_spec:template'
from material_spec
where template_uid is not null

-- process_run
insert into GEMDEdge 
select uid,spec_uid, 'process_run:spec'
from process_run
where spec_uid is not null

-- process_spec
insert into GEMDEdge 
select uid,template_uid, 'process_spec:template'
from process_spec
where template_uid is not null

-- measurement_run
insert into GEMDEdge 
select uid,spec_uid, 'measurement_run:spec'
from measurement_run
where spec_uid is not null

insert into GEMDEdge 
select uid,material_uid, 'measurement_run:material'
from measurement_run
where material_uid is not null

-- measurement_spec
insert into GEMDEdge 
select uid,template_uid, 'measurement_spec:template'
from measurement_spec
where template_uid is not null

insert into GEMDEdge 
select uid,template_uid, 'measurement_spec:template'
from measurement_spec
where template_uid is not null

-- ingredient_spec
insert into GEMDEdge 
select uid,process_spec_uid, 'ingredient_spec:process_spec'
from ingredient_spec
where process_spec_uid is not null

insert into GEMDEdge 
select uid,material_spec_uid, 'ingredient_spec:material_spec'
from ingredient_spec
where material_spec_uid is not null

-- ingredient_run
insert into GEMDEdge 
select uid,material_run_uid, 'ingredient_run:material_run'
from ingredient_run
where material_run_uid is not null

insert into GEMDEdge 
select uid,process_run_uid, 'ingredient_run:process_run'
from ingredient_run
where process_run_uid is not null


--=====

--=====
/*
;
with gr as (
select top 10 e.from_uid as root_uid, 1 as level
,      e.*
,      cast('material_run:'+c.uid+'-->'+e.gemd_ref+':'+e.to_uid as varchar(max)) as [path]
  from material_run c
  join GEMDEdge e on e.from_uid=c.uid
 where c.process_run_uid is not null 
 union all
select gr.root_uid, gr.level+1
,      e.*
,      gr.path+e.from_uid+'-->'+e.gemd_ref+':'+e.to_uid
  from gr
  join GEMDEdge e on e.from_uid=gr.to_uid
where gr.level < 16
)
select root_uid, level, path
  from gr
 order by 1,2
*/

with gr as (
select c.uid as root_uid, 0 as level, cast(NULL as varchar(64)) as endpoint_uid
,      c.uid as from_uid, cast(NULL as bigint) as edge_id, cast(NULL as varchar(64)) as gemd_ref
,      cast('material_run:'+c.uid as varchar(max)) as [path]
  from material_run c
 where c.process_run_uid is not null 
 union all
select gr.root_uid, gr.level+1, e.to_uid
,      e.to_uid, e.id, e.gemd_ref
,      gr.path+'-->'+e.gemd_ref+':'+e.to_uid
  from gr
  join GEMDEdge e on e.from_uid=gr.from_uid
where gr.level < 16
)
select root_uid, endpoint_uid
,      edge_id,gemd_ref
,      path, level
--,      min(path) as path, min(level) as min_level
  from gr
group by root_uid, endpoint_uid having count(*) > 1  -- if you want to find multiple paths between nodes
 order by root_uid, path

 --===============
 -- alternative vs GEMDContext only
-- first count possible multiple paths between two nodes: there are none
with gr as (
select c.uid as root_uid
,      c.gemd_type as root_type
,      0 as level
,      cast(NULL as varchar(64)) as endpoint_uid
,      c.uid as from_uid, cast(NULL as bigint) as edge_id, cast(NULL as varchar(64)) as gemd_ref
,      cast(gemd_type+c.uid as varchar(max)) as [path]
  from GEMDContext c
 union all
select gr.root_uid, gr.root_type, gr.level+1, e.to_uid
,      e.to_uid, e.id, e.gemd_ref
,      gr.path+'-->'+e.gemd_ref+':'+e.to_uid
  from gr
  join GEMDEdge e on e.from_uid=gr.from_uid
where gr.level < 16
)
select root_uid, root_type, endpoint_uid
--,      edge_id,gemd_ref
--,      path, level
,      min(path) as path, min(level) as min_level
  from gr
group by root_type, root_uid, endpoint_uid having count(*) > 1  -- if you want to find multiple paths between nodes
 order by root_type,root_uid, path
;
-- actually retrieve all paths
with gr as (
select c.uid as root_uid
,      c.gemd_type as root_type
,      0 as level
,      cast(NULL as varchar(64)) as endpoint_uid
,      c.uid as from_uid, cast(NULL as bigint) as edge_id, cast(NULL as varchar(64)) as gemd_ref
,      cast(gemd_type+c.uid as varchar(max)) as [path]
  from GEMDContext c
 union all
select gr.root_uid, gr.root_type, gr.level+1, e.to_uid
,      e.to_uid, e.id, e.gemd_ref
,      gr.path+'-->'+e.gemd_ref+':'+e.to_uid
  from gr
  join GEMDEdge e on e.from_uid=gr.from_uid
where gr.level < 16
)
select root_uid, root_type, endpoint_uid
,      edge_id,gemd_ref
,      path, level
  from gr
 order by root_type,root_uid, path

