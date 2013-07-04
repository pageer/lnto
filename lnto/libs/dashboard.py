from lnto import appdb
from lnto.libs.links import Link
from lnto.libs.tags import Tag

from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import select
from sqlalchemy import ForeignKey, Column, Integer, String, DateTime, Boolean, Text

class AbstractModule(object):
    
    typeid = 0
    classes = ''
    caption = ''
    template_type = 'link_list'
    userid = 0
    
    def __init__(self, userid):
        self.userid = userid
    
    def get_module_data(self):
        return []
    
    def get_caption(self):
        return self.caption
    
    
    def render_module(self):
        return {
            'classes': self.classes,
            'caption': self.get_caption(),
            'template': self.template_type,
            'data': self.get_module_data(),
        }


class AllLinksModule(AbstractModule):
    typeid = 1
    classes = 'all-links'
    caption = 'All Links'
    
    def get_module_data(self):
        return Link.get_by_userid(self.userid)


class PopularLinksModule(AbstractModule):
    typeid = 2
    classes = 'popular-links'
    caption = 'Most Visits'
    
    def get_module_data(self):
        return Link.get_by_most_hits(self.userid)
    
    
class RecentlyVisitedLinksModule(AbstractModule):
    typeid = 3
    classes = 'last-links'
    caption = 'Recently Visited'
    
    def get_module_data(self):
        return Link.get_by_most_recent_hit(self.userid)
    
    
class AllTagsModule(AbstractModule):
    typeid = 4
    classes = 'tag-cloud'
    caption = 'Tag Cloud'
    template_type = 'tag_list'
    
    def get_module_data(self):
        return Tag.get_cloud_by_user(self.userid)
    
    
class RecentlyAddedLinksModule(AbstractModule):
    typeid = 5
    classes = 'recent-links'
    caption = 'Recently Added'
    
    def get_module_data(self):
        return Link.get_by_most_recent(self.userid)
    

class FolderModule(AbstractModule):
    typeid = 6
    classes = 'link-folder'
    
    def get_module_data(self):
        pass
    


module_type_map = {
    1: AllLinksModule,
    2: PopularLinksModule,
    3: RecentlyVisitedLinksModule,
    4: AllTagsModule,
    5: RecentlyAddedLinksModule,
}


class Dashboard(object):
    
    userid = 0
    
    def __init__(self, userid):
        self.userid = userid
    
    def get_modules(self):
        modules = appdb.session.query(DashboardModule).filter_by(userid = self.userid).order_by(DashboardModule.position)
        



class DashboardModule(appdb.Model):
    __tablename__ = 'dashboard_modules'
    
    moduleid = Column(Integer, primary_key = True)
    userid = Column(Integer, ForeignKey('users.userid'))
    module_type = Column(Integer, default = 1)
    position = Column(Integer, default = 0)
    
    module = None
    
    def get_module(self, usr):
        self.module = module_type_map[self.module_type](usr)
    
    