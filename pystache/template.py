import re
import cgi

modifiers = {}
def modifier(symbol):
    """Decorator for associating a function with a Mustache tag modifier.

    @modifier('P')
    def render_tongue(self, tag_name=None, context=None):
        return ":P %s" % tag_name

    {{P yo }} => :P yo
    """
    def set_modifier(func):
        modifiers[symbol] = func
        return func
    return set_modifier


class Template(object):
    # The regular expression used to find a tag.
    tag_re = None

    # Opening tag delimiter
    otag = '{{'

    # Closing tag delimiter
    ctag = '}}'

    def __init__(self, template, context=None):
        self.template = template
        self.context = context or {}

        self._closure_map = {}
        self._closures = []

        self.compile_regexps()
        self.compile(template)
        self.update(**self.context)

    def update(self, **context):
        for var, val in context.items():
            updater = self._closure_map.get(var, None)
            if updater:
                updater(**{var: val})

    def render(self, fileobj=None, encoding=None):
        if fileobj:
            for c in self._closures:
                tmp = c()
                if encoding:
                    tmp = tmp.encode(encoding)
                fileobj.write(tmp)
        else:
            tmp = ''.join([c() for c in self._closures])
            if encoding:
                tmp = tmp.encode(encoding)
            return tmp

    def compile_regexps(self):
        """Compiles our section and tag regular expressions."""
        tags = { 'otag': re.escape(self.otag), 'ctag': re.escape(self.ctag) }

        # section = r"%(otag)s[\#|^]([^\}]*)%(ctag)s\s*(.+?)\s*%(otag)s/\1%(ctag)s"
        # self.section_re = re.compile(section % tags, re.M|re.S)

        tag = r"%(otag)s(#|=|&|!|>|\{)?(.+?)\1?%(ctag)s+"
        self.tag_re = re.compile(tag % tags)

    # def render_sections(self, template, context):
    #     """Expands sections."""
    #     while 1:
    #         match = self.section_re.search(template)
    #         if match is None:
    #             break

    #         section, section_name, inner = match.group(0, 1, 2)
    #         section_name = section_name.strip()

    #         it = context.get(section_name, None)
    #         replacer = ''
    #         if it and hasattr(it, '__call__'):
    #             replacer = it(inner)
    #         elif it and not hasattr(it, '__iter__'):
    #             if section[2] != '^':
    #                 replacer = inner
    #         elif it:
    #             insides = []
    #             for item in it:
    #                 insides.append(self.render(inner, item))
    #             replacer = ''.join(insides)
    #         elif not it and section[2] == '^':
    #             replacer = inner
    #         print "replacing:", section, "\n\nwith: ", replacer
    #         template = template.replace(section, replacer)

    #     return template

    def compile(self, template):
        """Compiles all the tags and text into a list of closures
        """
        tmp_len = len(template)
        pos = 0

        for match in self.tag_re.finditer(template):
            start = match.start()
            end = match.end()
            # have we skipped any text? If so create a text closure
            if pos < start:
                func = modifiers['TEXT'](self, template[pos:start])
                self._closures.append(func)

            tag, tag_type, tag_name = match.group(0, 1, 2)
            tag_name = tag_name.strip()

            func = modifiers[tag_type](self, tag_name)
            if func:
                self._closures.append(func)
                self._closure_map[tag_name] = func
            pos = end

        else:
            if pos < tmp_len:
                self._closures.append(modifiers['TEXT'](template[pos:]))
 
    @modifier(None)
    def compile_tag(self, tag_name):
        """Given a tag name and context, finds, escapes, and renders the tag."""
        rendered_text = ['']
        def _inner(**context):
            if len(context):
                self.context.update(context)
                raw = context.get(tag_name, '')
                if not raw and raw is not None:
                    rendered_text[0] = ''
                else:
                    rendered_text[0] = cgi.escape(unicode(raw))
                return None
            else:
                return rendered_text[0]
        return _inner

    @modifier('!')
    def compile_comment(self, tag_name=None, context=None):
        """Rendering a comment always returns nothing."""
        return None

    @modifier('{')
    @modifier('&')
    def compile_unescaped(self, tag_name=None):
        """Render a tag without escaping it."""
        rendered_text = ['']
        def _inner(**context):
            if len(context):
                self.context.update(context)
                rendered_text[0] = unicode(context.get(tag_name, ''))
                return None
            else:
                return rendered_text[0]
        return _inner

    @modifier('TEXT')
    def compile_text(self, text=''):
        def _inner(**context):
            if len(context):
                return None
            return text
        return _inner

    # @modifier('>')
    # def render_partial(self, tag_name=None, context=None):
    #     """Renders a partial within the current context."""
    #     # Import view here to avoid import loop
    #     from pystache.view import View

    #     view = View(context=context)
    #     view.template_name = tag_name

    #     return view.render()

    # @modifier('=')
    # def render_delimiter(self, tag_name=None, context=None):
    #     """Changes the Mustache delimiter."""
    #     self.otag, self.ctag = tag_name.split(' ')
    #     self.compile_regexps()
    #     return ''
