CREATE TABLE users (
	userid INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
	username VARCHAR(64) UNIQUE NOT NULL,
	password VARCHAR(255) NOT NULL,
	signup_ip VARCHAR(64) NOT NULL DEFAULT '',
	signup_date DATETIME NOT NULL
) Engine=InnoDB;

CREATE TABLE links (
	linkid INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
	userid INTEGER NOT NULL,
	name VARCHAR(255) NOT NULL DEFAULT '',
	description TEXT NOT NULL DEFAULT '',
	shortname VARCHAR(255) UNIQUE,
	url TEXT NOT NULL,
	added DATETIME NOT NULL,
	is_public TINYINT NOT NULL DEFAULT 1,
    FOREIGN KEY (userid) REFERENCES users(userid)
) Engine=InnoDB;

CREATE TABLE links_counts (
	linkid INTEGER NOT NULL,
	userid INTEGER NOT NULL,
	hit_count INTEGER NOT NULL DEFAULT 0,
	last_hit TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (linkid, userid),
    FOREIGN KEY (linkid) REFERENCES links(linkid) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (userid) REFERENCES users(userid) ON DELETE CASCADE ON UPDATE CASCADE
) Engine=InnoDB;

CREATE TABLE links_anonymous_count (
	linkid INTEGER NOT NULL PRIMARY KEY,
	hit_count INTEGER NOT NULL DEFAULT 0,
	last_hit TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (linkid) REFERENCES links(linkid) ON DELETE CASCADE ON UPDATE CASCADE
) Engine=InnoDB;

CREATE TABLE links_hits (
	hitid INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
	linkid INTEGER NOT NULL,
	userid INTEGER,
	ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (linkid) REFERENCES links(linkid) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (userid) REFERENCES users(userid) ON DELETE CASCADE ON UPDATE CASCADE
) Engine=InnoDB;

CREATE TABLE tags (
    tagid INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
    tag_name VARCHAR(64) NOT NULL DEFAULT '',
    UNIQUE (tag_name)
) Engine=InnoDB;

CREATE TABLE display_tags (
    displayid INTEGER NOT NULL PRIMARY KEY,
    tagid INTEGER NOT NULL,
    display_name VARCHAR(64) NOT NULL DEFAULT '',
    UNIQUE (display_name)
) Engine=InnoDB;

CREATE TABLE link_tags (
    linkid INTEGER NOT NULL,
    tagid INTEGER NOT NULL,
    PRIMARY KEY (tagid, linkid),
    FOREIGN KEY (linkid) REFERENCES links(linkid) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (tagid) REFERENCES tags(tagid) ON DELETE CASCADE ON UPDATE CASCADE
) Engine=InnoDB;

CREATE TABLE link_display_tags (
    linkid INTEGER NOT NULL,
    displayid INTEGER NOT NULL,
    PRIMARY KEY (linkid, displayid),
    FOREIGN KEY (linkid) REFERENCES links(linkid) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (displayid) REFERENCES display_tags(displayid) ON DELETE CASCADE ON UPDATE CASCADE
) Engine=InnoDB;

-- Folder structure
CREATE TABLE folders (
    folderid INTEGER NOT NULL PRIMARY KEY,
    userid INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    added DATETIME NOT NULL,
    is_public TINYINT NOT NULL DEFAULT 1,
    FOREIGN KEY (userid) REFERENCES users(userid)
) Engine=InnoDB;

CREATE TABLE folder_links (
    folderid INTEGER NOT NULL,
    linkid INTEGER NOT NULL,
    PRIMARY KEY (folderid, linkid),
    FOREIGN KEY (folderid) REFERENCES folders(folderid),
    FOREIGN KEY (linkid) REFERENCES links(linkid)
) Engine=InnoDB;

-- Dashboard modules
CREATE TABLE dashboard_modules (
    moduleid INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
    userid INTEGER NOT NULL,
    module_type INTEGER NOT NULL DEFAULT 1,
    position INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (userid) REFERENCES users(userid) ON DELETE CASCADE ON UPDATE CASCADE
) Engine=InnoDB;

CREATE TABLE dashboard_modules_config_tag (
    moduleid INTEGER NOT NULL PRIMARY KEY,
    tag_name VARCHAR(64) NOT NULL,
    FOREIGN KEY (moduleid) REFERENCES dashboard_modules(moduleid) ON DELETE CASCADE ON UPDATE CASCADE
) Engine=InnoDB;