from lnto import appdb
from lnto.libs.links import Link
from lnto.libs.tags import Tag

from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import select
from sqlalchemy import ForeignKey, Column, Integer, String, DateTime, Boolean, Text, func

class AbstractModule(object):
    
    typeid = 0
    classes = ''
    caption = ''
    shortdesc = ''
    template_type = ''
    configuration = None
    has_config = False
    config_required = False
    userid = 0
    
    def __init__(self, userid):
        self.userid = userid
    
    def get_module_data(self):
        return []
    
    def get_caption(self):
        return self.caption
    
    def get_template(self):
        return 'modules/' + self.template_type + '.html'
    
    def get_config_template(self):
        return 'modules/' + self.template_type + '_config.html'
    
    def get_configuration(self, moduleid):
        return {}
    
    def save_configuration(self, moduleid, config):
        pass
    
    def render_module(self):
        return {
            'classes': self.classes,
            'caption': self.get_caption(),
            'template': self.get_template(),
            'data': self.get_module_data(),
        }


class AllLinksModule(AbstractModule):
    typeid = 1
    classes = 'all-links'
    shortdesc = 'All links'
    caption = 'All Links'
    template_type = 'all_links'
    
    def get_module_data(self):
        return Link.get_by_user(self.userid)


class PopularLinksModule(AbstractModule):
    typeid = 2
    classes = 'popular-links'
    shortdesc = 'Most visited links'
    caption = 'Most Visits'
    template_type = 'most_visits'
    
    def get_module_data(self):
        return Link.get_by_most_hits(self.userid)
    
    
class RecentlyVisitedLinksModule(AbstractModule):
    typeid = 3
    classes = 'last-links'
    shortdesc = 'Most recently visited links'
    caption = 'Recently Visited'
    template_type = 'recent_visits'
    
    def get_module_data(self):
        return Link.get_by_most_recent_hit(self.userid)
    
    
class AllTagsModule(AbstractModule):
    typeid = 4
    classes = 'tag-cloud'
    shortdesc = 'All tags'
    caption = 'Tag Cloud'
    template_type = 'tag_cloud'
    
    def get_module_data(self):
        return Tag.get_cloud_by_user(self.userid)
    
    
class RecentlyAddedLinksModule(AbstractModule):
    typeid = 5
    classes = 'recent-links'
    shortdesc = 'Recently added links'
    caption = 'Recently Added'
    template_type = 'recent_links'
    
    def get_module_data(self):
        return Link.get_by_most_recent(self.userid)
    

class TagModuleConfig(appdb.Model):
    __tablename__ = 'dashboard_modules_config_tag'
    moduleid = Column(Integer, ForeignKey('dashboard_modules.moduleid'), primary_key = True, autoincrement = False)
    tag_name = Column(String(64))


class TagModule(AbstractModule):
    typeid = 6
    classes = 'show-tag'
    shortdesc = 'Links from a tag'
    has_config = True
    config_required = True
    template_type = 'tag_links'
    
    def get_configuration(self, moduleid):
        self.configuration = appdb.session.query(TagModuleConfig).filter_by(moduleid = moduleid).first()
    
    def save_configuration(self, moduleid, config):
        if not config.get('tag_name'):
            raise Exception('No tag name found.');
        item = appdb.session.query(TagModuleConfig).filter_by(moduleid = moduleid).first()
        if not item:
            item = TagModuleConfig()
            item.moduleid = moduleid
        item.tag_name = config.get('tag_name')
        appdb.session.add(item)
        appdb.session.commit()
    
    def get_caption(self):
        return self.configuration.tag_name
    
    def get_module_data(self):
        return Link.get_by_tag(self.configuration.tag_name, self.userid)
    

module_type_map = {
    1: AllLinksModule,
    2: PopularLinksModule,
    3: RecentlyVisitedLinksModule,
    4: AllTagsModule,
    5: RecentlyAddedLinksModule,
    6: TagModule,
}


class Dashboard(object):
    
    userid = 0
    
    def __init__(self, userid):
        self.userid = userid
    
    def get_modules(self):
        modules = appdb.session.query(DashboardModule).filter_by(userid = self.userid).order_by(DashboardModule.position).all()
        # Let's add some defaults
        if len(modules) == 0:
            modules.append(DashboardModule(1, self.userid, 1, 1))
            modules.append(DashboardModule(2, self.userid, 2, 2))
            modules.append(DashboardModule(3, self.userid, 3, 3))
            modules.append(DashboardModule(4, self.userid, 4, 4))
            modules.append(DashboardModule(5, self.userid, 5, 5))
        for mod in modules:
            mod.get_module()
        return modules
    
    def render(self):
        modules = self.get_modules()
        ret = []
        for mod in modules:
            ret.append(mod.render())
        return ret
    
    def get_next_position(self):
        pos = appdb.session.query(func.max(DashboardModule.position)).filter_by(userid = self.userid).first()[0]
        return 0 if pos is None else pos
    
    def add_module(self, module_type, position, config_data = None):
        mod = DashboardModule(userid = self.userid, module_type = module_type, position = position)
        appdb.session.add(mod)
        appdb.session.commit()
        if config_data:
            mod.get_module()
            mod.module.save_configuration(mod.moduleid, config_data)
    
    def remove_module(self, moduleid):
        mod = appdb.session.query(DashboardModule).filter_by(moduleid = moduleid, userid = self.userid).first()
        if mod:
            appdb.session.delete(mod)
            appdb.session.commit()
            return True
        else:
            return False
    

class DashboardModule(appdb.Model):
    __tablename__ = 'dashboard_modules'
    
    moduleid = Column(Integer, primary_key = True)
    userid = Column(Integer, ForeignKey('users.userid'))
    module_type = Column(Integer, default = 1)
    position = Column(Integer, default = 0)
    
    module = None
    
    def __init__(self, moduleid = None, userid = 0, module_type = 1, position = 0):
        self.moduleid = moduleid
        self.userid = userid
        self.module_type = module_type
        self.position = position
    
    def get_module(self):
        self.module = module_type_map[self.module_type](self.userid)
        self.module.get_configuration(self.moduleid);
    
    def render(self):
        ret = self.module.render_module()
        ret['moduleid'] = self.moduleid
        return ret
    