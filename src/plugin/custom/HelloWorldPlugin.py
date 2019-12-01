'''
Example of adding a plugin to Sweep
'''

from plugin.Plugin import AbstractPlugin

class HelloWorldPlugin(AbstractPlugin):
    '''Trivial example of added Plugin'''
    def goDoit(self):
        '''
        return Hello, world!
        '''
        your_section_text = "Hello, world!"
        res = dict(
            title=self.title,
            post=your_section_text
        )
        return res