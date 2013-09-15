import re

from lnto import appdb
from lnto.libs.links import Link
from lnto.libs.users import User
from lnto.libs.folders import Folder
from bs4 import BeautifulSoup

class LinkImporter(object):
    
    data = ''
    import_type = None
    soup = None
    user = None
    
    tag_folders = True  # Since folders don't really work yet, tag each entry with the folder name.
    
    def __init__(self, markup, import_type = None, user = None):
        self.data = markup
        self.import_type = import_type
        self.make_soup()
        self.user = user
        if self.user is None:
            self.user = User.get_logged_in()
    
    def fix_firefox_html(self):
        lines = self.data.split("\n")
        output = ''
        
        td_regex = re.compile('\s*<DT>')
        p_regex = re.compile('<P>')
        
        for l in lines:
            l = p_regex.sub('', l)
            if td_regex.match(l):
                l += '</DT>'
            output += l
        
        return output
    
    def make_soup(self):
        if self.import_type == 'htmlexport':
            fixed_markup = self.fix_firefox_html()
        else:
            fixed_markup = self.data
        self.soup = BeautifulSoup(fixed_markup)
    
    def convert(self):
        anchors = self.soup.find_all('a')
        links = {}
        duplicates = []
        errors = []
        folders = {}
        for a in anchors:
            data = {'userid': self.user.userid}
            data['url'] = a.attrs['href']
            # Handle nameless links - bookmarklets?
            if len(a.contents) == 0:
                data['name'] = data['url'][:250]
            else:
                data['name'] = unicode(a.contents[0])
            desc_node = self.get_description(a)
            if desc_node:
                data['description'] = unicode(desc_node.contents[0])
            try:
                link = Link(data)
                
                if links.get(link.url):
                    duplicates.append(link)
                else:
                    links[link.url] = link
                    appdb.session.add(link)
                    
                folder = self.get_folder(a)
                if folder:
                    f = folders.get(folder.contents[0])
                    if not f:
                        f = Folder()
                        f.userid = self.user.userid
                        f.name = folder.contents[0]
                        folders[folder.contents[0]] = f
                        appdb.session.add(f)
                    f.links.append(link)
                    
                    if self.tag_folders:
                        link.set_tags([folder.contents[0]])
                appdb.session.commit()
            except Exception:
                errors.append(link)
                appdb.session.rollback()
        return {'links': links, 'folders': folders, 'duplicates': duplicates, 'errors': errors}
        
    def get_description(self, item):
        next_sib = item.parent.next_sibling
        if next_sib and next_sib.string.strip() == '':
            next_sib = next_sib.next_sibling
        if next_sib and next_sib.name == 'dd':
            return next_sib
        return None
        
    def get_folder(self, item):
        par = item.parent.parent
        if par:
            par = par.previous_sibling
        if par and par.string.strip() == '':
            par = par.previous_sibling
        if par and par.name == 'dt':
            kids = list(par.children)
            if kids[0].name == 'h3':
                return kids[0]
        return None
    
    
    
