==================
Handlebar Pystache
==================

I'm playing around with aggressively caching mustache templates.

It currently only handles variable access, but I will hopefully figure out
a way to make sections work correctly.

My benchmarks so far have led to good results, for this case:

:: 

    TEMPLATE = """
    The person's name is {{person}}.
    The person's company is {{company}}.
    The person's email is {{email}}.
    The person's address is {{address}}
    The person's hyperlink is {{hyperlink}}
    """

    CHANGESET = [
        {'person': 'Joe Smith', 'company': 'WebSmith', 'email': 'jsmith@websmith.ex', 'address': '535 Sap Tree St.', 'hyperlink': '<a href="http://joesmith.ex/">joesmith.ex</a>'},
        {'email': 'joes@websmith.ex'},
        {'address': '213 Maple Syrup Lane.'},
        {'company': 'University of Hard Knocks', 'email': 'jos@hard.knocks.edu'},
        {'email': 'jos@knocks.edu'},
        {'company': '7 Triples', 'email': 'jsmith@7triples.ex'},
        {'email': 'joes@7triples.ex'},
        {'address': '82 Cashew Cream Ave.'},
        {'company': 'Media Matic', 'email': 'jsmith@mediamatic.ex'},
        {'email': 'joes@mediamatic.ex'},
        {'company': 'Hacken Smack', 'email': 'joe@hackensmack.ex'},
    ]

    template = pystache.handlebar.Template(TEMPLATE)
    for thing in CHANGESET:
        template.update(**thing)
        template.render()


This is optimized with the following thinking in mind. Not everything always
changes, so only update the pieces that do before you render. If you stored
this in memory using an LRU cache, you could probably save a bunch calls to
memcache and the database, but I haven't shown that yet.

So, far the benchmark above runs quite a bit faster than pystache alone, so
I think I'm on to something, but don't necessarily know what that "something" 
is yet. It's also preliminarily faster than Jinja and Jinja2 doing the same
thing. 

More info here in the future....


========
Pystache
========

Inspired by ctemplate_ and et_, Mustache_ is a
framework-agnostic way to render logic-free views.

As ctemplates says, "It emphasizes separating logic from presentation:
it is impossible to embed application logic in this template language."

Pystache is a Python implementation of Mustache. It has been tested
with Python 2.6.1.


Documentation
=============

The different Mustache tags are documented at `mustache(5)`_.

Install It
==========

::

    easy_install pystache


Use It
======

::

    >>> import pystache
    >>> pystache.render('Hi {{person}}!', {'person': 'Mom'})
    'Hi Mom!'

You can also create dedicated view classes to hold your view logic.

Here's your simple.py::

    import pystache
    class Simple(pystache.View):
        def thing(self):
            return "pizza"

Then your template, simple.mustache::

    Hi {{thing}}!

Pull it together::

    >>> Simple().render()
    'Hi pizza!'


Test It
=======

nose_ works great! ::

    easy_install nose
    cd pystache
    nosetests


Author
======

::

    context = { 'author': 'Chris Wanstrath', 'email': 'chris@ozmm.org' }
    pystache.render("{{author}} :: {{email}}", context)


.. _ctemplate: http://code.google.com/p/google-ctemplate/
.. _et: http://www.ivan.fomichev.name/2008/05/erlang-template-engine-prototype.html
.. _Mustache: http://defunkt.github.com/mustache/
.. _mustache(5): http://defunkt.github.com/mustache/mustache.5.html
.. _nose: http://somethingaboutorange.com/mrl/projects/nose/0.11.1/testing.html
