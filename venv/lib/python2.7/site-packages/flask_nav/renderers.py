from flask import current_app

from dominate import tags
from visitor import Visitor


class Renderer(Visitor):
    """Base interface for navigation renderers.

    Visiting a node should return a string or an object that converts to a
    string containing HTML."""

    def visit_object(self, node):
        """Fallback rendering for objects.

        If the current application is in debug-mode
        (``flask.current_app.debug`` is ``True``), an ``<!-- HTML comment
        -->`` will be rendered, indicating which class is missing a visitation
        function.

        Outside of debug-mode, returns an empty string.
        """
        if current_app.debug:
            return tags.comment('no implementation in {} to render {}'.format(
                self.__class__.__name__,
                node.__class__.__name__, ))
        return ''


class SimpleRenderer(Renderer):
    """A very basic HTML5 renderer.

    Renders a navigational structure using ``<nav>`` and ``<ul>`` tags that
    can be styled using modern CSS.

    :param kwargs: Additional attributes to pass on to the root ``<nav>``-tag.
    """

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def visit_Link(self, node):
        return tags.a(node.text, href=node.get_url())

    def visit_Navbar(self, node):
        kwargs = {'_class': 'navbar'}
        kwargs.update(self.kwargs)

        cont = tags.nav(**kwargs)
        ul = cont.add(tags.ul())

        for item in node.items:
            ul.add(tags.li(self.visit(item)))

        return cont

    def visit_View(self, node):
        kwargs = {}
        if node.active:
            kwargs['_class'] = 'active'
        return tags.a(node.text,
                      href=node.get_url(),
                      title=node.text,
                      **kwargs)

    def visit_Subgroup(self, node):
        group = tags.ul(_class='subgroup')
        title = tags.span(node.title)

        if node.active:
            title.attributes['class'] = 'active'

        for item in node.items:
            group.add(tags.li(self.visit(item)))

        return tags.div(title, group)

    def visit_Separator(self, node):
        return tags.hr(_class='separator')

    def visit_Text(self, node):
        return tags.span(node.text, _class='nav-label')
