CREATE SEQUENCE public.plots_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 1;

CREATE SEQUENCE public.measurements_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 1;

CREATE SEQUENCE public.taxonomy_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 1;

CREATE SEQUENCE public.county_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 1;

CREATE SEQUENCE public.vegetation_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 1;

CREATE SEQUENCE public.tipology_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 1;

CREATE SEQUENCE public.comunity_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 1;

CREATE SEQUENCE public.plot_type_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 1;

CREATE SEQUENCE public.plot_class_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 1;

CREATE SEQUENCE public.tree_status_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 1;

CREATE SEQUENCE public.owner_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 1;

CREATE TABLE public.plots (
id integer NOT NULL DEFAULT nextval('plots_id_seq'::regclass),
    county_id integer NOT NULL,
    vegetation_id integer NOT NULL,
    tipology_id integer NOT NULL,
    comunity_id integer NOT NULL,
    plot_type_id integer NOT NULL,
    plot_class_id integer NOT NULL,
    owner_id integer NOT NULL,
    name varchar(50) NOT NULL,
    subplot varchar(50),
    PRIMARY KEY (id)
);

CREATE INDEX ON public.plots
    (county_id);
CREATE INDEX ON public.plots
    (vegetation_id);
CREATE INDEX ON public.plots
    (tipology_id);
CREATE INDEX ON public.plots
    (comunity_id);
CREATE INDEX ON public.plots
    (plot_type_id);
CREATE INDEX ON public.plots
    (owner_id);


CREATE TABLE public.measurements (
id integer NOT NULL DEFAULT nextval('measurements_id_seq'::regclass),
    plot_id integer NOT NULL,
    date date NOT NULL,
    side char(1) NOT NULL,
    subplot boolean NOT NULL,
    tree_number integer,
    taxonomy_id integer NOT NULL,
    dap real NOT NULL,
    tree_tatus_id integer NOT NULL,
    gps varchar(50),
    agb real NOT NULL,
    observation varchar(50),
    PRIMARY KEY (id)
);

CREATE INDEX ON public.measurements
    (plot_id);
CREATE INDEX ON public.measurements
    (taxonomy_id);
CREATE INDEX ON public.measurements
    (tree_tatus_id);


CREATE TABLE public.taxonomy (
id integer NOT NULL DEFAULT nextval('taxonomy_id_seq'::regclass),
    name varchar(50) NOT NULL,
    authority varchar(50) NOT NULL,
    species varchar(50) NOT NULL,
    genus varchar(50) NOT NULL,
    commonname varchar(50) NOT NULL,
    PRIMARY KEY (id)
);


CREATE TABLE public.county (
id integer NOT NULL DEFAULT nextval('county_id_seq'::regclass),
    name varchar(50) NOT NULL,
    state varchar(2),
    PRIMARY KEY (id)
);

ALTER TABLE public.county
    ADD UNIQUE (name);


CREATE TABLE public.vegetation (
id integer NOT NULL DEFAULT nextval('vegetation_id_seq'::regclass),
    name varchar(50) NOT NULL,
    PRIMARY KEY (id)
);

ALTER TABLE public.vegetation
    ADD UNIQUE (name);


CREATE TABLE public.tipology (
id integer NOT NULL DEFAULT nextval('tipology_id_seq'::regclass),
    name varchar(50) NOT NULL,
    PRIMARY KEY (id)
);

ALTER TABLE public.tipology
    ADD UNIQUE (name);


CREATE TABLE public.comunity (
id integer NOT NULL DEFAULT nextval('comunity_id_seq'::regclass),
    name varchar(50) NOT NULL,
    PRIMARY KEY (id)
);

ALTER TABLE public.comunity
    ADD UNIQUE (name);


CREATE TABLE public.plot_type (
id integer NOT NULL DEFAULT nextval('plot_type_id_seq'::regclass),
    name varchar(50) NOT NULL,
    PRIMARY KEY (id)
);

ALTER TABLE public.plot_type
    ADD UNIQUE (name);


CREATE TABLE public.plot_class (
id integer NOT NULL DEFAULT nextval('plot_class_id_seq'::regclass),
    name varchar(59) NOT NULL,
    PRIMARY KEY (id)
);

ALTER TABLE public.plot_class
    ADD UNIQUE (name);


CREATE TABLE public.tree_status (
id integer NOT NULL DEFAULT nextval('tree_status_id_seq'::regclass),
    name varchar(50) NOT NULL,
    descripion varchar(50),
    PRIMARY KEY (id)
);


CREATE TABLE public.owner (
id integer NOT NULL DEFAULT nextval('owner_id_seq'::regclass),
    name varchar(50) NOT NULL,
    PRIMARY KEY (id)
);


ALTER TABLE public.plots ADD CONSTRAINT FK_plots__county_id FOREIGN KEY (county_id) REFERENCES public.county(id);
ALTER TABLE public.plots ADD CONSTRAINT FK_plots__vegetation_id FOREIGN KEY (vegetation_id) REFERENCES public.vegetation(id);
ALTER TABLE public.plots ADD CONSTRAINT FK_plots__tipology_id FOREIGN KEY (tipology_id) REFERENCES public.tipology(id);
ALTER TABLE public.plots ADD CONSTRAINT FK_plots__comunity_id FOREIGN KEY (comunity_id) REFERENCES public.comunity(id);
ALTER TABLE public.plots ADD CONSTRAINT FK_plots__plot_type_id FOREIGN KEY (plot_type_id) REFERENCES public.plot_type(id);
ALTER TABLE public.plots ADD CONSTRAINT FK_plots__plot_class_id FOREIGN KEY (plot_class_id) REFERENCES public.plot_class(id);
ALTER TABLE public.plots ADD CONSTRAINT FK_plots__owner_id FOREIGN KEY (owner_id) REFERENCES public.owner(id);
ALTER TABLE public.measurements ADD CONSTRAINT FK_measurements__plot_id FOREIGN KEY (plot_id) REFERENCES public.plots(id);
ALTER TABLE public.measurements ADD CONSTRAINT FK_measurements__taxonomy_id FOREIGN KEY (taxonomy_id) REFERENCES public.taxonomy(id);
ALTER TABLE public.measurements ADD CONSTRAINT FK_measurements__tree_tatus_id FOREIGN KEY (tree_tatus_id) REFERENCES public.tree_status(id);
ALTER TABLE public.plots ADD CONSTRAINT UK_plots UNIQUE (name,subplot);