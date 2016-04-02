create table click_log(page_name TEXT, section text, rank INT, query text, ip text,
    platform text, browser text, version text, language text,
    referrer text, click_time int);


create table query_log(query text, previous_query text, ip text, platform text, browser text, version text, language text, referrer text,
query_time int);

create table page_visit_log(page_id int, ip text, platform text, browser text, version text, language text, visit_time int);

create table pages(page_id int, page_name text);

insert into pages(page_id, page_name) values(1, 'index.html');
