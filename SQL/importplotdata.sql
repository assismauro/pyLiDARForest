/*

	plots

*/

insert into owner(name)
select distinct dono from rawplot
where not exists(select dono from owner);

insert into county(name)
select distinct municipio from rawplot
where not exists (select distinct name from county);

insert into vegetation(name)
select distinct vegetacao from rawplot
where not exists (select distinct name from vegetation);

insert into tipology(name)
select distinct tipologia from rawplot
where not exists (select distinct name from tipology);

insert into comunity(name)
select distinct comunidade from rawplot
where not exists (select distinct name from comunity);

insert into plot_type(name)
select distinct tipoparcela from rawplot
where not exists (select distinct name from plot_type);

insert into plot_class(name)
select distinct classificacaoparcela from rawplot
where not exists (select distinct name from plot_class);


insert into plots(county_id,vegetation_id,comunity_id,plot_type_id,plot_class_id,owner_id,name,subplot)
--select count (*) from (
select  distinct b.id,c.id,e.id,f.id,g.id,h.id,parcela,subparcela from rawplot a
inner join county b
on a.municipio = b.name
inner join vegetation c
on a.vegetacao = c.name
inner join comunity e
on a.comunidade = e.name
inner join plot_type f
on a.tipoparcela = f.name
inner join plot_class g
on a.classificacaoparcela = g.name
inner join owner h
on a.dono = h.name
--) s

/*

	Measurements

*/

--delete from taxonomy

insert into taxonomy(species,genus,commonname,density,owner_id)
select distinct
case
   when especie = '' THEN NULL
   else especie
end,
case
   when genero = '' THEN NULL
   else genero
end,
case
   when nomecomum = '' THEN NULL
   else nomecomum
end, densidadefinal, b.id
from rawplot a
inner join owner b
on a.dono = b.name

insert into tree_status(name)
select distinct
    case
        when tipo12 is null then 'VIVA'
        else tipo12
    end
from rawplot

select count(*) from measurements
