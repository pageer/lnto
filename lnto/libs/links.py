import urllib
from datetime import datetime
from bs4 import BeautifulSoup # pylint: disable=import-error
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql.expression import or_
from sqlalchemy import ForeignKey, Column, Integer, String, DateTime, Boolean, Text
from lnto import appdb
from lnto.libs.tags import Tag, link_tags

def search(terms):
    results = appdb.session \
            .query(Link) \
            .filter(or_(Link.name.like(terms), Link.url.like(terms))) \
            .all()
    return results

class Link(appdb.Model): # pylint: disable=too-many-public-methods,too-many-instance-attributes
    __tablename__ = 'links'

    linkid = Column(Integer, primary_key=True)
    userid = Column(Integer, ForeignKey('users.userid'))
    name = Column(String(256))
    url = Column(Text(convert_unicode=True))
    description = Column(Text(convert_unicode=True), default='')
    shortname = Column(String(256))
    added = Column(DateTime, default=datetime.now())
    is_public = Column(Boolean, default=True)

    owner = relationship('User', backref=backref('links', order_by=linkid))
    #display_tags = relationship('DisplayTag', secondary = link_display_tags, backref = 'links')
    tags = relationship('Tag', secondary=link_tags)

    count = None

    def __init__(self, row=None):
        if row is not None:
            self.name = row['name'] if row.get('name') else ''
            self.url = row['url'] if row.get('url') else ''
            self.description = row['description'] if row.get('description') else ''
            self.shortname = row['shortname'] if row.get('shortname') else None
            self.added = row['added'] if row.get('added') else datetime.now()
            self.is_public = bool(row['is_public']) if row.get('is_public') is not None else True
            self.userid = row['userid'] if row.get('userid') else 0
            self.linkid = row['linkid'] if row.get('linkid') else None
            if row.get('tags'):
                self.set_tags(row.get('tags').split(','))


    def get_taglist(self):
        ret = []
        for tag in self.tags:
            ret.append(str(tag))
        return ret


    def set_tags(self, taglist):
        while self.tags:
            del self.tags[0]

        for tag in taglist:
            self.add_tag(tag)


    def add_tag(self, tagname):
        tagname = tagname.strip()
        for tag in self.tags:
            if str(tag) == tagname:
                return

        tag = Tag.get_by_name(tagname)
        if not tag:
            tag = Tag(tagname)
        self.tags.append(tag)


    def remove_tag(self, tagname):
        tagname = tagname.strip()
        for tag in self.tags:
            if str(tag) == tagname:
                self.tags.remove(tag)
                return


    def save(self):
        if self.shortname == '':
            self.shortname = None
        appdb.session.add(self)
        appdb.session.commit()


    def delete(self):
        appdb.session.delete(self)
        appdb.session.commit()


    def get_count(self, user=None):
        if self.count is None:
            uid = self.userid if user is None else user.userid
            cnt = LinkCount.get_by({'userid': uid, 'linkid': self.linkid}) # pylint: disable=no-member
            self.count = cnt[0] if cnt else None
            if self.count is None:
                self.count = LinkCount({'userid': self.userid, 'linkid': self.linkid})
                self.count.insert()
        return self.count


    def get_hit(self, user=None):
        data = {'linkid': self.linkid}
        if user is not None:
            data['userid'] = user.userid
        return LinkHit(data)


    def is_owner(self, user):
        if not user:
            return False
        return self.userid == user.userid


    def serializable(self):
        return {
            'linkid': self.linkid,
            'userid': self.userid,
            'name': self.name,
            'url': self.url,
            'description': self.description,
            'shortname': self.shortname,
            'added': self.added.strftime('%Y-%m-%d %I:%m %p'),
            'is_public': self.is_public,
            'tags': self.get_taglist()
        }

    def already_exists(self):
        ret = appdb.session.query(Link) \
                .filter(Link.url == self.url, Link.userid == self.userid).first()
        if ret:
            self.linkid = ret.linkid
            return True
        return False

    @staticmethod
    def get_by_id(link_id):
        if isinstance(link_id, list):
            return appdb.session.query(Link).filter(Link.linkid.in_(link_id)).all()
        return appdb.session.query(Link).filter_by(linkid=link_id).first()

    @staticmethod
    def get_by_user(userid):
        return appdb.session.query(Link).filter_by(userid=userid).all()

    @staticmethod
    def get_public_by_user(userid):
        return appdb.session.query(Link).filter_by(userid=userid, is_public=True).all()

    @staticmethod
    def get_by_shortname(name):
        return appdb.session.query(Link).filter_by(shortname=name).first()

    @staticmethod
    def get_by_tag(tag, userid=None):
        if userid is None:
            return appdb.session.query(Link).filter(Link.tags.any(Tag.tag_name == tag)).all()
        return appdb.session.query(Link) \
                .filter_by(userid=userid).filter(Link.tags.any(Tag.tag_name == tag)) \
                .all()

    @staticmethod
    def get_public_by_tag(tag, userid=None):
        if userid is None:
            return appdb.session.query(Link) \
                    .filter(Link.is_public, Link.tags.any(Tag.tag_name == tag)) \
                    .all()
        return appdb.session.query(Link) \
                .filter(Link.userid == userid, Link.is_public, Link.tags.any(Tag.tag_name == tag)) \
                .all()

    @staticmethod
    def get_recent_public_by_tag(tags, userid=None, limit=10):
        if userid is None:
            return appdb.session.query(Link) \
                    .filter(Link.is_public, Link.tags.any(Tag.tag_name.in_(tags))) \
                    .order_by(Link.added.desc()).limit(limit) \
                    .all()
        return appdb.session.query(Link) \
                .filter(Link.userid == userid, Link.is_public) \
                .filter(Link.tags.any(Tag.tag_name.in_(tags))) \
                .order_by(Link.added.desc()).limit(limit) \
                .all()

    @staticmethod
    def get_recent_by_tag(tags, userid=None, limit=10):
        if userid is None:
            return appdb.session.query(Link) \
                    .filter(Link.tags.any(Tag.tag_name.in_(tags))) \
                    .order_by(Link.added.desc()) \
                    .limit(limit) \
                    .all()
        return appdb.session.query(Link) \
                .filter_by(userid=userid) \
                .filter(Link.tags.any(Tag.tag_name.in_(tags))) \
                .order_by(Link.added.desc()) \
                .limit(limit) \
                .all()

    @staticmethod
    def get_untagged(userid=None):
        if userid is None:
            return appdb.session.query(Link).filter(~Link.tags.any()).all()
        return appdb.session.query(Link).filter(~Link.tags.any(), Link.userid == userid).all()

    @staticmethod
    def get_public_untagged(userid=None):
        if userid is None:
            return appdb.session.query(Link).filter(~Link.tags.any(), Link.is_public).all()
        return appdb.session.query(Link) \
                .filter(~Link.tags.any(), Link.userid == userid, Link.is_public) \
                .all()

    @staticmethod
    def get_by_most_hits(owner=None, limit=10):
        query = appdb.session.query(Link, appdb.func.count(LinkHit.linkid)).join(LinkHit)
        if owner is not None:
            query = query.filter(Link.userid == owner)
        data = query.group_by(LinkHit.linkid) \
                .order_by(appdb.func.count(LinkHit.linkid).desc()) \
                .limit(limit)
        ret = []
        for row in data:
            row[0].hit_count = row[1]
            ret.append(row[0])
        return ret

    @staticmethod
    def get_by_most_recent_hit(owner=None, limit=10):
        query = appdb.session.query(Link, appdb.func.max(LinkHit.ts)).join(LinkHit)
        if owner is not None:
            query = query.filter(Link.userid == owner)
        data = query.group_by(LinkHit.linkid) \
                .order_by(appdb.func.max(LinkHit.ts).desc()) \
                .limit(limit)
        ret = []
        for row in data:
            row[0].last_hit = row[1]
            ret.append(row[0])
        return ret

    @staticmethod
    def get_by_most_recent(owner=None, limit=10):
        query = appdb.session.query(Link)
        if owner is not None:
            query = query.filter(Link.userid == owner)
        return query.order_by(Link.added.desc()).limit(limit).all()

    @staticmethod
    def get_public_by_most_recent(owner=None, limit=10):
        query = appdb.session.query(Link)
        if owner is not None:
            query = query.filter(Link.userid == owner, Link.is_public)
        else:
            query = query.filter(Link.is_public)
        return query.order_by(Link.added.desc()).limit(limit).all()

    @staticmethod
    def create_from_url(url):
        # TODO: Normalize the URL first # pylint: disable=fixme
        opener = urllib.FancyURLopener({})
        data = opener.open(url).read()
        return Link.create_from_webpage(url, data)

    @staticmethod
    def create_from_webpage(url, pagedata):
        soup = BeautifulSoup(pagedata)
        link = Link()
        link.url = url
        link.name = soup.head.title.string

        for meta in soup.head.find_all('meta'):
            name = meta.attrs.get('name')
            if name == 'description' and meta.attrs.get('content'):
                link.description = meta.attrs.get('content')

        return link

    @staticmethod
    def search_by_user(userid, query):
        pass


    @staticmethod
    def search_public_by_userid(userid, query):
        pass



