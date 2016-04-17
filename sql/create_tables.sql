create table if not exists click_log(page_name TEXT, section text, rank INT, query text, ip text,
    platform text, browser text, version text, language text,
    referrer text, click_time int, dist text);


create table if not exists query_log(query text, previous_query text, ip text, platform text, browser text, version text, language text, referrer text,
query_time int, dist text);

create table if not exists page_visit_log(page_id int, ip text, platform text, browser text, version text, language text, visit_time int, dist text);

create table if not exists pages(page_id int primary key, page_name text);

insert into pages(page_id, page_name) values(1, 'index.html');
