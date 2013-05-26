CREATE TABLE users (
	userid INTEGER NOT NULL PRIMARY KEY,
	username VARCHAR(64) UNIQUE NOT NULL,
	password VARCHAR(255) NOT NULL,
	signup_ip VARCHAR(64) NOT NULL DEFAULT '',
	signup_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE links (
	linkid INTEGER NOT NULL PRIMARY KEY,
	userid INTEGER NOT NULL,
	name VARCHAR(255) NOT NULL DEFAULT '',
	description TEXT NOT NULL DEFAULT '',
	shortname VARCHAR(255) UNIQUE,
	url TEXT NOT NULL,
	added DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	is_public TINYINT NOT NULL DEFAULT 1
);

CREATE TABLE links_counts (
	linkid INTEGER NOT NULL,
	userid INTEGER NOT NULL,
	hit_count INTEGER NOT NULL DEFAULT 0,
	last_hit DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (linkid, userid)
);

CREATE TABLE links_anonymous_count (
	linkid INTEGER NOT NULL PRIMARY KEY,
	hit_count INTEGER NOT NULL DEFAULT 0,
	last_hit DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE links_hits (
	hitid INTEGER NOT NULL PRIMARY KEY,
	linkid INTEGER NOT NULL,
	userid INTEGER,
	ts DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tags (
    tagid INTEGER NOT NULL PRIMARY KEY,
    tag_name VARCHAR(64) NOT NULL DEFAULT '',
    UNIQUE (tag_name)
);

CREATE TABLE display_tags (
    displayid INTEGER NOT NULL PRIMARY KEY,
    tagid INTEGER NOT NULL,
    display_name VARCHAR(64) NOT NULL DEFAULT '',
    UNIQUE (display_name)
);

CREATE TABLE link_tags (
    linkid INTEGER NOT NULL,
    tagid INTEGER NOT NULL UNIQUE,
    PRIMARY KEY (tagid, linkid)
);

CREATE TABLE link_display_tags (
    linkid INTEGER NOT NULL,
    displayid INTEGER NOT NULL,
    PRIMARY KEY (linkid, displayid)
);

-- Folder structure
CREATE TABLE folders (
    folderid INTEGER NOT NULL PRIMARY KEY,
    userid INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    position INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (userid) REFERENCES users(userid)
);

CREATE TABLE folder_links (
    folderid INTEGER NOT NULL,
    linkid INTEGER NOT NULL,
    PRIMARY KEY (folderid, linkid),
    FOREIGN KEY (folderid) REFERENCES folders(folderid),
    FOREIGN KEY (linkid) REFERENCES links(linkid)
);

CREATE TABLE folder_tree (
    ancestor INTEGER NOT NULL,
    descendant INTEGER NOT NULL,
    item_depth INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (ancestor, descendant),
    FOREIGN KEY (ancestor) REFERENCES folders(folderid),
    FOREIGN KEY (descendant) REFERENCES folders(folderid)
);

