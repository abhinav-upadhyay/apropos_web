create table click_log(page_name TEXT, section text, rank INT, query text, ip text,
    platform text, browser text, version text, language text,
    referrer text, click_time int);


create table query_log(query text, previous_query text, ip text, platform text, browser text, version text, language text, referrer text,
query_time int);