class LinkHit(appdb.Model):
    __tablename__ = "links_hits"

    hitid = Column(Integer, primary_key=True)
    linkid = Column(Integer, ForeignKey('links.linkid'))
    userid = Column(Integer)
    ts = Column(DateTime) # pylint: disable=invalid-name

    def __init__(self, row=None):
        if row is not None:
            self.hitid = row['hitid'] if row.get('hitid') else None
            self.linkid = row['linkid'] if row.get('linkid') else 0
            self.userid = row['userid'] if row.get('userid') else None
            self.ts = row['ts'] if row.get('ts') else None # pylint: disable=invalid-name


    def add_hit(self):
        self.ts = datetime.now()
        appdb.session.add(self)
        appdb.session.commit()

    def get_count(self):
        if self.userid:
            return appdb.session.query(LinkHit) \
                    .filter_by(linkid=self.linkid, userid=self.userid) \
                    .count()
        return appdb.session.query(LinkHit).filter_by(linkid=self.linkid).count()

    def get_last_hit(self):
        if self.userid:
            return appdb.session.query(appdb.func.max(LinkHit.ts)) \
                    .select_from(LinkHit) \
                    .filter_by(linkid=self.linkid, userid=self.userid) \
                    .scalar()
        return appdb.session.query(appdb.func.max(LinkHit.ts)) \
                .select_from(LinkHit) \
                .filter_by(linkid=self.linkid) \
                .scalar()


class LinkCount(appdb.Model): # pylint: disable=too-few-public-methods
    __tablename__ = "links_counts"
    linkid = Column(Integer, primary_key=True)
    userid = Column(Integer, primary_key=True)
    hit_count = Column(Integer)
    last_hit = Column(DateTime)

    def __init__(self, row=None):
        if row is not None:
            self.linkid = row['linkid'] if row.get('linkid') else None
            self.userid = row['userid'] if row.get('userid') else None
            self.hit_count = row['hit_count'] if row.get('hit_count') else None
            self.last_hit = row['last_hit'] if row.get('last_hit') else None

    def add_hit(self):
        self.hit_count += 1
        self.last_hit = datetime.now()
        appdb.session.add(self)
        appdb.session.commit()
